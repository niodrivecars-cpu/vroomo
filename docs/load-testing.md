# Vroom – Concurrency Smoke Testing (RC1 gate)

A lightweight, correctness-focused load test that answers one question the
275-test functional suite cannot: **does the application stay correct under
concurrent load?**

It is **not** a benchmark. The goal is to expose obvious concurrency problems
— 5xx responses, corrupted downloads, cross-tenant leakage, broken rate-limit
behavior, race conditions — not to measure throughput or latency. A single
profile of 1–5 virtual users per workflow over ~3 minutes is enough for that.

Scenarios live in `tests/performance/` as k6 scripts. `smoke.js` runs the
whole gate; each scenario file can also run standalone.

## Prerequisites

- [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) ≥ 0.49.
- A running instance of the application (dev `runserver`, or staging behind
  nginx) reachable from the machine running k6.
- The database seeded for the test (see below). Seeding creates two tenant
  companies, staff users, vehicles, drivers, and one document per vehicle with
  real signed-URL tokens, and writes the `loadtest_config.json` that every
  script loads at start.

### Seed the dataset

Run from the repo root:

```bash
# local/dev
python manage.py loadtest_seed --output tests/performance/loadtest_config.json
```

The command is idempotent: re-running reuses the same companies, users,
vehicles and documents and only refreshes the signed-URL tokens. Passwords are
reset to `--password` (default `Loadtest!2026`) on every run, so a fresh seed
always allows logins.

**Re-running the smoke gate requires a fresh database (or clearing the loadtest
bookings) *and a freshly restarted server*.** Booking windows in the scenarios
are relative to run time, so a second run on the same day re-books the same
absolute dates and produces legitimate conflict form errors. Either
delete/recreate the test database (and `MEDIA_ROOT`) before the gate run, or
delete the loadtest companies' `Booking` rows between runs. Rate limits and
upload/download throttle counters live in the cache (LocMemCache in dev), so a
failed run's counters would otherwise bleed into the next run; restart the dev
server between runs to get a fresh cache (and only audit `AuditLog` rows
written *after* the restart).

The generated `loadtest_config.json` must sit next to the scripts
(`tests/performance/`), because k6 resolves `open()` relative to the script
file. On staging, run the seed against the staging database and copy the file
to the machine/directory that runs k6 (or point every script at it with
`LOADTEST_CONFIG`).

The media files written by the seed land under `MEDIA_ROOT` and the config JSON
is gitignored; neither should be committed.

## Environment variables

All optional, all read at k6 startup:

| Variable               | Default                     | Purpose                                                            |
| ---------------------- | --------------------------- | ------------------------------------------------------------------ |
| `BASE_URL`             | `http://127.0.0.1:8000`     | Application base URL.                                              |
| `LOADTEST_CONFIG`      | `loadtest_config.json`      | Path to the seeded config (resolved relative to the script file).  |
| `SIMULATE_CLIENT_IP`   | `1`                         | Give every VU its own `X-Forwarded-For`. See “Client-IP isolation”.|
| `ATTACK`               | `0` (used by `smoke.js`)    | Enable the login brute-force scenarios.                            |

## Running the tests

`SIMULATE_CLIENT_IP` defaults to on. The app only honors forwarded IPs from
addresses listed in `TRUSTED_PROXY_IPS`, so **before any run** make sure the
load generator's address is trusted (this is the same setting documented in
`docs/deployment.md`):

```bash
# local dev .env (the load generator is 127.0.0.1):
TRUSTED_PROXY_IPS=127.0.0.1

# staging: add the load generator's egress IP for the test window:
TRUSTED_PROXY_IPS=<load-generator-ip>
```

This works both directly against a dev server and through nginx: k6 sends a
distinct `X-Forwarded-For` per VU, nginx appends its own hop, and
`fleet.security.get_client_ip` resolves the k6-supplied address because the
connection arrives from a trusted peer. It is what makes authenticated
workflows load-testable at all — without it every VU shares one source IP and
the per-IP login throttle (5/m) trips on the 6th login of the whole run.

