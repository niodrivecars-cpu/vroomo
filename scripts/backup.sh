#!/usr/bin/env bash
# Backup the Vroom database and media files.
#
# Usage: scripts/backup.sh <APP_DIR> <ENV_FILE> <BACKUP_DIR>
#
# Creates a timestamped directory containing:
#   vroom-db.dump        pg_dump, custom format
#   media.tar.gz         media/ directory archive
# Prints the backup path and prunes backups older than 14 days.
set -euo pipefail

APP_DIR="${1:?Usage: backup.sh APP_DIR ENV_FILE BACKUP_DIR}"
ENV_FILE="${2:?Usage: backup.sh APP_DIR ENV_FILE BACKUP_DIR}"
BACKUP_DIR="${3:?Usage: backup.sh APP_DIR ENV_FILE BACKUP_DIR}"

cd "$APP_DIR"

set -a
. "$ENV_FILE"
set +a

if [ -z "${DATABASE_URL:-}" ]; then
    DATABASE_URL="postgres://${DB_USER}:${DB_PASSWORD}@${DB_HOST:-127.0.0.1}:${DB_PORT:-5432}/${DB_NAME}"
fi

STAMP=$(date +%Y-%m-%d_%H%M%S)
DEST="$BACKUP_DIR/$STAMP"
mkdir -p "$DEST"

echo "==> Dumping database"
pg_dump --format=custom --no-owner --dbname="$DATABASE_URL" > "$DEST/vroom-db.dump"

MEDIA_ROOT=$(./venv/bin/python -c "import django,os; os.environ['DJANGO_SETTINGS_MODULE']='config.settings.production'; django.setup(); from django.conf import settings; print(settings.MEDIA_ROOT)")
echo "==> Archiving media from $MEDIA_ROOT"
tar -czf "$DEST/media.tar.gz" -C "$(dirname "$MEDIA_ROOT")" "$(basename "$MEDIA_ROOT")"

echo "==> Pruning backups older than 14 days"
find "$BACKUP_DIR" -maxdepth 1 -type d -name '20*' -mtime +14 -exec rm -rf {} +

echo "Backup complete: $DEST"
