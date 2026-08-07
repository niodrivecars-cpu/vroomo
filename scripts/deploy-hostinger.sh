#!/usr/bin/env bash
# Deploy or upgrade Vroom on Hostinger shared hosting (Passenger).
#
# Usage:
#   scripts/deploy-hostinger.sh <APP_DIR> <ENV_FILE> [REF]
#
#   APP_DIR  absolute path to the application checkout (e.g.
#            /home/u000000000/domains/example.com/vroom)
#   ENV_FILE absolute path to the production .env file
#   REF      git ref to deploy (tag or branch). Defaults to "main".
#
# Shared-hosting constraints (no systemd / sudo / Docker): the script refreshes
# the code, installs deps into the local venv, applies migrations, and asks
# Passenger to restart via the tmp/restart.txt touch. git must be usable over
# the SSH account, and any host-provided auto-deploy (hPanel -> Git) can
# replace the git step. Prefer release tags over main.
set -euo pipefail

APP_DIR="${1:?Usage: deploy-hostinger.sh APP_DIR ENV_FILE [REF]}"
ENV_FILE="${2:?Usage: deploy-hostinger.sh APP_DIR ENV_FILE [REF]}"
REF="${3:-main}"
PREVIOUS_REF=""

cd "$APP_DIR"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: environment file not found: $ENV_FILE" >&2
    exit 1
fi
chmod 600 "$ENV_FILE"

# Only update when git is available and this is a git checkout (host auto-deploy
# already pulled the code, in which case REF is informational).
if [ -d .git ] && git rev-parse --verify -q "$REF" >/dev/null 2>&1; then
    PREVIOUS_REF=$(git rev-parse --short HEAD)
    git fetch --tags origin
    git checkout "$REF"
elif [ -d .git ]; then
    echo "WARNING: git ref '$REF' not found locally; deploying current checkout" >&2
fi
CURRENT_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "untracked")

if [ ! -d venv ]; then
    python3 -m venv venv
fi
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

echo "==> Restarting Passenger (touch tmp/restart.txt)"
mkdir -p tmp
touch tmp/restart.txt

echo "==> Probing /health/"
sleep 5
bash scripts/healthcheck.sh "$ENV_FILE" "https://${ALLOWED_HOSTS%%,*}"

echo "==> Recorded previous ref for rollback: $PREVIOUS_REF"
echo "vroom_previous_ref=$PREVIOUS_REF" > .deploy-state

echo "Deployed $CURRENT_REF (was $PREVIOUS_REF)"
