# Postgres — References

> **Legacy (2026-08-07).** Production DB is now **MySQL 8** (ADR 0006). The
> `postgres:16` Docker service was replaced by `mysql:8.0`; see
> `knowledge/mysql/overview.md` and `docs/platform-support.md`. Kept as the
> historical reference for the VPS-era stack.

- Postgres docs: https://www.postgresql.org/docs/
- Legacy `docker-compose.yml` — the `postgres:16` dev service (now `mysql:8.0`).
- `config/settings/production.py` — DATABASE_URL wiring (now `mysql://`).
- `scripts/backup.sh`, `scripts/restore.sh` — backup/restore (scheme-branching).
- `knowledge/hostinger/` — deployment environment.
- postgres MCP guide: `platform/mcp/postgres.md` (disabled).
