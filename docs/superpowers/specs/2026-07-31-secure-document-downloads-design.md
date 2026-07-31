# Secure Document Downloads — Design

- **Date:** 2026-07-31
- **Status:** Approved for implementation (pending final review)
- **Author:** Claude (with user review)
- **Scope:** v1.0.0-rc1
- **Goal:** Make `VehicleDocument` files private (not publicly served), serve them only through an authenticated, tenant-scoped, audited download endpoint, and add explicit, time-limited, revocable signed URLs for deliberate external sharing. Also fix file lifecycle (orphan cleanup) and preserve original filenames.

---

## 1. Problem statement

Today:

- Uploaded documents are stored at `MEDIA_ROOT/documents/<uuid>.<ext>` and linked directly via `doc.file.url` (`fleet/templates/fleet/vehicle_detail.html:85`).
- `config/urls.py:25-26` serves `/media/` publicly under `DEBUG`; `docs/deployment.md` tells nginx to serve `/media/` publicly in production. **Anyone with the URL can fetch any vehicle document** (registration cards, insurance, technical inspections, vignettes) with no authentication, no tenant check, and no audit trail.
- `document_delete` (`fleet/views.py:396`) deletes the DB record but leaves the physical file on disk forever — sensitive data lingers in `MEDIA_ROOT` and backups.
- The original client filename is discarded at upload (`DocumentUploadTo` renames to UUID), so even a private endpoint would serve `documents/<uuid>.pdf`.
- `AuditLog.ACTION_CHOICES` has no download action and `AuditLog` has no company column.

## 2. Goals

1. **Private media storage** — `/media/` is never served publicly, in dev or prod.
2. **Authenticated, staff-only, tenant-scoped download endpoint** — cross-tenant access returns 404, consistent with the rest of the app.
3. **Full download audit** — every attempt (success *and* denial) logged with serving method, outcome, denial reason, user/IP/UA/session, and company.
4. **Explicit, time-limited signed URLs** for deliberate external sharing — never the default download path. Revocable without rotating `SECRET_KEY`.
5. **File lifecycle hygiene** — deleting a record or replacing its file removes the physical file; failures are logged but never abort the DB transaction.
6. **Original filename preserved** and used for the download `Content-Disposition` name.
7. **Admin UX** — explicit `Download` (authenticated) and `Generate temporary download link` actions; plus link revocation.

## 3. Non-goals (explicitly deferred)

- **X-Accel-Redirect / nginx internal redirect** and **S3 presigned URLs** — future performance/scaling work; the controller stays storage-agnostic so these can slot in without touching authorization logic.
- **Request-ID middleware** — the stack has no request-ID mechanism; `log_audit` already records IP, UA, session key. Revisit when a request-id exists ("if available" in the requirements).
- **Automated orphan-file cleanup job** — documented as a maintenance task (Section 9), not built for RC1.
- **Customer/driver self-service download** — no such portal exists yet; the signed-URL feature is the future path for it.

## 4. Approach decision

**Approach A — Django-streamed private media** (chosen, user-approved 9.8/10).

- Files stay on the existing filesystem storage at `MEDIA_ROOT/documents/...`; only the *access path* changes.
- A view authenticates, authorizes, and streams via `FileResponse` with safe headers.
- Portable across `runserver`, gunicorn, any server; no nginx coupling; trivial to test.
- Cost: bytes flow through Django — irrelevant at ≤10 MB per file (validated at upload).

Rejected alternatives: **B) X-Accel-Redirect** (nginx coupling, breaks dev, overkill at this size); **C) S3 presigned URLs** (external infra dependency not present in the self-hosted stack).

## 5. Design

### 5.1 Model changes — `fleet/models.py`, migration `0009`

`VehicleDocument` additions:

```python
original_filename = models.CharField(max_length=255, blank=True, verbose_name=_("Original filename"))
download_token_version = models.PositiveIntegerField(default=1, verbose_name=_("Download token version"))
```

- `original_filename` is captured from the upload in the create/edit views (Section 5.6). It is not set from the UUID-stored name.
- `download_token_version` is the **revocation counter**: every signed token embeds the current version; bumping it invalidates all outstanding tokens without touching `SECRET_KEY`.

