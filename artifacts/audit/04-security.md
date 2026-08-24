# Phase 4 — Security Review

## Authentication

### Login
- Uses Django's built-in `AuthenticationForm` via `CustomLoginView` (extends `LoginView`)
- Rate limited: `login_ip` = 5/m (IP-based), `login_user` = 20/h (username-based)
- Rate limit key uses `fleet.security.get_client_ip` (proxy-aware X-Forwarded-For)
- Rate limit denials logged to `AuditLog` via `RateLimitLogMiddleware`

**Evidence:** `views.py` L51-55, `settings/base.py` L131-140, `middleware.py` L66-101, `test_ratelimit.py`

**Status:** VERIFIED

### Password reset
- Uses Django's built-in `PasswordResetView` / `PasswordResetConfirmView` via Custom views
- Rate limited: `password_reset` = 3/h per IP
- Email backend configurable via `EMAIL_*` settings (SMTP by default)

**Status:** VERIFIED

### Logout
- Django built-in logout via `django.contrib.auth.urls`
- `log_audit(request, 'LOGOUT', ...)` records the event

**Status:** VERIFIED

## Authorization

### Staff requirement
- `@staff_required` decorator (`fleet/decorators.py` L1-27) checks `user.is_staff`
- Applied to all write views (create, edit, delete, status change, pickup, return)
- Read-only views use `@login_required` only (allows regular authenticated users to read)
- 17 tests in `test_authz.py` verify every write view requires staff

**Evidence:** `decorators.py`, `test_authz.py`, `views.py` (all `@staff_required` decorators)

**Status:** VERIFIED — PASS

### IDOR protection
- All object lookups use `tenant_get_object_or_404(request, Model, pk=pk)` which adds `company=request.company` to the filter
- Pattern used consistently across all 9 entity types
- No raw `Model.objects.get(pk=pk)` outside of `document_download` superuser branch (which is intentional)

**Evidence:** `views.py` L47-48, `test_idor.py` (35 tests), `test_documents.py` (signed URL company check)

**Status:** VERIFIED — PASS

## CSRF

- Django's built-in `CsrfViewMiddleware` (in MIDDLEWARE, `base.py` L32)
- All POST forms include `{% csrf_token %}` in templates
- `CSRF_TRUSTED_ORIGINS` configurable via `CSRF_TRUSTED_ORIGINS` env var
- `CSRF_COOKIE_SAMESITE = 'Lax'`, `CSRF_COOKIE_HTTPONLY = True` in production

**Status:** VERIFIED

## XSS

- All user input rendered via Django templates (auto-escaping enabled by default)
- No `|safe` filter used on user-generated content
- CSP (report-only): `script-src 'self' https://cdn.jsdelivr.net`
- CSP includes `frame-ancestors 'none'` preventing clickjacking

**Status:** VERIFIED

## SQL Injection

- No raw SQL queries found in views or models
- All database access via Django ORM with parameterized queries
- `select_for_update()` used for booking conflict prevention (not for SQL injection risk)
- No `extra()`, `extra_where()`, or `.raw()` calls in application code

**Status:** VERIFIED

## File Security

### Upload validation
- `validate_file_extension`: checks against `{.pdf, .png, .jpg, .jpeg}` whitelist
- `validate_file_size`: max 10 MB (`MAX_UPLOAD_SIZE = 10 * 1024 * 1024`)
- `validate_mime_type`: uses `python-magic` (`magic.from_buffer`) to verify MIME type matches whitelist
- Filenames sanitized via UUID-based storage path (`DocumentUploadTo` class) — original filename NOT used in storage path
- `original_filename` stored separately for display only

**Evidence:** `fleet/validators.py`, `fleet/tests/test_security.py` (ValidatorsTest + VehicleDocumentFileValidationTest), `fleet/tests/test_documents.py`

**Status:** VERIFIED — PASS

### Upload security tests
- 14 tests verify: valid extensions, invalid extensions (.exe, .js), size limits (under/over/exact), MIME validation (PDF/PNG/JPEG valid, text/HTML invalid), traversal filename rejection

**Status:** VERIFIED — PASS

