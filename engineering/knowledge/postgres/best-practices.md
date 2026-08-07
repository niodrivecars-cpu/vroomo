# Postgres — Best Practices

> **Legacy (2026-08-07).** Production DB is now **MySQL 8** (ADR 0006). The
> principles below are backend-agnostic and still apply; swap "Postgres" for
> "MySQL" in practice (see `knowledge/mysql/overview.md`).

- **Index tenant-scoping and filter columns.** Every query scopes by company;
  composite indexes pay off fast.
- **Use real row locks for exclusivity.** Where SQLite can't prove a claim,
  MySQL `select_for_update` (InnoDB) + a unique constraint is the
  production-grade answer (see `patterns/django-service-layer/`).
- **Prefer migrations + constraints over app-only guards.** Unique/check
  constraints are the last line of defense even if an app guard misses a path.
- **Keep dev/testing on SQLite but validate on the production backend.** Cheap,
  fast dev + truthful production checks (CI runs MySQL 8).
- **Backup/restore discipline.** `scripts/backup.sh`, `scripts/restore.sh`;
  restore is tested, not assumed (see `knowledge/hostinger/`).