`AuditLog` additions:

```python
company = models.ForeignKey("Company", null=True, on_delete=models.SET_NULL, related_name="audit_logs", verbose_name=_("Company"))
ACTION_CHOICES += [("DOWNLOAD", _("Download"))]
```

- Migration `0009` includes a **data migration** that backfills `company` on existing rows where the referenced object (`content_type` + `object_id`) still resolves to a tenant-scoped model (e.g. `fleet.Vehicle`, `fleet.VehicleDocument`) and its company can be recovered. Rows with no resolvable object (login/logout/system events, deleted objects) stay `NULL`.
- The column deliberately **remains nullable** (`SET_NULL`): audit history must survive a `Company` deletion without cascade-deleting or blocking it. Forcing non-null would require a sentinel company and would corrupt the audit record when a tenant is removed. This is an intentional deviation from "make non-null" — nullable + `SET_NULL` is the correct audit-retention semantics.

`VehicleDocument` lifecycle methods:

- `save()` — before `super().save()`, read the existing DB row (`VehicleDocument.objects.filter(pk=self.pk).first()`); after save, if the previous row had a file whose name differs from the new `self.file.name`, delete the old physical file best-effort (`try/except` + `logger.warning`, never raising).
- `delete()` — capture `self.file.name` before `super().delete()`; afterwards delete the physical file best-effort. DB transaction is never aborted by a filesystem failure.
- `get_signed_download_url(ttl=None)` — builds `reverse("fleet:document_download_signed", kwargs={"pk": self.pk})` + `?token=<signing.dumps(payload)>`, returns the relative URL. Callers needing an absolute URL use `request.build_absolute_uri(...)`.
- `revoke_download_links()` — `self.download_token_version += 1; self.save(update_fields=["download_token_version"])`.

**Token payload** (all fields signed; tamper-proof). `v` is a **payload schema version** so future token evolution (new claims, deprecations) never silently breaks older tokens:

```json
{
  "v": 1,                 // payload schema version, always validated == 1
  "doc": 123,             // VehicleDocument pk
  "company": 7,           // document's company_id
  "purpose": "vehicle_document_download",
  "version": 1,           // download_token_version at issuance
  "exp": 1785561600       // int(time.time()) + ttl, per-token expiry
}
```

Per-token TTL is baked into `exp`, so a 15-minute token is *not* accepted for the full default TTL. `signing.loads` is called with a generous safety `max_age` (30 days) only to bound payload retention; the authoritative expiry check is `exp`.

### 5.2 Audit — `fleet/audit.py`

- Extend `log_audit(request, action, obj=None, summary="", company=None)`; when `company` is omitted, fall back to `getattr(request, "company", None)` or `obj.company` (tenant-scoped objects). This enriches **every** existing audit row with a company column going forward.
- Add a `_log_download(request, doc, *, method, outcome, reason="")` helper that writes a `DOWNLOAD` row. The `change_summary` encodes the structured metadata the requirements ask for:

```
Download via session (ok)
Download via signed link (denied: token expired)
Download denied: object not found (pk=123)
```

Recorded across the two fields available: `object_id`/`content_type` (pk and `fleet.VehicleDocument`) and `change_summary` (method, outcome, reason). Company is now a real column. IP/UA/session/user already come from `log_audit`.
- Failures where the document is not resolvable (tampered/expired/wrong-pk token) still write an audit row using the URL pk and empty company — this is the incident-response value.
- **Denials are audited, not just successes.** The full denied set: expired token, tampered/invalid signature, wrong payload schema, wrong doc pk, company mismatch, revoked version, missing file, unauthorized (non-staff) user, cross-tenant attempt, and rate-limited request. Every one produces a `DOWNLOAD` row with `outcome=denied` and a specific reason. Denied events are typically *more* security-relevant than successes, so none fall through silently.

### 5.3 Download views — `fleet/views.py`

Two thin views sharing `_serve_document()`. Unlike the upload views (`fleet/views.py:357`), the download rate limit and staff check run **inside the view** (with `block=False` / manual check) rather than as pre-view decorators — so rate-limited and unauthorized attempts can be *audited* before the 403 is returned. Response codes stay identical (403).

