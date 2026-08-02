# Vroom — Production Deployment Guide

Targets Release 1.0 RC1. This guide covers a single-server deployment on
Ubuntu 24.04 LTS with PostgreSQL 16+, Redis 7+, Gunicorn, and nginx as a
TLS-terminating reverse proxy.

## Reference architecture

```
Internet
   │  HTTPS (443)
   ▼
nginx (TLS, static files, proxy / to gunicorn)
   │  HTTP (127.0.0.1:8000)
   ▼
gunicorn (4 workers, config.wsgi)
   │
   ├─── PostgreSQL 16+  (DATABASE_URL)
   └─── Redis 7+        (CACHE_URL, sessions optional)
```

`/health/` is public and returns HTTP 200 only when the database and cache are
both reachable; point your uptime monitor and load balancer at it.

## Prerequisites on the server

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip \
  postgresql postgresql-contrib redis-server nginx gettext libmagic1
```

- `gettext` is required for `manage.py compilemessages` (localization catalogs).
- `libmagic` is required by `python-magic` (document MIME detection).
- The deploy runs as a dedicated unprivileged user, e.g. `vroom`.

## Project layout on the server

```
/opt/vroom/
├── vroom/            # application code (git checkout, release tags)
├── .env              # production secrets (chmod 600, root-owned or vroom-owned)
├── staticfiles/      # collectstatic output (owned by vroom, served by nginx)
├── media/            # private user uploads (owned by vroom; NOT served by nginx)
└── logs/             # optional LOG_DIR for the rotating vroom.log
```

## 1. Create the database and Redis

```bash
sudo -u postgres createuser --pwprompt vroom
sudo -u postgres createdb -O vroom vroom
# Optional, enables bytea/hstore extensions if ever needed:
# sudo -u postgres psql -d vroom -c "CREATE EXTENSION IF NOT EXISTS hstore;"
```

Redis runs on localhost by default (bind 127.0.0.1). If it listens on a
non-default port, adjust `CACHE_URL` accordingly.

## 2. Deploy the code

Two options:

- **Fresh install:** `sudo -u vroom bash scripts/deploy.sh /opt/vroom/vroom /opt/vroom/.env`
- **Upgrade to a release tag:** `sudo -u vroom bash scripts/deploy.sh /opt/vroom/vroom /opt/vroom/.env v1.0-rc1`

`deploy.sh` performs, with the service stopped:
1. `git fetch` + `git checkout <tag-or-branch>` (defaults to `main`)
2. recreate/refresh the virtualenv and `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput`
5. `python manage.py compilemessages`
6. `python manage.py check --deploy`
7. restart gunicorn and run the `/health/` probe

## 3. gunicorn (systemd)

`/etc/systemd/system/vroom.service`:

```ini
[Unit]
Description=Vroom Gunicorn
After=network.target postgresql.service redis-server.service

[Service]
User=vroom
Group=vroom
WorkingDirectory=/opt/vroom/vroom
EnvironmentFile=/opt/vroom/.env
ExecStart=/opt/vroom/vroom/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Tune `--workers` to `(2 × CPU cores) + 1`. Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vroom
```

## 4. nginx

`/etc/nginx/sites-available/vroom`:

```nginx
server {
    listen 80;
    server_name vroom.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vroom.example.com;

    ssl_certificate     /etc/letsencrypt/live/vroom.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vroom.example.com/privkey.pem;

    # Enables SECURE_PROXY_SSL_HEADER -> SECURE_SSL_REDIRECT / secure cookies.
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header Host $host;

    location /static/ {
        alias /opt/vroom/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
    }
}
```

Enable and get a certificate:

```bash
sudo ln -s /etc/nginx/sites-available/vroom /etc/nginx/sites-enabled/
sudo nginx -t
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d vroom.example.com   # enables HTTPS + auto-renewal
sudo systemctl reload nginx
```

### 4.1 Client IP trust (rate limiting & audit logging)

Gunicorn binds to `127.0.0.1:8000`, so Django sees `REMOTE_ADDR = 127.0.0.1` for
every request. The app resolves the real client address in
`fleet/security.py:get_client_ip()`, which is used by **both** django-ratelimit
(every `ip` / `user_or_ip` key via `RATELIMIT_IP_META_KEY`) and the audit log
(`AuditLog.ip_address`).

The resolver only trusts forwarding headers from peers listed in
`X_FORWARDED_TRUSTED_PROXIES` (env `TRUSTED_PROXY_IPS`). For those peers it
walks `X-Forwarded-For` right-to-left (closest hop first) and returns the
rightmost address that is not itself a trusted proxy. Because the `location /`
block above appends the client address with
`proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`, any
client-supplied `X-Forwarded-For` values are always left of the appended
address and can never win the walk — client-supplied forwarding headers are
never trusted directly. Requests from any other peer use `REMOTE_ADDR` and
forwarded data is ignored.

```bash
# .env — required in the documented nginx + gunicorn-on-127.0.0.1 layout
TRUSTED_PROXY_IPS=127.0.0.1
```

Verify after deploy: an entry in `AuditLog` shows the real client IP (not
`127.0.0.1`), and the login IP rate limit keys off the real address (5 failed
attempts from one client IP, then another client IP is not throttled).

## 5. Environment file

Copy `.env.production.example` to `/opt/vroom/.env`, fill in real values, then:

```bash
sudo chown vroom:vroom /opt/vroom/.env
sudo chmod 600 /opt/vroom/.env
```

Required keys: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `DATABASE_URL` (or `DB_*`), `CACHE_URL`,
`TRUSTED_PROXY_IPS=127.0.0.1`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`,
`ADMIN_EMAIL`.

