# Booking Knowledge — Best Practices

- **Enforce exclusivity at the view/service layer**, then back it with a unique
  constraint where the DB supports it.
- **Prove concurrency claims with a load test** — `same_vehicle_booking_success == 1`
  under concurrent VUs is the accepted proof.
- **Scope booking queries by company**; never cross tenant lines.
- **Handle the SQLite lock artifact explicitly** in dev/load paths
  (`withSqliteRetry`), clearly documented as dev-only.
- **Link violations to active booking context** for a complete audit trail.
