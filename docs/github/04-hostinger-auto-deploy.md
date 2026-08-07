# 04 — Hostinger Auto-Deploy

From a connected GitHub repo to the first live deploy. This is the operational
half of ADR 0006 + ADR 0007: GitHub drives the deploy; Hostinger runs it.

> **Blocking precondition:** the Business plan must expose a **Python App**
> option in hPanel. Verify this *before* wiring auto-deploy. If the menu item
> is missing, this guide and the whole Hostinger path do not apply.

## 1. Connect the repository

hPanel → the site → **Websites → Manage → Git** (or **Deployment → Git**):

1. Add a new deployment.
2. Authorize GitHub and select the `vroomo` repository.
3. Set the target directory to the app root (the folder Passenger will serve,
   e.g. `public_html/vroom` or a subfolder of the domain root).
4. Choose **Auto Deploy** and select the branch `release/1.0`.

The repo is now cloned to the host. Auto-deploy pulls on every push to the
selected branch.

## 2. Choose the branch and path

- **Branch:** `release/1.0` (the release track; tags derive from it).
- **App root:** the directory where `passenger_wsgi.py` lives. Record the
  absolute path — you need it for every manual step below and for cron.

## 3. Create the MySQL database

hPanel → **Databases → MySQL Databases** → Create New Database:

- Name, user, password — record all three.
- Host: `127.0.0.1` or `localhost` (as shown by hPanel).

## 4. Set environment variables

hPanel → the site → **Manage → Python App** (or the site's environment
settings) — set:

| Variable | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | a fresh long random value |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | the real public hostname(s) |
| `CSRF_TRUSTED_ORIGINS` | `https://<real hostname>` |
| `DATABASE_URL` | `mysql://<user>:<pass>@<host>:3306/<dbname>` |
| `SECURE_SSL_REDIRECT` | `True` (set `False` only on a redirect loop) |
| `TRUSTED_PROXY_IPS` | empty on shared hosting (uses `REMOTE_ADDR`) |

Equivalent keys can also go in a `.env` file in the app root
(`config.settings` reads both via `python-decouple`).

## 5. Create the Python App (Passenger)

hPanel → **Websites → Manage → Python App**:

- App directory = the app root from step 1.
- Entry point = `passenger_wsgi.py`.
- Python version = one supported by the project (3.12 preferred).

## 6. Run the first deploy

The cleanest path is the deploy script, run over SSH or via the hPanel
terminal:

```bash
bash scripts/deploy-hostinger.sh /path/to/app /path/to/.env release/1.0
```

`deploy-hostinger.sh` (no sudo/systemd/Docker):
git checkout → venv → `pip install -r requirements.txt` → `migrate` →
`collectstatic` → `compilemessages` → `check --deploy` →
`touch tmp/restart.txt` (Passenger reload) → HTTPS `/health/` probe.

If the host auto-deployed the pull already, run the script anyway — it performs
the build steps against the already-pulled code.

## 7. Verify `/health/`

```bash
curl -fsS https://<your-domain>/health/
# -> {"status":"ok", "database": ...}  HTTP 200
```

Also confirm:
- Home page loads over HTTPS.
- Login page loads.
- An `AuditLog` row shows the real client IP.

## 8. Schedule backups

hPanel → **Cron Jobs**:

```cron
0 3 * * * /path/to/app/scripts/backup.sh /path/to/app /path/to/.env /path/to/backups >> /path/to/backups/backup.log 2>&1
```

Next: `05-first-release.md`. Before that, run the preflight checklist
(`docs/deployment/preflight-checklist.md`) — it is the Go/No-Go gate.
