# Vroom — Preflight Checklist (Go / No-Go Gate)

**Mandatory before any production deployment.** The release is **not**
production-ready until every box is checked. Nothing here is optional; an
unchecked box blocks shipping.

Status legend: `[ ]` not started · `[x]` done · `[~]` blocked (record why in
`Release Notes`).

## 0. Hostinger plan capability (the blocking gate)

> This is the **Go / No-Go gate**. The whole deployment design depends on the
> Business plan exposing a managed **Python App** (Passenger) service. Verify
> in hPanel **before** anything else.

- [ ] hPanel → Websites → Manage → the site shows a **Python App** option
- [ ] The Python App menu accepts `passenger_wsgi.py` as the entry point
- [ ] SSH / Git auto-deploy available on the plan (hPanel → Git → Auto Deploy)

**If any of the above is missing, STOP.** The current plan cannot run as
documented; revisit the hosting choice before continuing.

## 1. Environment & secrets

- [ ] `.env` exists in the app root and is `chmod 600`
- [ ] `SECRET_KEY` is a fresh long random value (not the example, not dev)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` = the real public hostname(s)
- [ ] `CSRF_TRUSTED_ORIGINS` = `https://<real hostname>`
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production` set in hPanel env
- [ ] `SECURE_SSL_REDIRECT` value decided and documented (default `True`; set
      `False` only if the proxy does not forward `X-Forwarded-Proto`)
- [ ] `TRUSTED_PROXY_IPS` value decided (empty on shared hosting unless the
      host's proxy IPs are known)
- [ ] No real secret is committed to the repository

## 2. Database

- [ ] MySQL/MariaDB database created in hPanel (name, user, password recorded)
- [ ] `DATABASE_URL=mysql://user:pass@host:3306/dbname` set and correct
- [ ] The DB user can connect from the hosting environment
- [ ] A `manage.py migrate` run on the empty DB completes with zero errors
- [ ] `manage.py check --deploy` completes with zero errors
- [ ] Migration-drift check clean: `python -m manage makemigrations --check --dry-run`

## 3. Static & media

- [ ] `STATIC_ROOT` is on a path served by the host; directory writable
- [ ] `MEDIA_ROOT` directory exists and is writable by the app process
- [ ] `collectstatic --noinput` completes and static files load over HTTPS

## 4. Runtime & restart

- [ ] Passenger serves the app from `passenger_wsgi.py`
- [ ] `tmp/restart.txt` touch restarts the app (logs show the reload)
- [ ] `GET /health/` returns HTTP 200 with `"status":"ok"` over HTTPS
- [ ] Home page loads; login page loads

## 5. HTTPS

- [ ] Host-managed TLS certificate issued for the domain
- [ ] `https://<domain>/` serves the app; plain `http://` redirects to HTTPS
- [ ] No redirect loop on HTTPS (the `SECURE_SSL_REDIRECT` check)
- [ ] Secure cookies set (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)

## 6. Security verification

- [ ] `/media/` is **not** served directly by the web server
- [ ] An `AuditLog` entry shows the real client IP (not the proxy's)
- [ ] Login rate limit keys off the real client IP (5 failed attempts throttle)
- [ ] CSRF token protects a state-changing form (create a record via the UI)

## 7. Backups & restore

- [ ] `scripts/backup.sh` runs to completion against MySQL (`mysqldump`)
- [ ] A restore was tested in a scratch environment (DB + media)
- [ ] Backup cron job scheduled in hPanel (Cron Jobs)

## 8. Data integrity (MySQL compatibility)

- [ ] Confirm no Postgres-only features are in use (see
      `docs/deployment/hostinger-business.md` §11 and the migration note in
      `docs/platform-support.md`)
- [ ] Booking exclusivity holds under `select_for_update` on MySQL/InnoDB
      (a second overlapping booking for the same vehicle is rejected)

## Release notes

| Date | Check | Result | Notes / blocker |
|---|---|---|---|
|  |  |  |  |
