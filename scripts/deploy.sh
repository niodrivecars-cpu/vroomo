#!/usr/bin/env bash
# Deploy or upgrade Vroom to a git ref, then restart the service.
#
# Usage:
#   scripts/deploy.sh <APP_DIR> <ENV_FILE> [REF]
#
#   APP_DIR  absolute path to the application checkout (e.g. /opt/vroom/vroom)
#   ENV_FILE absolute path to the production .env file
#   REF      git ref to deploy (tag or branch). Defaults to "main".
#
# Prereqs: run as the deploy user; systemd service named "vroom".
set -euo pipefail

APP_DIR="${1:?Usage: deploy.sh APP_DIR ENV_FILE [REF]}"
ENV_FILE="${2:?Usage: deploy.sh APP_DIR ENV_FILE [REF]}"
REF="${3:-main}"
SERVICE="vroom"
PREVIOUS_REF=""

cd "$APP_DIR"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: environment file not found: $ENV_FILE" >&2
    exit 1
fi
chmod 600 "$ENV_FILE"

git fetch --tags origin

if git rev-parse --verify -q "$REF" >/dev/null 2>&1 || git rev-parse --verify -q "refs/remotes/origin/$REF" >/dev/null 2>&1; then
    PREVIOUS_REF=$(git rev-parse --short HEAD)
    git checkout "$REF"
else
    echo "ERROR: git ref '$REF' not found" >&2
    exit 1
fi
CURRENT_REF=$(git rev-parse --short HEAD)

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

run_manage() {
    set -a
    . "$ENV_FILE"
    set +a
    ./venv/bin/python manage.py "$@"
}

echo "==> Running migrations"
run_manage migrate --noinput

echo "==> Collecting static files"
run_manage collectstatic --noinput

echo "==> Compiling translation catalogs"
run_manage compilemessages --ignore venv

echo "==> Running production checks"
run_manage check --deploy

echo "==> Reloading $SERVICE (graceful, zero-downtime)"
if sudo systemctl is-active --quiet "$SERVICE"; then
    # HUP (ExecReload) lets gunicorn finish in-flight requests before respawning
    # workers. Falls back to a full restart if the unit has no ExecReload.
    if ! sudo systemctl reload "$SERVICE"; then
        echo "==> Reload unsupported; falling back to restart"
        sudo systemctl restart "$SERVICE"
    fi
else
    echo "==> Service inactive; starting"
    sudo systemctl restart "$SERVICE"
fi
sudo systemctl --no-pager --lines=20 status "$SERVICE"

echo "==> Probing /health/"
sleep 3
bash scripts/healthcheck.sh "$ENV_FILE"

echo "==> Recorded previous ref for rollback: $PREVIOUS_REF"
echo "vroom_previous_ref=$PREVIOUS_REF" > .deploy-state

echo "Deployed $CURRENT_REF (was $PREVIOUS_REF)"
