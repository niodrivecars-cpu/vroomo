# MySQL — Overview

Production database truth. Vroom deploys on **MySQL/MariaDB** (Hostinger
Business shared hosting). See ADR 0006 and `docs/deployment/hostinger-business.md`.

> **Migration note (PostgreSQL → MySQL, 2026-08-07):** the production database
> is now MySQL. PostgreSQL is **not** the production dependency anymore —
> there is no `psycopg2` driver, no `postgres://` default, and no Postgres-only
> schema features. This is recorded in ADR 0006 and `docs/platform-support.md`.
> The Postgres path still exists only inside `backup.sh`/`restore.sh` as a
> scheme branch for the historical VPS reference, and in this file's earlier
> wording, which is superseded.

## What it is
The transactional backend for production. MySQL/InnoDB provides real row
locking (`select_for_update`), transactions, and production-grade concurrency —
unlike the SQLite dev harness. The booking-exclusivity path (`select_for_update`
in `fleet/views.py`) was verified to work on MySQL/InnoDB; CI runs the full suite
against MySQL 8 to keep it proven.

## How it fits
- `DATABASE_URL=mysql://...` in production settings (fallback builds `mysql://`
  from `DB_*`).
- `PyMySQL>=1.2.0` (+ `cryptography`) is the driver; `config/__init__.py`
  installs the `MySQLdb` shim so Django's `django.db.backends.mysql` works.
  **Version matters:** `PyMySQL==1.1.1` reports `version_info=(1,4,6)`, which
  fails Django's `mysqlclient >= 2.2.1` import gate (`ImproperlyConfigured`).
  1.2.0 reports `(2,2,8)` and passes. requirements.txt pins 1.2.0.
- CI mirrors production: the test suite runs against a MySQL 8 service
  container; local runs stay on in-memory SQLite (`config.test_settings`).
- Concurrency claims (ADR 0005 retry layer) are validated against MySQL in CI.

## Compatibility check (2026-08-07)
Reviewed `fleet/models.py`, all migrations, and query usage for Postgres-only
features before the pivot:
- No `JSONField`/`JSONB`, `ArrayField`, `HStoreField`, `GinIndex`, `GIST`,
  `on_conflict`, `gen_random_uuid`, or raw SQL.
- No `CheckConstraint`/`UniqueConstraint`/custom indexes beyond standard
  `unique=True` on `CharField` (VARCHAR) — all portable.
- Only portable field types: `CharField`, `TextField`, `IntegerField`,
  `DecimalField`, `DateField`, `DateTimeField`, `BooleanField`, `BigAutoField`,
  foreign keys. Decimal columns use MySQL `DECIMAL(10,2)` — safe for money.
- Aggregates (`Sum`, `F`) and lookups used are cross-database.

## Where it's heading
Caching via Redis (empty `CACHE_URL` on shared hosting = in-memory cache today)
and query-tuning against real production data are roadmap items
(`engineering/platform/ROADMAP.md`, Phase 4C).
