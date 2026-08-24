# Phase 22 — Documentation Reconciliation

## Methodology

Each claim in the engineering domain docs is compared against executable source code evidence. Claims are classified as VERIFIED, PARTIALLY VERIFIED, UNVERIFIED, UNKNOWN, MISSING, PLANNED, or DISPROVEN.

## Domain model docs (`engineering/domain/`)

### `domain/model/entities.md`

| Entity | Documented | In code (models.py) | Status |
|---|---|---|---|
| Company | Tenant/organization | Line 21-31 | VERIFIED |
| UserProfile | User-company binding | Line 34-43 | VERIFIED |
| Vehicle | Rentable asset | Line 59-82 | VERIFIED |
| VehicleDocument | Private documents | Line 85-170 | VERIFIED |
| Driver | Driver record | Line 173-187 | VERIFIED |
| Booking | Reservation/rental | Line 190-230 | VERIFIED |
| Maintenance | Service records | Line 233-258 | VERIFIED |
| Violation | Traffic violations | Line 261-309 | VERIFIED |
| AuditLog | Action trail | Line 312-350 | VERIFIED |
| Invoice | Planned | NOT in models.py | PLANNED |
| Payment | Planned | NOT in models.py | PLANNED |
| Customer | Planned | NOT in models.py | PLANNED |

**Finding:** Invoice, Payment, and Customer are documented as planned entities but not yet implemented in models. The `business-completeness-2026-08-02.json` evidence confirms: "10 gaps owned and tracked in Phase 2."

### `domain/model/policies.md`

21 policies (P1-P21) documented. Evidence file `executable-knowledge-2026-08-02.json` confirms:
- 21 policies parsed, validator PASS
- 8 Enforced, 10 Validated, 3 Proposed
- P1, P2, P4, P6, P15 marked as Validated-but-unimplemented (Phase 2A)
- P8, P16, P18 marked as Proposed

**Status:** VERIFIED

### `domain/model/state-machines.md` / `domain/booking/state-machine.md`

Booking state machine: `confirmed → rented → returned` (or `late`, `cancelled`).

**Evidence:** `models.py` L191-197 (Booking STATUS_CHOICES), `views.py` L285-325 (pickup/return enforcement).

**Status:** VERIFIED

## Vroom MD vs. Reality

### Claim: "Multi-tenant isolation via Company model + middleware"

**Actual evidence:** Verified — TenantScopedModel base class, TenantScopedManager, CompanyMiddleware, tenant_objects() helper.

**Status:** VERIFIED

### Claim: "Booking concurrency protection via SELECT FOR UPDATE"

**Actual evidence:** `views.py` L212-232 uses `transaction.atomic()` + `Vehicle.objects.select_for_update()`. k6 `sameVehicleBooking` test confirms 1 success / 49 rejections.

**Status:** VERIFIED

### Claim: "File uploads validated (extension, size, MIME)"

**Actual evidence:** `validators.py` with 3 validators; 14 tests in `test_security.py` + 11 tests in `test_documents.py` verify validation.

**Status:** VERIFIED

### Claim: "Rate limiting on login, upload, download"

**Actual evidence:** `settings/base.py` L131-140 defines 8 rate limits; `views.py` applies decorators; 12 tests in `test_ratelimit.py` + 18 tests in `test_client_ip.py` verify enforcement.

**Status:** VERIFIED

### Claim: "i18n with en/fr/ar, Arabic RTL"

**Actual evidence:** 3 locale catalogs with .po+.mo, 186-line test suite verifying integrity, 132-line locale test verifying RTL rendering.

**Status:** VERIFIED

### Claim: "No REST API — web UI only"

**Actual evidence:** `config/urls.py` L12-21 — no API router, no DRF. `fleet/urls.py` — 37 URL patterns, all template-based views.

**Status:** VERIFIED

### Claim: "No Celery in stack"

**Actual evidence:** `docs/deployment.md` §13 states "Celery is not part of this stack." No Celery config in any settings file. No `celery.py` file.

**Status:** VERIFIED

### Claim: "Redis is optional (LocMemCache fallback)"

**Actual evidence:** `base.py` L114-129 — Redis cache only if `CACHE_URL` is set, otherwise LocMemCache. Health check tests use LocMemCache.

**Status:** VERIFIED

## Discrepancies found

### DISCREPANCY D1: Test timing
- **Claimed:** "278 tests OK (792.077s)" in `rc1-suite.json`
- **Actual:** 278 tests found, 277 passed + 1 flaky failure in 355s on this machine
- **Cause:** `test_audit_log_default_ordering` is flaky due to `auto_now_add` second-granularity. On the CI run, timing was slower (792s) so the race didn't trigger. On this machine, tests ran faster (355s) and entries shared timestamps.
- **Status:** UNVERIFIED (test is environment-dependent)
- **Impact:** LOW — test bug, not a code bug. Fix: add sub-second delay or use `freezegun`/explicit timestamps.

### DISCREPANCY D2: python-magic on Windows
- **Claimed:** CI runs `python -m pytest` with full test suite passing
- **Actual:** On Windows, `python-magic` segfaults without `libmagic.dll`. The CI runs on Linux where it works.
- **Status:** UNVERIFIED on Windows (environment issue, not a code issue)
- **Impact:** LOW — CI on Linux is unaffected.

### DISCREPANCY D3: Database in CI vs dev
- The EC246a0 commit says "migrate dev stack to MySQL" but `.env.example` shows PostgreSQL credentials
- CI evidence shows MySQL grants (`ci/mysql: grant test_% privileges`)
- Test settings use SQLite in-memory
- **Status:** PARTIALLY VERIFIED — CI uses MySQL, tests use SQLite, dev `.env` shows PostgreSQL. This is a real inconsistency but doesn't affect test validity (SQLite is only for test, production uses PostgreSQL/MySQL via DATABASE_URL).
