# Postgres — Pitfalls

- **Don't trust SQLite behavior as Postgres truth.** SQLite ignores
  `select_for_update` and serializes writes globally; a check-then-insert race
  that "passes" on SQLite can still exist on Postgres. Validate locking on
  Postgres.
- **"database is locked" is SQLite-only.** If you see it in dev, it's the
  swallowed write-lock artifact (ADR 0005), not something Postgres will show.
- **Missing indexes on tenant scoping columns** — every multi-tenant query
  filters by company/tenant; index those columns or scans scale with tenant data.
- **Connection pool under load** — default pool sizes can bottleneck under the
  attack profile; verify with real load data.
- **Migrations must be tested on Postgres**, not just `makemigrations --check`
  (which only detects drift, not runtime errors).
