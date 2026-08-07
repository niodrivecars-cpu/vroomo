# ADR 0006: Production deployment strategy — Hostinger shared hosting

- **Status:** Accepted
- **Date:** 2026-08-07
- **Author:** Vroom team

## Context

Vroom ships on **Hostinger Business shared hosting**. Unlike the VPS layout
previously documented (Ubuntu + PostgreSQL + Redis + gunicorn + nginx +
GitHub Actions SSH CD), shared hosting has hard constraints: no
sudo/systemd/Docker, Passenger-managed processes, no Redis, and MySQL/MariaDB
as the database. CI must mirror the production backend so the tested path is
the shipped path.

## Decision

1. **Production target:** Hostinger Business shared, running the Django app via
   **Passenger** (`passenger_wsgi.py` entry point) with **MySQL/MariaDB**
   (`PyMySQL` driver) and in-memory cache. Full guide:
   `docs/deployment/hostinger-business.md`.
2. **Database:** MySQL is the reference backend. `psycopg2-binary` is replaced
   by `PyMySQL` (+ `cryptography`) in `requirements.txt`;
   `config/__init__.py` calls `pymysql.install_as_MySQLdb()`. PostgreSQL
   remains supported by `backup.sh`/`restore.sh` (scheme-branching) but is not
   the tested production path.
3. **CI mirrors production:** the CI suite runs against a MySQL 8 service
   container (`DATABASE_URL=mysql://...`); `config.test_settings` uses
   `DATABASE_URL` when set and in-memory SQLite locally.
4. **Deploy:** hPanel Git auto-deploy + `scripts/deploy-hostinger.sh`
   (no sudo/systemd/Docker: git checkout → venv pip install → migrate →
   collectstatic → compilemessages → check --deploy → `touch tmp/restart.txt` →
   `/health/` probe).
5. **CD retirement:** `.github/workflows/cd.yml` is removed from active CI and
   preserved as a VPS reference at `docs/legacy/cd-vps-reference.yml`. GitHub
   Actions no longer builds/pushes Docker images; the `Dockerfile` stays for
   local development only.
6. **HTTPS:** TLS is host-managed; `SECURE_SSL_REDIRECT` is env-tunable
   (default `True`) because some Passenger/LiteSpeed setups do not forward
   `X-Forwarded-Proto`.
7. **Monitoring:** error tracking (Sentry) is documented but **not yet
   configured** — no dependency, DSN setting, or initialization exists. Logs are
   inspected via the hPanel Python App logs and `/health/` is the uptime
   monitor target.

## Alternatives considered

- **Keep the VPS + nginx/gunicorn layout** — rejected as the production path:
  requires a VPS or the ability to run systemd/Docker, which Hostinger shared
  does not provide; also rejected for the CI SSH-CD model.
- **mysqlclient driver** — rejected: needs a C compiler and libmysqlclient on
  the host; PyMySQL is pure-Python and installs cleanly on shared hosting.
- **Run CI on SQLite and only "smoke" MySQL** — rejected: tests must run on the
  shipped backend (this ADR supersedes the previous Postgres-CI assumption).
- **No automated deploy at all (FTP)** — rejected: Git auto-deploy + a script
  keeps releases auditable and repeatable.

## Consequences

- **Positive:** the production target is constrained to what shared hosting
  can actually run; CI exercises MySQL exactly like production; deploy is
  repeatable without sudo/systemd/Docker; VPS layout remains as a documented
  reference.
- **Negative:** no Redis (in-memory cache only); client-IP trust defaults to
  `REMOTE_ADDR` (rate limiting may key off the shared proxy unless
  `TRUSTED_PROXY_IPS` is set); no WAL archiving (daily backup ≈ 24 h RPO).
- **Trade-offs accepted:** PostgreSQL path is no longer CI-tested; Sentry is
  deferred to a later change; `cd.yml` and GHCR publishing are decommissioned.

## Evidence

`engineering/evidence/verification/hostinger-pivot-2026-08-07.json`
(supersedes `deployment-automation-2026-08-06.json`).

## Compliance

- `requirements.txt` has no `psycopg2`; `config/__init__.py` installs PyMySQL's
  MySQLdb shim; CI's service container and `DATABASE_URL` are MySQL.
- `passenger_wsgi.py` exists at the repo root; `scripts/deploy-hostinger.sh`
  runs the documented sequence; `.github/workflows/` contains no `cd.yml`.
- `docs/platform-support.md` documents the Hostinger vs VPS matrix and this
  guide's decisions.
