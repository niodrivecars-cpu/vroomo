# Pattern: Soft Delete

## Why we use it
To keep history or allow accidental-delete recovery by marking rows deleted
instead of removing them.

## When NOT to use it
- When hard delete is fine (no audit/restore requirement) — soft delete poisons
  every query with a "where deleted is null" clause and uniqueness constraints.
- When a dedicated audit/archive table gives the same history without polluting
  live tables. Vroom keeps audit history in `AuditLog` and does not soft-delete
  core entities by default.

## Trade-offs
- **Advantages:** recoverability, history, no FK breakage.
- **Disadvantages:** every query must filter deleted rows (easy to forget →
  ghosts in listings), unique constraints get complicated, indexes grow.
- **Alternatives:** hard delete + audit log, archive table, deleted-at only for
  entities that genuinely need it.

## Vroom examples
None for core entities; `AuditLog` captures action history instead. Consider
soft delete only where a specific business need (e.g. invoice restore) appears.

## Common mistakes
- Forgetting the filter in one query.
- Unique index breaking on re-created deleted rows.
- Counting deleted rows in aggregates.

## Required tests
- Soft-deleted rows invisible in lists/queries; restore path tested; unique
  re-create tested.

## Security review
Soft-deleted data remains accessible via audit/admin — ensure tenant scoping
still applies to deleted data access.

## Performance review
The deleted-filter must be indexed; a soft-deleted table that grows unboundedly
needs a retention policy.
