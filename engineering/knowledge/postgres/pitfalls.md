# Postgres — Pitfalls

> **Legacy (2026-08-07).** Production DB is now **MySQL 8** (ADR 0006). The
> same principles apply: SQLite still can't prove concurrency claims; MySQL is
> now the backend to validate on (see `knowledge/mysql/overview.md`).

- **Don't trust SQLite behavior as production truth.** SQLite ignores
  `select_for_update` and serializes writes globally; a check-then-insert race
  that "passes" on SQLite can still exist on MySQL. Validate locking on MySQL.
- **"database is locked" is SQLite-only.** If you see it in dev, it's the
  swallowed write-lock artifact (ADR 0005), not something MySQL will show.
- **Missing indexes on tenant scoping columns** — every multi-tenant query
  filters by company/tenant; index those columns or scans scale with tenant data.
- **Connection pool under load** — default pool sizes can bottleneck under the
  attack profile; verify with real load data.
- **Migrations must be tested on the production backend**, not just
  `makemigrations --check` (which only detects drift, not runtime errors). CI
  runs the suite on MySQL 8 for this reason.
