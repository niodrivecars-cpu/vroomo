# Performance Gate

The load bar a release must clear. Numeric thresholds, not impressions.

## Setup
- Fresh state: restart the server, clear cache, reset the test DB.
- Run against the same code that will be tagged.

## Runs
1. **Smoke (default):** `k6 run tests/performance/smoke.js`
2. **Attack:** `ATTACK=1 k6 run tests/performance/smoke.js`

## Thresholds (both runs)
All 9 from `tests/performance/smoke.js` must pass:

- `booking_http_500 == 0`
- `download_body_mismatch == 0`
- `health_non_200 == 0`
- `http_req_duration` p(95) < 5000
- `login_429_without_retry_after == 0`
- `same_vehicle_booking_success == 1`
- `tenant_isolation_violation == 0`
- `unexpected_http_4xx == 0`
- `unexpected_http_5xx == 0`

## Pass criteria
Both runs exit 0 AND all thresholds green. Archive output + summary under
`evidence/performance/`.

## RC1 baseline
- default: p95 980.07 ms, 356/358 checks.
- attack: p95 3.21 s, 414/415 checks.
- Residual check failures were the SQLite write-lock artifact (HTTP 200, no row
  persisted) — not application failures; error thresholds stayed 0.

## Caveat
Run k6 on a machine with it installed and sufficient RAM; results depend on
fresh state.
