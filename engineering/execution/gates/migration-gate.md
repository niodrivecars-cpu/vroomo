# Migration Gate

Protects schema integrity and data continuity.

## Automated
1. `makemigrations --check --dry-run --settings=config.test_settings` → no drift.
2. Full test suite runs against a migrated test DB (migrations applied cleanly).

## Review checklist (human)
- Migration is reversible where sensible (`reverse` runs).
- No destructive operation on production data without a backup + runbook step.
- Renames/data-moves (e.g. adding `company` to existing rows in 0009) reviewed
  for correctness on real data.
- Migration files are part of the record — never edited after shipping.

## Production discipline
- Back up before applying (`scripts/backup.sh`).
- Apply via `deploy.sh`/`runbooks/deploy-runbook.md`; health-check after.

## Pass criteria
No drift, suite green, destructive steps reviewed, backup confirmed.
