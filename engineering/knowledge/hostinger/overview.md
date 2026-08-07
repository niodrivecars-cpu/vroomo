# Hostinger Knowledge

Deployment environment specifics for Vroom.

## Layout
- Hostinger **Business shared hosting** — the app runs as a Python App via
  Passenger (hPanel → Websites → Manage → Python App). The VPS layout is kept as
  a historical alternative (`docs/deployment.md`).
- Passenger serves the app from `passenger_wsgi.py`; static via collectstatic.
- MySQL/MariaDB created in hPanel (Databases → MySQL Databases); the app
  connects via `DATABASE_URL=mysql://...` (PyMySQL shim, see
  `knowledge/mysql/overview.md`). Postgres is no longer a production dependency
  (ADR 0006).
- No Redis on shared hosting: `CACHE_URL` stays empty (in-memory cache).

## Operations
- Deploy: `scripts/deploy.sh`; rollback: `scripts/rollback.sh`.
- Backup: `scripts/backup.sh`; restore: `scripts/restore.sh`.
- Health: `scripts/healthcheck.sh`.
- Deployment notes: `docs/deployment.md`.

## Where it's heading
Production observability (Sentry, logging) — see `platform/ROADMAP.md`.
