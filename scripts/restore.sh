#!/usr/bin/env bash
# Restore a Vroom backup (database + media). Run with the app stopped.
#
# Usage: scripts/restore.sh <APP_DIR> <ENV_FILE> <BACKUP_PATH>
#
# Drops and recreates the database from the dump (Postgres or MySQL, selected
# by the DATABASE_URL scheme), then unpacks the media archive. Destructive —
# requires explicit confirmation unless --yes is passed.
set -euo pipefail

APP_DIR="${1:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
ENV_FILE="${2:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
BACKUP_PATH="${3:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
CONFIRM="${4:-}"

DB_DUMP="$BACKUP_PATH/vroom-db.dump"
DB_SQL="$BACKUP_PATH/vroom-db.sql"
MEDIA_TAR="$BACKUP_PATH/media.tar.gz"

if [ ! -f "$DB_DUMP" ] && [ ! -f "$DB_SQL" ]; then
    echo "ERROR: neither $DB_DUMP nor $DB_SQL found" >&2
    exit 1
fi

if [ "$CONFIRM" != "--yes" ]; then
    read -r -p "This DROPS and recreates the production database. Type 'restore' to continue: " answer
    if [ "$answer" != "restore" ]; then
        echo "Aborted."
        exit 1
    fi
fi

cd "$APP_DIR"

set -a
. "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
    DATABASE_URL="mysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST:-127.0.0.1}:${DB_PORT:-3306}/${DB_NAME}"
fi

SCHEME=${DATABASE_URL%%:*}

URL_REST=${DATABASE_URL#*://}
AUTH_HOST=${URL_REST%%/*}
CREDS=${AUTH_HOST%%@*}
DB_NAME=${URL_REST#*/}
DB_NAME=${DB_NAME%%\?*}
DB_USER=${CREDS%%:*}
DB_PASS=${CREDS#*:}
DB_HOST=${AUTH_HOST##*@}
DB_PORT=${DB_HOST##*:}
DB_HOST=${DB_HOST%:*}

case "$SCHEME" in
    mysql|mariadb)
        echo "==> Dropping and recreating database $DB_NAME"
        MYSQL_PWD="$DB_PASS" mysql \
            --host="${DB_HOST:-127.0.0.1}" --port="${DB_PORT:-3306}" --user="$DB_USER" \
            -e "DROP DATABASE IF EXISTS \`$DB_NAME\`; CREATE DATABASE \`$DB_NAME\` CHARACTER SET utf8mb4;"
        echo "==> Restoring database from dump"
        MYSQL_PWD="$DB_PASS" mysql \
            --host="${DB_HOST:-127.0.0.1}" --port="${DB_PORT:-3306}" --user="$DB_USER" "$DB_NAME" \
            < "$DB_SQL"
        ;;
    postgres|postgresql)
        echo "==> Dropping and recreating database $DB_NAME"
        sudo -u postgres psql -p "${DB_PORT:-5432}" -c "DROP DATABASE IF EXISTS \"$DB_NAME\";" >/dev/null
        sudo -u postgres psql -p "${DB_PORT:-5432}" -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";" >/dev/null
        echo "==> Restoring database from dump"
        pg_restore --no-owner --no-privileges --dbname="$DATABASE_URL" "$DB_DUMP"
        ;;
    *)
        echo "ERROR: unsupported DATABASE_URL scheme: $SCHEME" >&2
        exit 1
        ;;
esac

if [ -f "$MEDIA_TAR" ]; then
    MEDIA_ROOT=$(./venv/bin/python -c "import django,os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production'; django.setup(); from django.conf import settings; print(settings.MEDIA_ROOT)")
    echo "==> Restoring media into $MEDIA_ROOT"
    mkdir -p "$(dirname "$MEDIA_ROOT")"
    tar -xzf "$MEDIA_TAR" -C "$(dirname "$MEDIA_ROOT")"
fi

echo "Restore complete: $BACKUP_PATH"
echo "Now run: scripts/deploy.sh (or deploy-hostinger.sh) and restart the app."
