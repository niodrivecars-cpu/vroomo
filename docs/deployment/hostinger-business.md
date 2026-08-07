# Vroom — Hostinger Business Deployment Guide

Target: **Hostinger Business shared hosting**. The app runs as a **Python App**
via **Passenger** (hPanel → Websites → Manage → **Python App**), backed by
**MySQL/MariaDB** created in hPanel (Databases → MySQL Databases). This is the
production reference; the VPS layout (`docs/deployment.md`) is kept as an
alternative.

> **Before you start — hPanel check (blocking):**
> Confirm that the plan shows a **Python App** option (hPanel → Websites →
> Manage → the site → the app menu). Hostinger Business shared ships it; if the
> menu item is missing, the plan cannot run Passenger and this guide does not
> apply (revisit the plan choice).

## Reference architecture

```
Internet
   │  HTTPS (host-managed TLS on LiteSpeed/Apache)
   ▼
LiteSpeed/Apache (TLS, static files, proxies / to Passenger)
   │
   ▼
Passenger (reads passenger_wsgi.py at the app root)
   │
   └─── MySQL/MariaDB  (DATABASE_URL, from hPanel Databases)
          cache: in-memory (no Redis on shared hosting)
```

`/health/` is public and returns HTTP 200 only when the database is reachable;
point your uptime monitor at it.

## 1. Create the database in hPanel

1. hPanel → Databases → MySQL Databases → **Create New Database**.
2. Record: database name, user, password, host (usually `127.0.0.1` or
   `localhost`).

## 2. Create the Python App in hPanel

1. hPanel → Websites → Manage → **Python App** → **Create**.
2. Settings:
   - **App root / directory:** a folder inside `public_html` or the domain
     path, e.g. `vroom`.
   - **Entry point:** `passenger_wsgi.py`.
   - **Python version:** one supported by the app (3.12 preferred).
3. Set the **environment variables** in the app's "Environment" section
   (or via a `.env` file in the app root — `config.settings` reads both via
   `python-decouple`):
   - `DJANGO_SETTINGS_MODULE=config.settings.production`
   - `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
     `DATABASE_URL=mysql://...`
   - `SECURE_SSL_REDIRECT` — set `False` only if the host does not forward
     `X-Forwarded-Proto` and you get a redirect loop; the host-level HTTPS
     redirect then covers it.
   - `TRUSTED_PROXY_IPS` — leave empty on shared hosting (falls back to
     `REMOTE_ADDR`; no forwarded IPs are trusted, so client-IP rate limiting
     keys off the connection source).

## 3. Deploy the code

Preferred: **hPanel → Git** (Auto Deploy) pulls from the GitHub repository into
the app directory on every push to the chosen branch (use a release branch such
as `release/1.0`).

After the pull (or when running manually over SSH):

```bash
bash scripts/deploy-hostinger.sh /path/to/app /path/to/.env release/1.0
```

`deploy-hostinger.sh` performs, without sudo/systemd/Docker:

1. `git fetch` + `git checkout <ref>` (skipped when the host auto-deployed)
2. refresh the `venv/` and `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput`
5. `python manage.py compilemessages`
6. `python manage.py check --deploy`
7. `touch tmp/restart.txt` → Passenger reloads the app
8. `/health/` probe over HTTPS

## 4. Static and media files

- **Static:** `collectstatic` writes to `STATIC_ROOT` (default
  `<app-dir>/staticfiles`). hPanel/LiteSpeed serves it directly. If static
  files 404, check the app root is correct in the Python App settings and that
  `STATIC_ROOT` is on a served path.
- **Media:** private uploads under `MEDIA_ROOT` (default `<app-dir>/media`).
  As on the VPS, nothing is served by the web server — downloads go through the
  application (see `docs/deployment.md` §7).

## 5. Environment file

Copy `.env.production.example` to the app root as `.env`, fill in real values,
and `chmod 600`. hPanel "Environment" variables override the file.

Required keys: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `DATABASE_URL` (or `DB_*`), `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD`, `ADMIN_EMAIL`. `CACHE_URL` stays empty (in-memory cache).

## 6. Post-deploy verification

```bash
curl -fsS https://<your-domain>/health/
./venv/bin/python -m manage check --deploy
```

`deploy-hostinger.sh` already runs `check --deploy` and the health probe.

## 7. Backups

`scripts/backup.sh /path/to/app /path/to/.env /path/to/backups` — detects MySQL
from `DATABASE_URL` and runs `mysqldump` (or `pg_dump` on Postgres), archives
`media/`, and prunes backups older than 14 days. Schedule with the hPanel
**Cron Jobs** feature:

```cron
0 3 * * * /path/to/app/scripts/backup.sh /path/to/app /path/to/.env /path/to/backups >> /path/to/backups/backup.log 2>&1
```

