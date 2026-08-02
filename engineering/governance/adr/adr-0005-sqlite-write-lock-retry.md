# ADR 0005: SQLite write-lock retry for concurrent booking

- **Status:** Accepted
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Vroom's booking-exclusivity rule (one vehicle per overlapping window) is
enforced with check-then-insert. On SQLite this raced: `select_for_update` is a
no-op, so concurrent POSTs serialize on the whole DB and the loser surfaces as a
swallowed "database is locked" that re-renders the form as HTTP 200. On Postgres
this path does not exist.

## Decision
Add a retry wrapper (`withSqliteRetry`) that detects the SQLite-lock artifact
(HTTP 200 with no rendered form error markup) and retries once. Real conflicts
and validation errors always render error markup, so the absence of it is the
dev-only lock signature. See `tests/performance/common.js`.

## Alternatives considered
- **Rely on Postgres behavior in dev** — rejected: dev is SQLite, and tests must
  be truthful there too.
- **Global DB-level serialization** — rejected: destroys concurrency.
- **Synchronize booking POSTs in the process** — rejected: single-process hack,
  not portable.

## Consequences
- **Positive:** truthful smoke tests on SQLite; no phantom failures; the rule
  still holds (exactly one success per same-vehicle window under load).
- **Negative:** one retry is best-effort; it does not change the Postgres
  production path.
- **Trade-off accepted:** dev-specific handling that is clearly documented as
  SQLite-only, so it is not mistaken for a production concurrency mechanism.

## Evidence
k6 smoke + attack: `same_vehicle_booking_success == 1` under 5 concurrent VUs on
one vehicle/window; post-run DB audit found 0 overlapping booking pairs.

## Compliance
Concurrency claims carry a test that asserts exactly-one-success under load;
the retry logic is isolated and documented as SQLite-dev-only.
