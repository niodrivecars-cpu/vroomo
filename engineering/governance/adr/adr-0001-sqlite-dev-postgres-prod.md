# ADR 0001: SQLite dev / MySQL production split

- **Status:** Superseded by 0006 (production database changed from Postgres to
  MySQL; the SQLite-dev half still stands)
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Vroom needed a dev database that requires zero infrastructure and a production
database that is transactional and production-grade. MySQL 8 is the deployment
target (Hostinger VPS, docker compose `mysql:8`, served via `DATABASE_URL` with
PyMySQL).

## Decision
Develop and run tests against SQLite (`config/settings/test.py`, in-memory);
deploy against MySQL 8 (`config/settings/base.py` parses `DATABASE_URL`,
CI uses `mysql://vroom:vroom@127.0.0.1:3306/vroom_ci`). Documented in
`knowledge/mysql/` and `knowledge/django/`.

## Alternatives considered
- **Postgres everywhere** — was the original production target but dropped in
  favour of MySQL on Hostinger; not the deployed engine.
- **SQLite everywhere** — unsafe for production concurrency and data volume.
- **MySQL everywhere** — rejected for dev to keep zero-setup, portable tests.

## Consequences
- **Positive:** zero-setup dev, fast CI, portable tests; MySQL honours
  `select_for_update`, so concurrency behavior is observable in production.
- **Negative:** SQLite silently ignores `select_for_update` and swallows
  "database is locked", masking concurrency behavior. Concurrency claims must be
  validated against MySQL or proven with targeted tests.
- **Trade-off accepted:** the dev/prod DB divergence is handled by an explicit
  retry layer (ADR 0005) and documented pitfalls.

## Evidence
`fleet/tests/` run against SQLite in CI; production CI jobs run MySQL 8.0
(`DATABASE_URL=mysql://vroom:vroom@127.0.0.1:3306/vroom_ci`); concurrency
control relies on `select_for_update`, which MySQL enforces.

## Compliance
`config/settings/test.py` uses `:memory:` SQLite; production settings require
`DATABASE_URL` pointing at MySQL 8; concurrency tests are tagged and reviewed.