## 6. Post-deploy verification

```bash
curl -fsS http://127.0.0.1:8000/health/   # {"status":"ok", ...}
curl -fsS https://vroom.example.com/health/
sudo -u vroom /opt/vroom/vroom/venv/bin/python -m manage check --deploy
```

The `check --deploy` step is also re-run automatically by `deploy.sh`.

## 7. Document downloads

Document files are **private** — nginx never serves `/media/`, so nothing is
reachable by guessing a URL. All downloads go through the application:

- `fleet:document_download` (`/fleet/documents/<pk>/download/`) serves a document
  to an authenticated staff member, scoped to their company.
- `fleet:document_download_signed` (`/fleet/documents/<pk>/download/?token=...`)
  serves a document to anyone holding a valid signed token (no login required).

Signed tokens expire (default `DOCUMENT_SIGNED_URL_TTL`, 86400 s / 24 h), are
bound to a per-document revocation version, and are invalidated by
"Revoke temporary links" in the admin. Both endpoints are rate-limited
(`download_per_user` / `download_anon_ip` in `SECURITY_RATE_LIMITS`), and every
attempt — allowed or denied — is written to `AuditLog`. Physical files are
removed from storage on replace and on delete.

## 8. Backups

`scripts/backup.sh /opt/vroom/vroom /opt/vroom/.env /srv/backups/vroom`:

- `pg_dump` of the database (compressed, timestamped)
- tar of the `media/` directory
- prunes backups older than 14 days
- returns the backup directory path

Schedule with cron:

```cron
0 3 * * *  /opt/vroom/vroom/scripts/backup.sh /opt/vroom/vroom /opt/vroom/.env /srv/backups/vroom >> /var/log/vroom-backup.log 2>&1
```

Test restores regularly in a scratch environment — an untested backup is a hope.

## 9. Rollback

Two cases:

- **Application-only regression:** `scripts/rollback.sh /opt/vroom/vroom /opt/vroom/.env` re-checks out the previously deployed release tag (recorded by `deploy.sh`), reinstalls deps, restarts gunicorn, and probes `/health/`. Database schema is unchanged.
- **Database/data disaster:** restore from backup, then redeploy the matching release:

```bash
bash scripts/restore.sh /opt/vroom/vroom /opt/vroom/.env /srv/backups/vroom/backup-YYYY-MM-DD_HHMMSS
```

`restore.sh` drops and recreates the database from the dump and unpacks the
media archive. It must run with the application stopped.

## 10. Security notes

- `SECRET_KEY` must be unique per environment and never committed.
- `DEBUG` is forced `False` by `config/settings/production.py`, which also
  validates `SECRET_KEY` and `ALLOWED_HOSTS` at startup.
- HTTPS-only: HSTS (1 year, subdomains, preload), secure cookies, TLS redirect
  via `SECURE_PROXY_SSL_HEADER` (nginx sets `X-Forwarded-Proto`).
- Report-only CSP, `X-Frame-Options: DENY`, and `nosniff` are emitted by
  `fleet.middleware.SecurityHeadersMiddleware`.
- All logins, password resets, and uploads are rate-limited
  (`settings.SECURITY_RATE_LIMITS`).
- The firewall should expose only ports 22, 80, 443. PostgreSQL and Redis must
  bind to 127.0.0.1 only.
