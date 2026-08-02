# Booking Knowledge — Pitfalls

- **Assuming window-overlap checks are atomic.** Check-then-insert without a
  lock/constraint can double-book under concurrency (SQLite ignores row locks).
- **Swallowing "database is locked"** — re-renders a valid form as HTTP 200 with
  no error markup; on SQLite this is a dev-only signature, handled by
  `withSqliteRetry`.
- **Booking for a vehicle in another company** — the booking must stay inside
  the tenant's own vehicles (isolation).
- **Not testing the "exactly one winner" case** — the exclusivity guard is only
  proven by a concurrent test, not by reading the code.
