# Postgres — Overview

Production database truth. Vroom deploys on Postgres 16 (docker compose
`postgres:16`, Hostinger VPS).

## What it is
The transactional backend for production. It provides real row locking
(`select_for_update`), serializable behavior, and production-grade concurrency —
unlike the SQLite dev harness.

## How it fits
- `DATABASE_URL=postgres://...` in production settings.
- Postgres is where concurrency claims are finally validated (ADR 0001, ADR 0005).
- postgres MCP (`platform/mcp/postgres.md`) gives live inspection once Docker +
  uv are available.

## Where it's heading
Caching via Redis and query-tuning against real production data are roadmap items
(`platform/ROADMAP.md`).
