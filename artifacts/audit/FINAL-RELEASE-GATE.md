# Final Release Gate — Vroom RC1

## Audit scope

This audit was conducted against the Vroom repository at `release/1.0` branch (HEAD `cb2c0f3`), using evidence-based verification per the 27-rule audit framework.

## Gates

| Gate | Status | Evidence |
|---|---|---|
| Architecture | PASS | 1 app, 9 entity models, 11 migrations, all verified via source code |
| Database Integrity | PASS | 11 migrations applied cleanly, tenant-scoped unique constraints verified |
| Tenant Isolation | PASS | 35 IDOR tests pass, CompanyMiddleware + tenant_objects() enforce scoping |
| Authentication | PASS | Login rate-limited (5/m IP, 20/h user), audit-logged, proxy-aware IP resolution |
| Authorization | PASS | `@staff_required` on all write views (17 tests pass), `@login_required` on reads |
| Security | PASS | bandit -ll clean, pip-audit clean, 37 file-security tests pass |
| Booking Concurrency | PASS | `select_for_update()` + `transaction.atomic()` (2 tests pass), k6 sameVehicleBooking confirms 1/49 |
| Financial Logic | PARTIAL | Booking `total_amount` is a client-submitted field, NOT server-computed (see F3) |
| Celery Isolation | N/A | No Celery in stack (documented in `docs/deployment.md` §13) |
| Redis Isolation | N/A | No Redis in stack; LocMemCache used when CACHE_URL is empty |
| File Security | PASS | Upload validators (ext/size/MIME), signed URL downloads, 37 tests pass |
| API Security | N/A | No REST API — web UI only |
| Automated Tests | PASS | 278 tests, 278 PASS, 0 FAIL (re-run 2026-08-22 after F1 fix: 355.7s, exit 0) |
| Playwright | SKIPPED | Playwright MCP unavailable (see tool inventory); k6 load tests used instead |
| Accessibility | NOT ASSESSED | Not in scope for this evidence-gathering phase |
| UI/UX | NOT ASSESSED | Apple Design skill unavailable (CSS design system applied to base.html instead) |
| Backups | DOCUMENTED | `scripts/backup.sh`: daily pg_dump + media, 14-day retention; RPO ≤24h (target ≤15min needs WAL archiving) |
| Restore | TESTED | `scripts/restore.sh` tested in deployment automation review |
| Deployment | PASS | Hostinger shared hosting (Passenger + MySQL), gunicorn+nginx alternative, CI/CD validated |
| Observability | PARTIAL | Logging to file+console (verbose formatter), health endpoint with DB+cache probes; no Sentry/DataDog integration |
| Documentation | PASS | 187 MD files, 0 broken internal links, claims reconciled |

## Key discrepancies & findings

### FINDING F1 — FLAKY TEST: `test_audit_log_default_ordering` → RESOLVED
- **Severity:** LOW
- **Status:** FIXED (2026-08-22)
- **Issue:** `AuditLog.created_at` uses `auto_now_add=True` (second granularity). Two entries created in the same second produce non-deterministic ordering with `-created_at` Meta ordering.
- **Root cause:** `Meta.ordering = ['-created_at']` has no tiebreaker for equal timestamps.
- **Fix applied:** `fleet/models.py` L347 → `ordering = ['-created_at', '-id']`. Adding `-id` as a deterministic tiebreaker (auto-increment PK is monotonic) makes "newest first" reproducible without a schema/migration change, and also makes real admin listing ordering deterministic.
- **Re-verification:** `manage.py test fleet.tests.test_security.AuditLogModelTest.test_audit_log_default_ordering` → OK. **Full-suite re-run (2026-08-22): 278 tests, 278 PASS, 0 FAIL (355.7s, exit 0). No regression.**
- **Evidence:** `models.py` L346-347, test `test_security.py` L178-183.

### FINDING F2 — Python 3.14 + python-magic segfault → CLOSED / HISTORICAL
- **Severity:** LOW (CI is Linux)
- **Status:** CLOSED — environment event, not a code defect.
- **Issue:** On Python 3.14 (CPython 3.14.7, Windows), `python-magic` v0.4.27 segfaults on `import magic` (native `libmagic` load). Any test path hitting `validate_mime_type` crashed with exit 139 (SIGSEGV).
- **Resolution:** Verified environment is **Python 3.12 + `python-magic-bin`** (which provides `libmagic-1.dll`). Under that environment the full suite runs clean (278/278). The historical Python 3.14 run (`proc_52e9fb7c58fb`) is accounted for and closed.
- **Evidence:** Exit code 139 on 3.14; `magic.from_buffer` works on 3.12 + python-magic-bin.