Test restores regularly in a scratch environment — an untested backup is a hope.

## 8. Rollback

- **Application-only regression:** `git checkout <previous-tag>` (or re-run
  `deploy-hostinger.sh` with the previous ref), then `touch tmp/restart.txt`.
  `deploy-hostinger.sh` records the previous ref in `.deploy-state`.
- **Database/data disaster:** restore from backup with
  `scripts/restore.sh /path/to/app /path/to/.env /path/to/backups/<stamp>`
  (runs the `mysql` client path when `DATABASE_URL` is MySQL), then redeploy the
  matching release.

## 9. Monitoring

Shared hosting has **no systemd/journald, no Redis CLI, no local Postgres** —
the VPS checklist (`docs/deployment.md` §13) only partially applies:

| Check | How | Healthy |
|---|---|---|
| App answers | `curl -fsS https://<domain>/health/` | HTTP 200, `"status":"ok"` |
| Uptime | hPanel uptime monitor or UptimeRobot pointed at `/health/` | 99.9%+ |
| Recent errors | hPanel → Python App → error log / Passenger log | no `Traceback` |
| DB reachable | `/health/` reports DB status | ok |
| Disk / inodes | hPanel → Files → usage | < 80% |
| TLS certificate | host-managed; check expiry in hPanel | expiry > 30 days |
| Audit trail | one `AuditLog` entry shows the real client IP | real IP recorded |
| Rate limiting | login from a second client IP is not throttled | only culprit throttled |

### Error tracking (documented, not configured)

**Sentry** is the intended error tracker but is **not wired up yet**. The
drivers are in place (`redis`, SMTP email), but no `sentry-sdk` dependency,
`SENTRY_DSN` setting, or initialization exists. When enabled:

1. `pip install sentry-sdk` (pin it in `requirements.txt`).
2. In `config/settings/production.py` (or a `hostinger` settings module), call
   `sentry_sdk.init(dsn=config('SENTRY_DSN', default=''), ...)` only when the
   DSN is set, with environment name matching the deploy.
3. Set `SENTRY_DSN` in hPanel environment / `.env`.

Until then, errors are visible in the Passenger log and via the email
`ADMIN_EMAIL` if a mail backend is configured.

## 10. Limits and honest trade-offs

- **In-memory cache** (no Redis): sessions fall back to the DB; per-instance
  cache is not shared across Passenger workers. Acceptable at this scale;
  re-evaluate if traffic grows.
- **Client IP trust:** with `TRUSTED_PROXY_IPS` empty, the app uses
  `REMOTE_ADDR` — safe, but if the host exposes a fixed proxy IP, listing it in
  `TRUSTED_PROXY_IPS` restores correct client IPs for rate limiting.
- **No zero-downtime DB strategy** — `migrate` runs before restart; for
  releases that drop/rename columns, take a maintenance window (see
  `docs/deployment.md` §11).
- **RPO:** daily backup ≈ up to 24 h of loss (Hostinger shared has no WAL
  archiving). Acceptable for launch; document the RPO in the DR table.

## 11. MySQL compatibility — explicit declaration

> **This project no longer depends on PostgreSQL.** The production database is
> MySQL/MariaDB (ADR 0006, 2026-08-07). State it here so no new developer
> assumes the old VPS/Postgres stack.

Verified against `fleet/models.py`, every migration in `fleet/migrations/`, and
all query usage:

- **No Postgres-only schema features:** no `JSONField`/`JSONB`, `ArrayField`,
  `HStoreField`, `GinIndex`/`GIST`, `Unaccent`, `CheckConstraint`,
  `UniqueConstraint`, `db_table`, or custom indexes — only portable field types
  (`BigAutoField`, `CharField`, `IntegerField`, `DecimalField`, `DateField`,
  `DateTimeField`, `BooleanField`, `TextField`, `ForeignKey`, `OneToOneField`).
- **No raw SQL / `connection.cursor()`** — all data access goes through the ORM
  with portable lookups and aggregates.
- **Booking exclusivity** (`select_for_update` in `fleet/views.py`) is supported
  on MySQL/InnoDB; the same one-booking-per-vehicle-window rule holds and is
  covered by the CI suite (MySQL 8) and the preflight check.
- **Money columns** are `DecimalField` → MySQL `DECIMAL(10,2)` — safe for
  currency math.
- **Driver pin:** `requirements.txt` pins `PyMySQL>=1.2.0`. Do not downgrade to
  1.1.1 — it reports `version_info=(1,4,6)`, which fails Django's
  `mysqlclient >= 2.2.1` import gate, so the app cannot start against MySQL.

If a future change introduces a Postgres-only feature, it must be flagged in
review against this section and `docs/platform-support.md`.
