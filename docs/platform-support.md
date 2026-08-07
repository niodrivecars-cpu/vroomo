# Vroom — Platform Support Matrix

Target hosting: **Hostinger Business shared** (Passenger + LiteSpeed, MySQL,
in-memory cache) with the **VPS** (nginx + gunicorn + PostgreSQL + Redis) layout
kept as a reference path.

| Capability | Hostinger Business (target) | VPS (reference) |
|---|---|---|
| Runtime | Python via Passenger (`passenger_wsgi.py`) | Gunicorn behind nginx (systemd) |
| WSGI entry | `config.wsgi` through `passenger_wsgi.py` | `config.wsgi` via gunicorn |
| Database | MySQL / MariaDB via PyMySQL | PostgreSQL 16+ |
| DB driver | `PyMySQL` (+ `cryptography`) | `psycopg2-binary` (unused — see note) |
| Migrations | `manage.py migrate` (deploy script) | same |
| Static files | `collectstatic` into `STATIC_ROOT`, served by LiteSpeed | nginx `location /static/` |
| Media files | private, under `MEDIA_ROOT`, app-served downloads | same (nginx never serves `/media/`) |
| Cache | none (in-memory locmem) | Redis 7+ |
| Background jobs | none (no Celery in stack) | none |
| TLS | host-managed cert (auto-issued/auto-renewed) | certbot + Let's Encrypt |
| HTTPS redirect | host-level or `SECURE_SSL_REDIRECT` (env-tunable) | nginx `return 301` + Django redirect |
| Proxy trust | `TRUSTED_PROXY_IPS` empty → `REMOTE_ADDR` | `TRUSTED_PROXY_IPS=127.0.0.1` |
| Process supervision | Passenger (shared) | systemd unit `vroom.service` |
| Zero-downtime | restart via `tmp/restart.txt` touch | graceful `systemctl reload` (SIGHUP) |
| Deploy automation | hPanel Git auto-deploy + `scripts/deploy-hostinger.sh` | GitHub Actions CD + `scripts/deploy.sh` |
| CI database | **MySQL 8** (mirrors production) | — (Postgres historically, now MySQL) |
| Docker image | **not used in CI** (kept for local dev only) | GHCR image (historical) |
| Backups | `scripts/backup.sh` (mysqldump) + cron | same script (pg_dump) |
| Restores | `scripts/restore.sh` (mysql client) | same script (pg_restore) |
| Rate limiting | in-app (works on any host) | in-app |
| Audit logging | in-app (DB-backed) | in-app |
| Error tracking | Sentry — documented, not configured yet | Sentry — documented, not configured yet |

## Notes

> **Migration note (2026-08-07): PostgreSQL → MySQL is complete.** The project
> **no longer depends on PostgreSQL**. Verified across `fleet/models.py`, all
> migrations, and query usage: no `JSONField`/`JSONB`, `ArrayField`,
> `HStoreField`, `GinIndex`/`GIST`, `Unaccent`, raw SQL, `CheckConstraint`,
> `UniqueConstraint`, or custom indexes — only portable field types and ORM
> queries. Booking exclusivity (`select_for_update` in `fleet/views.py`) works
> on MySQL/InnoDB and is proven in CI (MySQL 8). Local dev and CI mirror this:
> `docker-compose.yml`, `setup.ps1`, and `README.md` use MySQL, and the full
> history is in `engineering/knowledge/mysql/overview.md` + ADR 0006.

- **DB driver:** `psycopg2-binary` was replaced by `PyMySQL` as the single
  driver. **Pin `PyMySQL>=1.2.0`** — it reports a mysqlclient-compatible
  `version_info` (`(2,2,8)`) that satisfies Django's `mysqlclient >= 2.2.1`
  import gate. `PyMySQL==1.1.1` (reports `(1,4,6)`) makes the MySQL backend
  fail at import time with `ImproperlyConfigured`, so the CI MySQL run must use
  the pin above. PostgreSQL is still supported at the settings level and the
  backup/restore scripts branch on the `DATABASE_URL` scheme, but MySQL is the
  tested production path.
- **CI parity:** the CI suite runs against MySQL 8 in a GitHub Actions service
  container so tests execute on the same backend as production. Local runs keep
  fast in-memory SQLite via `config.test_settings`.
- **Docker:** the `Dockerfile` is retained for local development; CI no longer
  builds or pushes images.
- **CD:** `cd.yml` was retired from `.github/workflows/` and preserved as a VPS
  reference at `docs/legacy/cd-vps-reference.yml`.

## Deploy checklist by platform

- **Hostinger:** `docs/deployment/hostinger-business.md`
- **VPS (reference):** `docs/deployment.md`
