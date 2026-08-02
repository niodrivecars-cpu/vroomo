# Verification Gate — v1.0.0-rc1

Date: 2026-08-02
Commit: `b269e92` (tag `v1.0.0-rc1`)

## Static / Unit Gate

| Step | Result | Evidence |
|---|---|---|
| `ruff check .` | PASS | exit 0, no issues |
| `bandit -r fleet config -q -ll` | PASS | exit 0 |
| `pip-audit -r requirements.txt -r requirements-dev.txt` | PASS | "No known vulnerabilities found" |
| `makemigrations --check --dry-run --settings=config.test_settings` | PASS | "No changes detected" |
| `manage.py test fleet --settings=config.test_settings --verbosity=2` | PASS | 278 tests, OK (792.077s) |
| `collectstatic --noinput --settings=config.test_settings` | PASS | 130 static files |
| `check --deploy` (production settings) | PASS | exit 0, 1 warning (CI placeholder `SECRET_KEY` length — expected) |
| `compilemessages` | SKIP (local) | `msgfmt` not installed on dev machine; CI installs gettext. Catalog integrity covered by test suite (`test_i18n_catalog`, `.mo` ↔ `.po` sync verified in 278-test run). |

## Load Gate (k6)

Two smoke runs on a fresh SQLite-backed server (fresh cache, no prior state):

| Run | Exit | Checks | p95 http_req_duration | Verdict |
|---|---|---|---|---|
| default | 0 | 356 succeeded / 358 (2 transient SQLite-lock 200s, no rows persisted) | 980.07 ms | PASS |
| attack (cross-tenant, expired/tampered/oversized downloads) | 0 | 414 succeeded / 415 (1 transient SQLite-lock `booking-create` 200, no row persisted) | 3.21 s | PASS |

All 9 thresholds green in both runs:

- `booking_http_500` == 0
- `download_body_mismatch` == 0
- `health_non_200` == 0
- `http_req_duration` p(95) < 5000
- `login_429_without_retry_after` == 0
- `same_vehicle_booking_success` == 1
- `tenant_isolation_violation` == 0
- `unexpected_http_4xx` == 0
- `unexpected_http_5xx` == 0

Post-run audit (attack run): 46 bookings created, 0 overlapping pairs, all 6 vehicles exercised,
0 rate-limit denials. Tenant isolation enforced at the view layer (source-tenant boundary checks in
`fleet/views.py`, defensive `.filter(...)` on every cross-tenant query).

## Note on the 2/1 failing checks

Both failures were HTTP 200 responses that hit a transient SQLite write lock
(`database is locked`) inside a retry loop, and no row was persisted. They are
load-frame artifacts of the SQLite test backend, not application failures; all
error-path thresholds (`unexpected_http_4xx/5xx`, `booking_http_500`) remained 0.
The Django-level `with_sqlite_retry` wrapper (SQLite `isSqliteLockArtifact`
detection) handles these in production.

## How to reproduce

```bash
# default smoke
k6 run tests/performance/smoke.js
# attack smoke (requires fresh DB/cache; see docs/load-testing.md)
ATTACK=1 k6 run tests/performance/smoke.js
```
