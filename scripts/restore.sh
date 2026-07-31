#!/usr/bin/env bash
# Restore a Vroom backup (database + media). Run with the app stopped.
#
# Usage: scripts/restore.sh <APP_DIR> <ENV_FILE> <BACKUP_PATH>
#
# Drops and recreates the database from the dump, then unpacks the media
# archive. Destructive — requires explicit confirmation unless --yes is passed.
set -euo pipefail

APP_DIR="${1:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
ENV_FILE="${2:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
BACKUP_PATH="${3:?Usage: restore.sh APP_DIR ENV_FILE BACKUP_PATH [--yes]}"
CONFIRM="${4:-}"

DB_DUMP="$BACKUP_PATH/vroom-db.dump"
MEDIA_TAR="$BACKUP_PATH/media.tar.gz"

if [ ! -f "$DB_DUMP" ]; then
    echo "ERROR: $DB_DUMP not found" >&2
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
    DATABASE_URL="postgres://${DB_USER}:${DB_PASSWORD}@${DB_HOST:-127.0.0.1}:${DB_PORT:-5432}/${DB_NAME}"
fi

# postgres://user:pass@host:port/dbname
PG_HOST=$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgres://[^@]*@([^:/]+).*#\1#')
PG_PORT=$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgres://[^@]*@[^:/]+:([0-9]+)/.*#\1#')
PG_DB=$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgres://[^@]*@[^/]+/([^?]*).*#\1#')
PG_USER=$(printf '%s' "$DATABASE_URL" | sed -E 's#^postgres://([^:]+):.*#\1#')

echo "==> Dropping and recreating database $PG_DB"
sudo -u postgres psql -p "${PG_PORT:-5432}" -c "DROP DATABASE IF EXISTS \"$PG_DB\";" >/dev/null
sudo -u postgres psql -p "${PG_PORT:-5432}" -c "CREATE DATABASE \"$PG_DB\" OWNER \"$PG_USER\";" >/dev/null

echo "==> Restoring database from dump"
pg_restore --no-owner --no-privileges --dbname="$DATABASE_URL" "$DB_DUMP"

if [ -f "$MEDIA_TAR" ]; then
    echo "==> Restoring media"
    tar -xzf "$MEDIA_TAR" -C /opt/vroom
fi

echo "Restore complete: $BACKUP_PATH"
echo "Now run: scripts/deploy.sh $APP_DIR $ENV_FILE (or rollback) and restart the service."