### Download security
- Authenticated downloads require `@login_required` + `@staff_required`
- Cross-tenant document access blocked via `tenant_get_object_or_404` (404 for other company's docs)
- Signed URL downloads: token includes company ID, version, expiry; verified server-side
- `download_token_version` allows revocation (models.py L146-150)
- Content-Type derived from file extension whitelist, never from client
- `X-Content-Type-Options: nosniff` on download responses
- `Cache-Control: private, no-store` on download responses
- Rate limited: `download_per_user` = 20/h, `download_anon_ip` = 10/h

**Evidence:** `fleet/downloads.py`, `fleet/views.py` L427-456, `fleet/tests/test_documents.py` (37 tests)

**Status:** VERIFIED — PASS

### File replacement & deletion
- `VehicleDocument.save()` deletes old physical file on replacement
- `VehicleDocument.delete()` deletes physical file (best-effort, never aborts DB delete)
- `original_filename` updated on admin form when new file provided

**Evidence:** `fleet/models.py` L108-131, `fleet/tests/test_documents.py` (VehicleDocumentModelTests, DocumentOriginalFilenameTests)

**Status:** VERIFIED — PASS

## Rate Limiting

| Resource | Key | Rate | Evidence |
|---|---|---|---|
| Login POST | IP | 5/m | views.py L52, settings L132 |
| Login POST | username | 20/h | views.py L53, settings L133 |
| Password reset | IP | 3/h | views.py L59, settings L134 |
| Document upload | user_or_ip | 10/m | views.py L379, settings L135 |
| Document upload | user_or_ip | 50/h | views.py L379-380, settings L136 |
| Document download (auth) | user_or_ip | 20/h | downloads.py L74-77, settings L138 |
| Document download (anon) | IP | 10/h | downloads.py L74-77, settings L139 |
| 429 response includes Retry-After: 60 | — | — | middleware.py L82 |

**Status:** VERIFIED

## Security Headers

| Header | Value | Source |
|---|---|---|
| X-Content-Type-Options | nosniff | middleware.py L21 |
| X-Frame-Options | DENY | middleware.py L22 |
| Referrer-Policy | strict-origin-when-cross-origin | middleware.py L23 |
| Cross-Origin-Opener-Policy | same-origin | middleware.py L24 |
| Cross-Origin-Resource-Policy | same-origin | middleware.py L25 |
| Permissions-Policy | geolocation=(), microphone=(), camera=() | middleware.py L26 |
| Content-Security-Policy | Report-Only, dynamic | base.py L198-208 |

### CSP directives
- default-src 'self'
- script-src 'self' https://cdn.jsdelivr.net
- style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com
- img-src 'self' data:
- font-src 'self' https://fonts.gstatic.com
- connect-src 'self'
- frame-ancestors 'none'
- base-uri 'self'
- form-action 'self'

**Status:** VERIFIED

## Secrets / Configuration

- SECRET_KEY loaded from environment via `config('SECRET_KEY')`
- DEBUG = False enforced in production.py L26, startup validation L17-18
- ALLOWED_HOSTS required in production
- SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE = True in production
- SECURE_HSTS_SECONDS = 31536000 (1 year), HSTS include subdomains + preload

**Status:** VERIFIED

## CORS

**Status:** N/A — Same-origin web application, no cross-origin API endpoints.

## Health endpoint

`/health/` is a public endpoint (no authentication required).
- Returns 200 with `{'status': 'ok', 'checks': {'database': 'ok', 'cache': 'ok'}}` when healthy
- Returns 503 when database or cache is unreachable
- `Cache-Control: no-store` header set
- Exposes DB/cache reachability but no sensitive data

**Status:** VERIFIED — acceptable information disclosure

## Dependency vulnerabilities

- bandit (-ll): 0 findings (exit 0)
- pip-audit: 0 known vulnerabilities

**Evidence:** `engineering/evidence/security/rc1-bandit.json`, `rc1-pip-audit.json`

**Status:** VERIFIED — PASS

## SSRF / Path Traversal

- No URL fetching or external HTTP requests in application code
- Document file paths use UUID-based storage (no user-controlled paths)
- `serve_document` uses `storage.open(name)` — storage backend controls path resolution
- Upload path: `documents/{uuid}{ext}` — no path components from user

**Status:** VERIFIED

## Session security

- Session cookie: HTTPOnly, SameSite=Lax, Secure (production)
- 24-hour session expiry
- Session expires on browser close
- Session key stored in AuditLog for audit trail

**Status:** VERIFIED

## Summary

| Category | Status |
|---|---|
| Authentication | VERIFIED |
| Authorization (staff gate) | VERIFIED — PASS |
| IDOR / Tenant isolation | VERIFIED — PASS |
| CSRF | VERIFIED |
| XSS | VERIFIED |
| SQL Injection | VERIFIED |
| File uploads | VERIFIED — PASS |
| File downloads | VERIFIED — PASS |
| Rate limiting | VERIFIED |
| Security headers | VERIFIED |
| CSP | VERIFIED |
| Secrets | VERIFIED |
| DEBUG | VERIFIED |
| ALLOWED_HOSTS | VERIFIED |
| CORS | N/A |
| Health endpoint | VERIFIED |
| Error disclosure | VERIFIED |
| Dependency vulns | VERIFIED — PASS |
| SSRF / Path traversal | VERIFIED |
| Session security | VERIFIED |

**No P0 security issues found.**