`document_download` — session path:

```python
@login_required
def document_download(request, pk):
    if not request.user.is_staff:
        log_audit(request, "DOWNLOAD", None, _("Download denied: unauthorized user"))
        return forbidden(request)  # 403, renders fleet/forbidden.html
    ...
```

- Rate limit applied as `@ratelimit(key="user_or_ip", rate=settings.SECURITY_RATE_LIMITS["download_per_user"], method="GET", block=False)`; when `request.limited` is set, audit `denied: rate limited` and return 403.
- Object resolution mirrors `TenantAdminMixin` (`fleet/admin.py:17`): **superuser → all companies**; otherwise tenant-scoped via `request.company` → `get_object_or_404`. Cross-tenant = 404, audited as `denied: cross-tenant`.
- Audits success; on missing object or missing file audits denial.

`document_download_signed` — token path:

```python
@ratelimit(key="ip", rate=settings.SECURITY_RATE_LIMITS["download_anon_ip"], method="GET", block=False)
def document_download_signed(request, pk): ...
```

- No login required — a valid, unexpired, version-matching token *is* the authorization (same model as a password-reset link). This is the deliberate external-sharing path.
- When `request.limited`, audit `denied: rate limited` and return 403 (protects leaked links from brute-force scraping).
- Validation order (each failure → 403 + audit with a specific denial reason):
  1. `token` query param present (else `missing token`).
  2. `signing.loads` succeeds (else `BadSignature` → `tampered`; `SignatureExpired` → `expired`).
  3. `payload["v"] == 1` (else `schema mismatch`).
  4. `payload["purpose"] == "vehicle_document_download"` (else `wrong purpose`).
  5. `payload["doc"] == <url pk>` (else `wrong document`).
  6. `payload["exp"] > time.time()` (else `expired`).
  7. Document exists; `payload["company"] == doc.company_id` (else `company mismatch`); `payload["version"] == doc.download_token_version` (else `revoked`).
- Anonymous requests get the IP rate limit (`download_anon_ip`) to blunt leaked-link abuse.

`_serve_document(request, doc, *, via_signed)`:

- Verify `doc.file.storage.exists(doc.file.name)` — else 404 + audit `denied: file missing`. Because the check→open is racy, the `open("rb")` is also wrapped in `try/except OSError` → 404 + audit `denied: file missing`; filesystem drift must never surface a 500.
- **Streaming:** `doc.file.open("rb")` returns the FieldFile (which proxies the configured storage backend — never a raw local path assumption) and is handed to `FileResponse`, which streams from storage in chunks. The file is **never read fully into memory**; this keeps the controller storage-agnostic (S3/X-Accel later without touching authorization).
- Response headers:
  - `Content-Disposition: attachment` — never inline (avoids browser rendering of hostile content). Filename = `original_filename` (fallback: stored name), **control characters (CR/LF) stripped** to prevent header injection; non-ASCII handled via RFC 5987 `filename*=UTF-8''<pct-encoded>` with an ASCII fallback in `filename=`.
  - `X-Content-Type-Options: nosniff`.
  - `Cache-Control: private, no-store` + `Pragma: no-cache` + `Expires: 0` — sensitive documents must not be cached by browsers or proxies.
- `Content-Type` derived from a whitelisted extension→MIME map (`application/pdf`, `image/jpeg`, `image/png`) — never from a client-supplied header.
- Audit success (user populated when the request is authenticated, else `None`).

### 5.4 URL routes — `fleet/urls.py`, `config/urls.py`

`fleet/urls.py`:

```python
path("documents/<int:pk>/download/", views.document_download, name="document_download"),
path("documents/<int:pk>/download/signed/", views.document_download_signed, name="document_download_signed"),
```

`config/urls.py`: **remove** the `if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` block and the now-unused `static` import. Private media means no public serving in any environment.

### 5.5 Settings — `config/settings/base.py`, env files

```python
DOCUMENT_SIGNED_URL_TTL = config("DOCUMENT_SIGNED_URL_TTL", default=86400, cast=int)  # seconds

SECURITY_RATE_LIMITS = {
    # ... existing ...
    "download_per_user": "30/m",
    "download_anon_ip": "10/m",
}
```

