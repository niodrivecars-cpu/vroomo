# Deploy Runbook

Deploy Vroom to the Hostinger VPS. See `docs/deployment.md` for full notes.

## Prereqs
- `scripts/deploy.sh` available; SSH access to the VPS.
- `.env.production` populated (secrets not in repo).
- `TRUSTED_PROXY_IPS=127.0.0.1` set (ADR 0003).
- Backup taken (`scripts/backup.sh`).

## Steps
1. `git checkout <release-tag>` (the gate-passing commit).
2. `scripts/deploy.sh` — pulls, installs deps, migrates, collects static,
   restarts gunicorn.
3. `scripts/healthcheck.sh` — health endpoint returns 200.
4. Spot-check: login, a booking, a signed download.

## Post-deploy
- Verify client IP resolution behind nginx (audit/rate limit still correct).
- Verify no `DEBUG`, correct headers.

## Rollback
If the deploy is broken:
1. `scripts/rollback.sh` — reverts to the previous release.
2. Health-check again.
3. Record what broke for the next release.

## Migrations
Destructive migrations: back up first, review the migration gate, apply
carefully. `scripts/restore.sh` is the escape hatch (test it before you need it).
