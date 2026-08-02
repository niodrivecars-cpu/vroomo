# Booking — Edge Cases

Catalogue of tricky situations the reference tests must cover.

## Concurrency
- **Two users, same vehicle, same window** → exactly one succeeds (B1).
- **Adjacent windows (end == start)** → allowed (no overlap if exclusive).
- **SQLite "database is locked"** → HTTP 200 with no error markup; handled by
  `withSqliteRetry`, must not produce a phantom failure (dev-only).

## Tenancy
- **Cross-tenant vehicle reference** → rejected; booking stays in-tenant (B2).
- **Vehicle deleted under active booking** → PROTECT blocks deletion (B6).

## Windows & time
- **expected_return == pickup_date** → invalid (B3).
- **Booking spanning a weekend/holiday** → no special pricing yet; duration is
  wall-clock.
- **returned booking with actual_return < pickup_date** → invalid data; validate.

## Money
- **Zero/negative amount** → rejected (B4).
- **Deposit > total_amount** → policy question (Business Rules Review).

## Status
- **Cancelled booking that had a rental started** → currently impossible;
  confirm desired behavior.
- **Late → returned** → allowed; late is derived, cleared when returned.