`DOCUMENT_SIGNED_URL_TTL` is the *default* TTL for generated links (admin offers 15 m / 1 h / 24 h); each token carries its own `exp` regardless.

Add `DOCUMENT_SIGNED_URL_TTL` to `.env.example` and `.env.production.example`.

### 5.6 Templates & upload capture

- `fleet/templates/fleet/vehicle_detail.html:85`: `{{ doc.file.url }}` → `{% url 'fleet:document_download' doc.pk %}`. Label stays "Download".
- `document_create` (`fleet/views.py:360`): set `doc.original_filename = request.FILES["file"].name` before save.
- `document_edit` (`fleet/views.py:380`): when `"file" in request.FILES`, update `original_filename`; otherwise keep the existing value.

### 5.7 Admin — `fleet/admin.py`

`VehicleDocumentAdmin`:

- `list_display` gains a **Download** link → `fleet:document_download` (authenticated; opens new tab). This is the everyday path and requires no token.
- A per-object **Generate temporary download link** action, surfaced as a button in `list_display`, routed to a custom admin view (`admin:fleet_vehicledocument_generate_link`) registered on the admin site:
  - GET renders a page with a TTL chooser (15 minutes / 1 hour / 24 hours, default from `DOCUMENT_SIGNED_URL_TTL`).
  - Shows the generated absolute signed URL (`build_absolute_uri(get_signed_download_url(...))`), its expiry timestamp, and a copy button.
  - A **Revoke temporary links** button calls `revoke_download_links()` and confirms that all outstanding links are dead.
- **Form widget fix:** the default admin `ClearableFileInput` renders a "Currently: <a href>`{{ file.url }}`" link, which 404s once `/media/` is private. A small `AdminFileWidget` subclass replaces that link with the authenticated `fleet:document_download` URL (opens in new tab) plus a note that uploads replace the current file.
- Shared links are therefore an *intentional, audited, reversible* operation — never a side effect of normal browsing.

`AuditLogAdmin.list_display` gains `company`.

### 5.8 Deployment & ops — `docs/deployment.md`

- Remove the public `/media/` location block from the nginx config example. `/media/` is no longer web-served at all; documents are delivered only by the app through the download views.
- `/static/` remains public as today.
- `backup.sh` / `restore.sh` unchanged — `MEDIA_ROOT` is still fully backed up.
- **Maintenance task (documented, not built):** periodic orphan sweep — find files under `MEDIA_ROOT/documents/` with no matching `VehicleDocument` row and archive/delete them.

## 6. Files changed

| File | Change |
|---|---|
| `fleet/models.py` | `original_filename`, `download_token_version`, `AuditLog.company`, `DOWNLOAD` action, `save()`/`delete()` cleanup, `get_signed_download_url()`, `revoke_download_links()` |
| `fleet/migrations/0009_*.py` | Schema migration (both models) **+ data migration** backfilling `AuditLog.company` |
| `fleet/audit.py` | `company` param + fallback; `_log_download` helper |
| `fleet/views.py` | `document_download`, `document_download_signed`, `_serve_document`; in-view staff/rate-limit checks with audit; capture `original_filename` in create/edit |
| `fleet/urls.py` | Two new routes |
| `config/urls.py` | Remove DEBUG media serving + unused import |
| `config/settings/base.py` | `DOCUMENT_SIGNED_URL_TTL`, two rate limits |
| `.env.example`, `.env.production.example` | `DOCUMENT_SIGNED_URL_TTL` |
| `fleet/templates/fleet/vehicle_detail.html` | Link swap |
| `fleet/admin.py` | Download link, generate-link view + revoke, `AdminFileWidget` fix, audit company column |
| `docs/deployment.md` | nginx media removal, signed-URL note, maintenance task |
| `fleet/tests/test_documents.py` | New test module |

## 7. Testing plan — `fleet/tests/test_documents.py`

Run with `--settings=config.settings.test` (SQLite `:memory:`), per project convention.

