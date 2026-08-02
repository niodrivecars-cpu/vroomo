# postgres MCP

Live PostgreSQL inspection through postgres-mcp (crystaldba), configured in
`opencode.jsonc`.

## Prerequisites
- `uv`/`uvx` installed (not yet present on the dev machine — install first).
- `docker compose up -d` with the postgres:16 service running.
- `.env` DATABASE_URL values matching the URI in `opencode.jsonc`.

## When to use
- Inspecting real schema (`\d`, indexes, constraints) instead of guessing.
- Debugging a query plan, locks, or data-specific bugs.
- Verifying a migration against the actual database the product ships on.

## When NOT to use
- The SQLite dev backend is running and the question is dev-only (most day-to-day
  work). Postgres is the prod target; SQLite is the dev harness.
- Without Docker/DB up — the server won't respond; check `docker ps` first.

## Call order
1. Confirm DB is up: `docker compose ps`.
2. Connect via postgres MCP.
3. Inspect → reproduce → fix → verify migration with `makemigrations --check`.

## Common mistakes
- Treating SQLite behavior as equal to Postgres. E.g. SQLite ignores
  `select_for_update`; the swallowed "database is locked" path is dev-only.
  Validate concurrency claims on Postgres, not SQLite.
- Running schema commands against the dev SQLite DB then shipping a migration
  that only works on Postgres.

## Example
```
Inspect: show columns of fleet_booking;
Verify: EXPLAIN the booking exclusivity query for overlapping windows.
```