```bash
# Full RC1 gate (concurrency workflows + health):
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/performance/smoke.js

# Full gate plus the login-throttle attack on isolated client IPs:
k6 run -e BASE_URL=http://127.0.0.1:8000 -e ATTACK=1 tests/performance/smoke.js

# Focused scenario runs:
k6 run -e BASE_URL=http://127.0.0.1:8000 -e ATTACK=1 tests/performance/login-rate-limit.js
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/performance/document-download.js
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/performance/booking-workflow.js
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/performance/tenant-isolation.js
```

Only disable `SIMULATE_CLIENT_IP` if you have a concrete reason (e.g. multiple
load generators on distinct source IPs). On a single generator it will fail
quickly with unexpected 429s on logins.

## What each scenario does

| Scenario            | Workload                                                                 | Checks                                                                                     |
| ------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `healthProbe`       | Polls `/health/` every 3s for the whole run.                              | HTTP 200 and JSON `status == "ok"` (DB + cache reachable).                                 |
| `bruteForce`        | 1 VU hammers `/accounts/login/` with distinct usernames.                  | Limit (5/m per IP) trips to 429; `Retry-After` present; no 5xx.                            |
| `successLogin`      | 3 VUs log in legitimately (≤3 attempts each, below their own 5/m). | Each → 302; never throttled by the attacker's IP (isolation). |
| `authDownload`      | Authenticated downloads, plus a cross-tenant document id.                | 200 with the exact seeded file bytes; foreign company id → 404.                             |
| `signedDownload`    | Signed-URL downloads (anonymous).                                        | Valid token streams full bytes; expired → 403; tampered → 403.                             |
| `distinctBooking`   | 3 VUs create bookings on non-conflicting (vehicle, day) pairs.           | Every POST → 302; no 5xx.                                                                  |
| `sameVehicle`       | 5 VUs simultaneously book company A's first vehicle for one window.      | Exactly one success (exclusive-booking invariant); losers get the form error.              |
| `companyA`/`companyB` | Mixed tenant traffic: A books/downloads, B lists/uploads/books.         | No cross-tenant data in lists, no cross-tenant downloads, no cross-tenant booking accepted.|

## Pass / fail criteria

The error budget maps directly to k6 thresholds. `smoke.js` fails (nonzero
exit) if any of these thresholds is violated:

| Threshold                                             | Meaning                                                                 |
| ----------------------------------------------------- | ----------------------------------------------------------------------- |
| `unexpected_http_5xx == 0`                            | No HTTP 500 anywhere.                                                    |
| `unexpected_http_4xx == 0`                            | No 4xx outside the explicitly expected sets (expected: 404 cross-tenant, 403 bad/expired tokens, 429 throttled, 200 form errors). |
| `health_non_200 == 0`                                 | Health endpoint never degraded during the run.                           |
| `booking_http_500 == 0`                               | No server errors during booking creation.                                |
| `download_body_mismatch == 0`                         | Every download returned the exact seeded byte length and PDF magic.      |
| `same_vehicle_booking_success == 1`                   | The exclusive-booking guard held under the race (see below).             |
| `tenant_isolation_violation == 0`                     | No foreign license plates/customer markers ever appeared in a tenant's own lists. |
| `login_429_without_retry_after == 0`                  | Every 429 carried `Retry-After: 60` (only present with `ATTACK=1`).      |
| `http_req_duration p(95) < 5000ms`                    | Sanity latency gate only — catches gross hangs, not regressions.         |

A green `smoke.js` exits 0. Red thresholds are printed in the summary and exit
nonzero.