### FINDING F3 — Booking.total_amount client-controlled → RESOLVED
- **Severity:** MEDIUM (financial integrity)
- **Status:** RESOLVED (2026-08-22). All verification gates passed.
- **Approved rule (2026-08-22, product/domain decision, Option 2):**
  `rental_days = ceil(elapsed_time / 24h)` (>= 1), `total_amount = vehicle.daily_rate × rental_days`. Documented in `engineering/domain/pricing/business-rules.md` ("Approved rental-day & pricing rule").
- **Code change applied:**
  - `fleet/pricing.py` (NEW): `rental_days(pickup, expected_return)` + `calculate_booking_total(vehicle, pickup, expected_return)`. Elapsed-duration based, tz-aware, `ceil`, floor 1, no discounts/extras/taxes/currency/deposit-override.
  - `fleet/forms.py` `BookingForm`: `total_amount` field set `required=False`; `save()` overridden to compute `total_amount` via `calculate_booking_total(...)` and **ignore** the client value; `deposit` untouched.
  - Both `booking_create` and `booking_edit` go through this form, so create and edit recompute server-side.
- **F3 protection boundary (explicit):** the calc lives in `BookingForm.save()`, so the HTTP form create/edit paths are protected. Other write paths verified:
  - `BookingAdmin` (admin.py L151) — default `ModelAdmin`, **no `save_model` override** → admin editing dates/vehicle does NOT recompute `total_amount` (data-consistency gap, not a client-trust vuln). Recorded as **F8**.
  - No management command / script creates Bookings (only `loadtest_seed`, `send_alerts` touch Vehicles/Documents/Drivers).
  - No factories/services; tests use `Booking.objects.create(...)` with explicit `total_amount` (trusted fixtures, not external paths).
- **Verification (Rule 0.2 complete):**
  - Targeted pricing tests: **25/25 PASS** (`fleet/tests/test_pricing.py`).
  - Full suite: **303 tests, 0 failures, 0 errors, exit 0** (278 baseline + 25 new; 394.4s).
  - Security re-check: **bandit exit 0** (no issues in `fleet`/`config`, incl. new `pricing.py` + `BookingForm.save()`). **pip-audit** surfaced a Django dependency CVE (see **F9**), independent of the F3 code change.
  - `ruff check fleet/` passes clean (FURB157 in new file fixed).
  - No existing behavior regressed; `deposit` and DB field preserved.
- **Deposit exposure (F7):** `deposit` unchanged per instruction. Opened-as-F7 observation stands; F3 does not alter it.
- **Determination (from evidence):** Before the fix, `total_amount` was accepted verbatim from the POST (views.py L195-227, L242-265; forms.py L25-33). Now the only authoritative input is `Vehicle.daily_rate`; the client value is discarded. This closes the client-trust vulnerability for the form path. F8 tracks the admin-path consistency gap.

### FINDING F4 — python-magic-bin missing from Windows dev requirements → OPEN / LOW
- **Severity:** LOW
- **Status:** OPEN — documentation/dependency gap for Windows developers.
- **Issue:** `requirements-dev.txt` does not list `python-magic-bin`. Windows devs installing only the declared deps hit the F2 segfault until they discover the need for `python-magic-bin` (which bundles `libmagic-1.dll`).
- **Fix (proposed):** Add `python-magic-bin` to `requirements-dev.txt` (Windows-specific) or document the prerequisite in `docs/deployment.md` / setup notes.
- **Evidence:** `requirements-dev.txt` (no python-magic-bin); F2 resolution required it on Windows.

### FINDING F5 — Booking overlap check excludes 'late'/'returned' status → LOW (observation)
- **Severity:** LOW
- **Status:** VERIFIED behavior, potential gap to confirm.
- **Issue:** Overlap check in `booking_create`/`booking_edit` (`views.py` L215-220, L256-261) filters `status__in=['confirmed', 'rented']`. A booking in 'late' or 'returned' status does not block new bookings for the same vehicle+period.
- **Assessment:** Correct for 'returned' (past). For 'late' (still out, overdue), blocking may be desirable, but it is a business decision, not a bug. Flag for product confirmation.
- **Evidence:** `views.py` L215-220, L256-261.

### FINDING F6 — Database config inconsistency → LOW
- **Severity:** LOW
- **Status:** PARTIALLY VERIFIED.
- **Issue:** `.env.example` shows PostgreSQL (`DB_NAME=vroomo`); CI grants MySQL privileges (`ci/mysql: grant test_%`); `ec246a0` commit says "migrate to MySQL"; deployment docs reference PostgreSQL (VPS) and MySQL (Hostinger). Test settings use SQLite (expected).
- **Evidence:** `.env.example`, `config/settings/test.py`, `engineering/evidence/verification/deployment-automation-2026-08-06.json`.

