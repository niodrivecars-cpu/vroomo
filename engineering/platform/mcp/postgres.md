# postgres MCP — legacy

> **Legacy, disabled (2026-08-07).** Production and dev databases are now
> **MySQL 8** (ADR 0006); the `postgres:16` Docker service was replaced by
> `mysql:8.0`, so this server has nothing to connect to. Kept for reference only.
> See `docs/platform-support.md` and `knowledge/mysql/overview.md`.

Live PostgreSQL inspection through postgres-mcp (crystaldba), configured in
`opencode.jsonc` (now `enabled: false`).

## Prerequisites (historical)
- `uv`/`uvx` installed (not yet present on the dev machine — install first).
- `docker compose up -d` with the postgres:16 service running.
- `.env` DATABASE_URL values matching the URI in `opencode.jsonc`.

## When to use
- Inspecting real schema (`\d`, indexes, constraints) instead of guessing.
- Debugging a query plan, locks, or data-specific bugs.
- Verifying a migration against the actual database the product ships on.

## When NOT to use
- The SQLite dev backend is running and the question is dev-only (most day-to-day
  work). MySQL is the prod target; SQLite is the dev harness.
- Without Docker/DB up — the server won't respond; check `docker ps` first.

## Common mistakes
- Treating SQLite behavior as equal to the production DB. E.g. SQLite ignores
  `select_for_update`; the swallowed "database is locked" path is dev-only.
  Validate concurrency claims on MySQL (CI runs the suite against MySQL 8), not
  SQLite.
- Running schema commands against the dev SQLite DB then shipping a migration
  that only works on one backend.
