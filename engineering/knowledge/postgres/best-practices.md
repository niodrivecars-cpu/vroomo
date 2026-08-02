# Postgres — Best Practices

- **Index tenant-scoping and filter columns.** Every query scopes by company;
  composite indexes pay off fast.
- **Use real row locks for exclusivity.** Where SQLite can't prove a claim,
  Postgres `select_for_update` + a unique constraint is the production-grade
  answer (see `patterns/django-service-layer/`).
- **Prefer migrations + constraints over app-only guards.** Unique/check
  constraints are the last line of defense even if an app guard misses a path.
- **Keep dev/testing on SQLite but validate on Postgres.** Cheap, fast dev +
  truthful production checks.
- **Backup/restore discipline.** `scripts/backup.sh`, `scripts/restore.sh`;
  restore is tested, not assumed (see `knowledge/hostinger/`).