**Session path (`document_download`)**
1. Anonymous → redirect to login.
2. Authenticated non-staff → 403 **+ audit `denied: unauthorized user`**.
3. Staff, cross-tenant doc → 404 + audit `denied: cross-tenant`.
4. Superuser → 200 for a doc of a company other than the profile company.
5. Staff of owning company → 200; response bytes equal file bytes; `Content-Type` from extension map; `Content-Disposition: attachment` with `original_filename`; `nosniff`; `Cache-Control: private, no-store`.
6. Download writes a `DOWNLOAD` audit row (user, company, method `session`, outcome `ok`).
7. File deleted from disk behind the DB row → 404 + audit `denied: file missing`.
8. Rate limit exceeded → 403 + audit `denied: rate limited`.

**Signed path (`document_download_signed`)**
9. No token → 403 + audit `missing token`.
10. Valid token, anonymous → 200 + audit with `user=None`.
11. Expired token (`exp` in the past) → 403 + audit `denied: token expired`.
12. Tampered token (invalid signature) → 403 + audit `denied: token tampered`.
13. Token for a different doc pk → 403 + audit `denied: wrong document`.
14. Token whose `company` ≠ doc's company → 403 + audit `denied: company mismatch`.
15. After `revoke_download_links()`, an outstanding token → 403 `denied: token revoked`; a freshly generated token → 200.
16. A 15-minute token is rejected after its own `exp` even though the default TTL is longer.
17. Anonymous IP rate limit exceeded → 403 + audit `denied: rate limited`.

**Lifecycle**
18. Deleting a doc removes the physical file; DB row gone.
19. Edit-replacing the file removes the old physical file, keeps the new one; `original_filename` updates on upload, is preserved when no new file is uploaded.

**Unit & headers**
20. `get_signed_download_url()` round-trips through `signing.loads` with the correct payload (`v`, `doc`, `company`, `purpose`, `version`, `exp`).
21. `revoke_download_links()` bumps the version.
22. Non-ASCII `original_filename` → response carries RFC 5987 `filename*=UTF-8''...` (and ASCII fallback); CR/LF in a crafted filename is stripped, not echoed.
23. Backfill migration: a pre-existing CREATE audit row for a still-existing tenant object gains the correct `company`; an unresolvable row stays `NULL`.

## 8. Security considerations

- **Signed URLs are bearer tokens.** Anyone holding a valid, unexpired link can fetch the document without a login — this is the intended sharing semantics. Mitigations: deliberate generation (admin only), short default TTL (24 h) with 15 m/1 h options, per-IP anonymous rate limit, revocation counter, full audit, and `no-store` caching.
- **Forwarded-mail risk** (compromised mailbox) is documented in `docs/deployment.md`; shorter TTLs and revocation are the controls.
- Cross-tenant isolation: session path 404s on tenant mismatch; signed path enforces `company == doc.company` inside the signed payload.
- Superuser session path is intentionally tenant-unrestricted, consistent with `TenantAdminMixin`.
- No caching of sensitive responses; attachment disposition; sanitized filenames; whitelisted MIME map; `nosniff`.
- Token payload carries a schema version (`v`), binding generation and validation to one unambiguous contract and leaving a clean upgrade path for future claims.
- Denials are as heavily audited as successes — failed attempts are the earliest signal of a leaked or brute-forced link.

## 9. Rollout

Part of the pre-RC1 work: apply migration `0009` (schema + backfill), deploy, verify nginx no longer exposes `/media/`, run the full suite (`220 existing + ~23 new`), rerun `ruff check .`, `check --deploy`, bandit, pip-audit. Document orphan-sweep as a maintenance task.

## 10. Open questions

None blocking. Deliberate choices recorded for posterity:

- Signed endpoint allows unauthenticated access by design (sharing). If this ever feels too permissive, the fix is to require auth *or* a token — both paths already exist.
- `AuditLog.company` enriches all audit rows, not just downloads; this is a strict improvement for a multi-tenant app but touches the audit model generally.
- `AuditLog.company` stays nullable (`SET_NULL`) despite the backfill — audit history must survive tenant deletion (deviates from "make non-null"; rationale in §5.1).
- Download views do their own staff/rate-limit checks (instead of `@staff_required`/`block=True`) so that unauthorized and rate-limited attempts are auditable; response codes are unchanged.
