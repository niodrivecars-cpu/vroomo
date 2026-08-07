# Backup / Restore Runbook

Database and file continuity on the host (MySQL/MariaDB on Hostinger shared).

## Backup (`scripts/backup.sh`)
- MySQL dump + media files (`mysqldump`; the script branches on the
  `DATABASE_URL` scheme — `pg_dump` only as a legacy path).
- Take before any migration or deploy.
- Retain per a policy (start with daily + pre-deploy).

## Restore (`scripts/restore.sh`)
1. Stop writes (brief maintenance if needed).
2. Restore DB from the dump.
3. Restore media files to their location.
4. Health-check + verify a tenant's data is intact.

## Rules
- **Test restore, not just backup.** An untested restore is a rumor.
- Restore to a fresh DB first if unsure; validate before switching traffic.
- Records of backup/restore go to evidence if part of a release or incident.

## Frequency
- Pre-deploy: always.
- Scheduled: daily minimum; align with the pilot data volume.