**Gate definition.** The gate is green when k6 exits 0 **and** every threshold
above is met. A small number of individual *checks* may still fail inside a
green run — on SQLite the booking POSTs race the `database is locked`
`OperationalError`, which `booking_create` swallows and degrades to a plain
200 form re-render (`fleet/views.py`), so a rare `booking-create: status 302`
/ `iso-b-book: status 302` check failure means "that POST got a lock artifact,
retried, and never persisted a row" — not a lost or double booking. The
DB-side post-run audit (below) confirms no data was lost. Chase a fully
check-green SQLite run only by raising the retry budget in
`tests/performance/common.js`; do not tune `settings`/`busy_timeout` for the
test.

### SQLite lock retry in the scripts
On the SQLite test database a booking POST can hit `database is locked` and
return a 200 form with **no** `invalid-feedback` error block, which is
indistinguishable from a successful render unless the body is inspected. The
scripts handle this explicitly:
- `common.js` defines `isSqliteLockArtifact(res)` — `res.status === 200` with
  no `invalid-feedback` substring — and `withSqliteRetry(fn, attempts=3)` which
  re-POSTs with a 250 ms backoff when that signature is seen.
- It is wired only where a *success* is required for correctness:
  `distinctBooking` (booking-workflow) and the `companyA`/`companyB` booking
  POSTs (tenant-isolation). It is deliberately **not** applied to the
  `sameVehicle` losers (those are supposed to 200) or to `iso-b-cross-book`
  (a genuine conflict 200). A real conflict re-render always carries the
  `invalid-feedback` error block (rendered by django-bootstrap5's
  `field_errors.html`), so it is never mistaken for a lock artifact.
- This is a test-environment accommodation: `database is locked` cannot happen
  on MySQL/InnoDB, which is why the retry is scoped to the scripts, not the app.

## Post-run verification (audit trail)

k6 cannot see the database; the audit assertions are a two-part check:

```bash
# Count of failed logins and throttling events from the brute-force run:
python manage.py shell -c "
from fleet.models import AuditLog
print('LOGIN_FAILED  ', AuditLog.objects.filter(action='LOGIN_FAILED').count())
print('LOGIN         ', AuditLog.objects.filter(action='LOGIN').count())
print('RATE_LIMITED  ', AuditLog.objects.filter(action='RATE_LIMITED').count())
print('DOWNLOAD      ', AuditLog.objects.filter(action='DOWNLOAD').count())
print('CREATE        ', AuditLog.objects.filter(action='CREATE').count())
"
```

- `RATE_LIMITED` must be nonzero and roughly equal to the number of 429s in the
  brute-force run (each 429 is written once by `RateLimitLogMiddleware`).
- `DOWNLOAD` must be nonzero and cover every successful and denied download.
- Every seeded company must have a `LOGIN` row for its users, and bookings must
  produce `CREATE` rows with the correct `company_id`.
- Only count rows created **after** the run started (the `AuditLog` table is
  never emptied by the seed); filter by `created_at` or start from a cleared
  table.

## Notes and known considerations

### Fixed-window rate limiting and 429 timing
django-ratelimit uses fixed windows. The brute-force scenario therefore asserts
**behavior** (a 429 eventually appears and carries `Retry-After`) rather than
an exact attempt count. The same is true of the functional test suite.

### Client-IP isolation (`SIMULATE_CLIENT_IP`)
The app only honors `X-Forwarded-For` from addresses in `TRUSTED_PROXY_IPS`
(`fleet.security.get_client_ip`), so the load generator must be a trusted peer
for the test window. With `SIMULATE_CLIENT_IP=1` each VU then presents a
distinct `X-Forwarded-For`, and the login throttle, download rate limits and
tenant workflows operate on per-client-IP buckets end to end — locally and
through nginx. Leave `TRUSTED_PROXY_IPS` back at its production value (the
real proxy addresses) as soon as the test is done.

### The `same_vehicle_booking_success == 1` threshold

