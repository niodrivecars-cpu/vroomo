# 06 — Troubleshooting

Common failure modes after the GitHub/Hostinger setup. Each entry: symptom →
likely cause → fix.

## CI failures

| Symptom | Cause | Fix |
|---|---|---|
| `test` job red at the MySQL service step | MySQL container not ready / port clash | Re-run; if persistent, check the service `options` health-cmd and available runners |
| `ruff` fails | Style/lint violation | `ruff check . --fix`, then re-push |
| `bandit` fails | Security finding | Fix in a branch, not on the protected branch |
| `pip-audit` fails | Known vulnerable pin | Bump the package + pin, verify, commit |
| `makemigrations --check` reports drift | Missing/new migration | `manage.py makemigrations`, review, include in the PR |
| `compilemessages` fails | Broken `.po` or missing locale | Fix catalog; test suite covers `.po` ↔ `.mo` sync |
| Tests fail on **MySQL** but pass on SQLite | DB-specific behavior (locking, decimals, strings) | Investigate in CI; the MySQL run is the real gate |
| `check --deploy` errors | Production-settings misconfig | Fix env in the workflow step, not the app |

## Database connection failures

- **"Can't connect to MySQL server"** — wrong `DATABASE_URL` host/port; on shared
  hosting use the hPanel-provided host (`127.0.0.1` or `localhost`), not a
  public hostname.
- **`mysqlclient 2.2.1 or newer is required`** — PyMySQL downgraded below 1.2.0.
  Restore the pin (`PyMySQL==1.2.0`); 1.1.1 fails Django's import gate
  (`CHANGELOG.md`, release checklist).
- **Access denied for user** — wrong DB user/password in env; re-check hPanel.
- **Unknown database** — DB not created in hPanel, or name mismatch in
  `DATABASE_URL`.

## Passenger problems

- **503 / app not starting** — check the Passenger log (hPanel → Python App →
  error log). Common: missing env vars, missing `.env`, wrong entry point.
- **No module named 'config'** — the app root or `PYTHONPATH` is wrong; the
  Python App directory must contain `passenger_wsgi.py`.
- **Stale code after deploy** — auto-deploy may lag; re-run
  `scripts/deploy-hostinger.sh` and `touch tmp/restart.txt`.
- **Worker crashes on restart** — a migration or env change broke startup;
  check the log, roll back the env change first (not the code).

## `collectstatic` errors

- **Permission denied on `STATIC_ROOT`** — the app process can't write the
  static dir; create it and chmod writable, or point `STATIC_ROOT` at a served
  writable path.
- **404 on static files after deploy** — `collectstatic` ran into a different
  `STATIC_ROOT` than the web server serves; align the paths.

## Migration errors

- **Migration applied but columns missing** — a `migrate` run failed partway
  (shared hosting, no WAL); restore from backup, re-run `migrate` in a
  maintenance window.
- **`django.db.migrations.exceptions.InconsistentMigrationHistory`** — the DB
  drifted from the migration files; reconcile or restore.
- **Always**: take a backup before any `migrate`; test restore first
  (`docs/deployment/hostinger-business.md` §7).

## Missing environment variables

- **`SECRET_KEY` errors** — not set or placeholder; set a fresh random value in
  hPanel env or `.env` (600 perms).
- **`ALLOWED_HOSTS` / CSRF origin errors** (403, Invalid HTTP_HOST) — the
  hostname isn't in `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`.
- **Emails not sending** — `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` wrong or
  app password needed for Gmail.

## HTTPS / redirect issues

- **Redirect loop on HTTPS** — `SECURE_SSL_REDIRECT=True` with a proxy that
  doesn't forward `X-Forwarded-Proto`; set it `False` and let the host-level
  redirect handle it (documented in `hostinger-business.md` §2).
- **Mixed content (HTTP assets on HTTPS page)** — cache/static served over
  HTTP; ensure all URLs are scheme-relative or HTTPS.

## Upload / download failures

- **Upload fails with 413/400** — host upload size limits; check hPanel PHP/app
  limits and the app's rate limits.
- **Download link expired/tampered** — signed URLs are expiry-gated by design
  (ADR 0002); generate a fresh link.
- **`/media/` is served directly** — web server must NOT serve `MEDIA_ROOT`;
  downloads go through the app (security check in
  `docs/deployment/post-deploy-validation.md`).

## First-deploy blockers (known, before RC2)

- hPanel **Python App** option missing on the plan → stop; the Hostinger path
  doesn't apply (preflight §0).
- No `origin` / no push yet → see `01-create-repository.md`.
- MySQL CI run never executed → it only runs after the first push to
  `release/1.0`; until then treat "CI green on MySQL" as unverified
  (`CHANGELOG.md` rc2 note).
