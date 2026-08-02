# ADR 0001: SQLite dev / Postgres production split

- **Status:** Accepted
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Vroom needed a dev database that requires zero infrastructure and a production
database that is transactional and production-grade. Postgres is the deployment
target (Hostinger VPS, docker compose `postgres:16`).

## Decision
Develop and run tests against SQLite (`config/settings/test.py`, in-memory);
deploy against Postgres. Documented in `knowledge/postgres/` and
`knowledge/django/`.

## Alternatives considered
- **Postgres everywhere** — requires a running service for every dev; not portable.
- **SQLite everywhere** — unsafe for production concurrency and data volume.

## Consequences
- **Positive:** zero-setup dev, fast CI, portable tests.
- **Negative:** SQLite silently ignores `select_for_update` and swallows
  "database is locked", masking concurrency behavior. Concurrency claims must be
  validated against Postgres or proven with targeted tests.
- **Trade-off accepted:** the dev/prod DB divergence is handled by an explicit
  retry layer (ADR 0005) and documented pitfalls.

## Evidence
`fleet/tests/` run 278 tests on SQLite; load tests exercised the SQLite
write-lock artifact; postgres MCP prepared for Postgres verification.

## Compliance
`config/settings/test.py` uses `:memory:` SQLite; production settings require
`DATABASE_URL` pointing at Postgres; concurrency tests are tagged and reviewed.
