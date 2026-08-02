# Load Testing Knowledge

k6 methodology for Vroom — how releases are proven under load.

## The method (short version)
1. **Fresh state.** Restart the server, reset the DB/cache. Stale state poisons
   results (see `docs/load-testing.md`).
2. **Two profiles.** `smoke.js` (default) + `ATTACK=1` (adversarial:
   cross-tenant, expired/tampered/oversized, rate-limit abuse).
3. **Assert thresholds, not impressions.** exit 0 AND all thresholds green.
4. **Archive everything.** Output + summary → `evidence/performance/`.

## Thresholds (smoke.js)
`booking_http_500 == 0`, `download_body_mismatch == 0`, `health_non_200 == 0`,
`http_req_duration p(95) < 5000`, `login_429_without_retry_after == 0`,
`same_vehicle_booking_success == 1`, `tenant_isolation_violation == 0`,
`unexpected_http_4xx == 0`, `unexpected_http_5xx == 0`.

## Concurrency proof
`sameVehicleBooking` forces 5 VUs onto one (vehicle, window); exactly one must
succeed — this is the load proof for the exclusivity guard (ADR 0005).

## Known dev artifacts
- 2/1 residual check failures in RC1 runs were the SQLite write-lock artifact
  (HTTP 200, no row persisted), not application failures; error thresholds stayed
  0. Postgres never hits this path.
- Under `ATTACK=1`, download VUs can collide on one user and trip the 20/h
  download limit — `authDownloads` iterations are capped (9) to stay under it.

## References
- `docs/load-testing.md` — full run instructions.
- `tests/performance/*.js` — scripts.
- `evidence/performance/` — RC1 summaries.
