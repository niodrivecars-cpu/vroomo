# Booking — Invariants

Invariants hold at all times. Each maps to a reference test (`test-matrix.md`).

| # | Invariant | Enforcement | Proof |
|---|---|---|---|
| B1 | No two non-cancelled bookings of the same vehicle have overlapping `[pickup, expected_return)` windows | check-then-insert at view layer + concurrency retry | k6 `same_vehicle_booking_success == 1` under 5 VUs on one window |
| B2 | `vehicle.company == booking.company` and `driver.company == booking.company` | tenant-scoped manager + validation | IDOR/cross-tenant tests |
| B3 | `expected_return > pickup_date` | form validation | validation tests |
| B4 | `total_amount >= 0`, `deposit >= 0` | form/model validation | validation tests |
| B5 | Booking status is always one of the enum values; transitions respect the state machine | choices + service enforcement | state-machine tests |
| B6 | A booking's vehicle/driver cannot be deleted while the booking exists (PROTECT) | FK `on_delete=PROTECT` | model tests |

## Notes
- B1 is the load-critical invariant. On SQLite it is proven via the
  `withSqliteRetry` artifact handling; on Postgres, `select_for_update` is the
  production-grade guard (ADR 0005).
- B2 is the isolation invariant — its failure is a security incident, tested
  both unit-level and under load (`tenant_isolation_violation == 0`).
