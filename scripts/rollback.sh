#!/usr/bin/env bash
# Roll back the application code to the previously deployed ref.
#
# Usage: scripts/rollback.sh <APP_DIR> <ENV_FILE>
#
# Application-only rollback: checks out the previous git ref recorded by
# deploy.sh, reinstalls dependencies, and restarts the service. It does NOT
# reverse database migrations — see docs/deployment.md for data disasters.
set -euo pipefail

APP_DIR="${1:?Usage: rollback.sh APP_DIR ENV_FILE}"
ENV_FILE="${2:?Usage: rollback.sh APP_DIR ENV_FILE}"
SERVICE="vroom"

cd "$APP_DIR"

if [ ! -f .deploy-state ]; then
    echo "ERROR: no .deploy-state found; cannot determine previous ref" >&2
    exit 1
fi

PREVIOUS_REF=$(sed -n 's/^vroom_previous_ref=//p' .deploy-state)
if [ -z "$PREVIOUS_REF" ]; then
    echo "ERROR: previous ref not recorded in .deploy-state" >&2
    exit 1
fi

echo "==> Rolling back to $PREVIOUS_REF"
git checkout "$PREVIOUS_REF"

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

set -a
. "$ENV_FILE"
set +a

./venv/bin/python manage.py collectstatic --noinput
./venv/bin/python manage.py check --deploy

echo "==> Restarting $SERVICE"
sudo systemctl restart "$SERVICE"

echo "==> Probing /health/"
sleep 3
bash scripts/healthcheck.sh "$ENV_FILE"

echo "Rolled back to $PREVIOUS_REF"