**What the scenario validates.** `booking_create` enforces exclusive booking
with a check-then-insert: a SELECT looks for an overlapping
`status__in=['confirmed','rented']` booking, and only if none exists does the
INSERT proceed. A bare check-then-insert is not atomic, so under a tight race
two requests can both pass the SELECT and both succeed. The `sameVehicle`
scenario fires five simultaneous requests at one vehicle/window specifically to
expose this.

**How the app guarantees exclusivity.** Since the RC1 gate, `booking_create`
(and `booking_edit`) wrap the check-and-insert in `transaction.atomic()` and
lock the vehicle row with `select_for_update()`. On MySQL/InnoDB (production)
this serializes concurrent booking attempts for the same vehicle: the second
request blocks on the row lock, then re-runs the overlap SELECT and sees the
winner, so it renders the conflict form instead of double-booking.

**SQLite caveat (test database).** SQLite ignores `FOR UPDATE`, so the row lock
is a no-op under the test DB. The `transaction.atomic()` wrapper still helps:
a request that would lose the race either re-checks after the winner commits
(conflict form, 200) or hits SQLite's `database is locked`/`OperationalError`,
which the view catches and degrades to a plain form re-render (200). Either way
it does not become a second confirmed booking, so the gate's "exactly one
winner" assertion holds on SQLite too — but the *serialization* itself is only
verifiable on MySQL (the CI suite runs against MySQL 8). Unit tests
(`fleet/tests/test_views.py`) assert the lock is acquired on both the create
and edit paths.

**Expected behavior under the invariant.** Exactly **one** request wins the
window (302) and the other four are **rejected by design** — they render the
form with the conflict error (HTTP 200). This asymmetry is the point of the
test, not a flake: failing requests are the system correctly enforcing
exclusivity. `same_vehicle_booking_success` therefore counts **winners**, and
`unexpected_http_4xx == 0` is not violated because a 200 conflict form error is
an explicitly expected outcome (a 429/403/404 there would be a separate
regression).

**What constitutes a regression.** The threshold fails only when the count of
winners differs from 1 — i.e. the invariant is genuinely violated by
overlapping confirmed bookings. That includes:
- `count == 0` → no request won, so the race never reached the view (e.g. a
  request was dropped before the INSERT, a session/login failure, or the
  window collided with another booking).
- `count > 1` → two overlapping bookings were committed. On MySQL this
  means the `select_for_update` guard regressed (or the lock was removed); on
  SQLite it can only mean the overlap SELECT itself regressed, since the lock
  is a no-op there.

**How to fix it if it fails.** Inspect
`Booking.objects.filter(vehicle=…, status__in=['confirmed','rented'])` for
overlapping rows, and confirm `fleet/views.py` still acquires the vehicle row
lock (`select_for_update()`) inside `transaction.atomic()` in both
`booking_create` and `booking_edit`.

### The 403-on-upload expectation in `document_create`
Document uploads are rate-limited (`upload_per_user` 10/m). The tenant
isolation scenario uploads at most a handful of times per VU, keeping every run
under that limit; a 429 there would surface as an unexpected 4xx and fail the
test, which is the desired signal if upload throughput is ever raised.

### Signed downloads and the anonymous rate limit
`download_anon_ip` (default `10/h`) applies to anonymous signed-URL downloads
per client IP. The `signedDownload` scenario keeps its volume well under that
limit (a few valid tokens per VU) so the run validates token expiry/integrity
rather than tripping the throttle; the throttle itself is covered by unit tests
and by `downloads.is_download_rate_limited`.

### Auth downloads and `download_per_user`
`download_per_user` (default `20/h`) applies to authenticated downloads.
`authDownload` picks its user from the seeded list via the global k6 `__VU`
id, and adding/removing scenarios (e.g. `ATTACK=1`) shifts that numbering — in
the worst case both download VUs can land on the same user. The scenario
therefore caps its iterations at 9 per VU (2 × 9 = 18), keeping even the
collision worst case under the 20/h ceiling, so a run validates download
integrity instead of tripping the authenticated throttle.
