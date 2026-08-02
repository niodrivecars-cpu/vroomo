# Hostinger Knowledge

Deployment environment specifics for Vroom's VPS.

## Layout
- nginx on `127.0.0.1` proxying to gunicorn (same host). `TRUSTED_PROXY_IPS=127.0.0.1`
  must be set so client IPs resolve correctly (ADR 0003).
- Python 3 + venv; app served by gunicorn; static via collectstatic.
- Postgres 16 (docker compose or host install).

## Operations
- Deploy: `scripts/deploy.sh`; rollback: `scripts/rollback.sh`.
- Backup: `scripts/backup.sh`; restore: `scripts/restore.sh`.
- Health: `scripts/healthcheck.sh`.
- Deployment notes: `docs/deployment.md`.

## Where it's heading
Production observability (Sentry, logging) — see `platform/ROADMAP.md`.