### FINDING F7 — `deposit` client-editable by staff author (parity observation) → OPEN / LOW
- **Severity:** LOW
- **Status:** OPEN — observation, same trust level as F3's `total_amount`. Not an untrusted-actor exposure.
- **Issue:** `deposit` is in `BookingForm.Meta.fields` (forms.py L28) and rendered via `{% bootstrap_form %}` in `form.html`, so a `@staff_required` user can submit any deposit value. No lower-privilege actor can reach it (same gate as `total_amount`). Per F3 instruction, this is NOT a distinct untrusted-actor exposure, so it is recorded separately rather than folded into F3.
- **Instruction:** Do NOT change `deposit` meaning/calculation yet. Stays open until a deposit policy exists (pricing business-rules note "Deposit > total_amount → policy question").
- **Evidence:** forms.py L28, form.html L14, booking_detail.html L86 (display).

### FINDING F9 — Django 6.0.7 had a known CVE (pip-audit) → RESOLVED
- **Severity:** MEDIUM (dependency vulnerability)
- **Status:** RESOLVED (2026-08-22). `Django==6.0.7` → `Django==6.0.8` in `requirements.txt`.
- **Issue:** `pip-audit` reported `django 6.0.7` → `PYSEC-2026-3717`, fix versions `5.2.17, 6.0.8`.
- **Fix applied:** bumped `Django==6.0.7` → `Django==6.0.8` in `requirements.txt` (requirements-dev.txt inherits via `-r`). Reinstalled in the verified Python 3.12 + python-magic-bin env.
- **Verification:** `pip-audit` → **No known vulnerabilities found (exit 0)**; `ruff check fleet/` → clean; `bandit -r fleet config` → exit 0; **full suite 303/303 PASS, exit 0** (388.6s). No regression.
- **Evidence:** `requirements.txt` L1 `Django==6.0.8`; pip-audit output `No known vulnerabilities found`; `vroom-f9-full.txt` Ran 303 tests OK.

## P0 OPEN
None.

## P1 OPEN
None.

## P2 OPEN
1. **F3** — Server-side `total_amount` computation for Booking (MEDIUM, financial integrity). **RESOLVED** — full verification passed: 303/303 tests, bandit clean, ruff clean. See `F3-AMBIGUITY.md` for prior-blocker history.
2. **F4** — Add `python-magic-bin` to Windows dev requirements / docs (LOW).
3. **F7** — `deposit` client-editable by staff (LOW, parity observation; no change until deposit policy exists).
4. **F8** — Admin `BookingAdmin` edit path did not recompute `total_amount` (data-consistency gap). **RESOLVED** — `BookingAdmin.save_model` now recomputes via `calculate_booking_total`; 4/4 admin tests pass, 307/307 suite green.
5. **F9** — Django CVE `PYSEC-2026-3717` (MEDIUM). **RESOLVED** — bumped `Django==6.0.8`; pip-audit clean, 303/303 suite green.

## FINAL RELEASE STATUS

**CONDITIONAL** — All P0 security boundaries PASS. F3 (financial integrity), F8 (admin pricing recompute), and F9 (Django CVE) RESOLVED with full evidence. Remaining items are LOW observations (F4/F7); none block a non-financial-grade release.

- **F1 (flaky test):** RESOLVED — `ordering = ['-created_at', '-id']`; full suite 278/278 PASS (exit 0).
- **F2 (Python 3.14 segfault):** CLOSED / HISTORICAL — verified env is Python 3.12 + python-magic-bin.
- **F3 (financial integrity):** RESOLVED — code applied (`fleet/pricing.py`, `BookingForm.save()`); targeted 25/25 green; full **303/303 PASS, exit 0**; bandit clean; ruff clean. Protection boundary: HTTP form create/edit. Admin path closed by F8 (`BookingAdmin.save_model`).
- **F4 (Windows dev dep):** OPEN / LOW.
- **F7 (`deposit` staff-editable):** OPEN / LOW (parity observation; unchanged by F3).
- **F8 (admin edit recompute gap):** RESOLVED — `BookingAdmin.save_model` recomputes `total_amount` via `calculate_booking_total`; 4/4 admin tests pass, 307/307 suite green.
- **F9 (Django CVE):** RESOLVED — `Django==6.0.8`; pip-audit clean (0 vulns), 303/303 suite green, bandit/ruff clean.

All P0 security boundaries PASS. **bandit clean (exit 0); pip-audit clean (0 vulns, exit 0); ruff clean; full suite: 307 tests, 307 PASS, 0 FAIL, 0 ERROR, exit 0 (400.2s).** F3 + F8 together close the pricing-invariant protection boundary across HTTP form and Django admin.
