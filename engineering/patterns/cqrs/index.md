# Pattern: CQRS (Command Query Responsibility Segregation)

## Why we use it
When reads and writes diverge sharply in shape or scale — e.g. rich write model
plus denormalized read views, or reads far outnumber writes.

## When NOT to use it
**Default: don't.** Vroom does not use CQRS. It adds a read model, eventual
consistency, and infrastructure for a problem the app doesn't have. Revisit only
if real load data shows reads/writes diverging badly.

## Trade-offs
- **Advantages:** optimized reads, write model stays clean.
- **Disadvantages:** eventual consistency, duplication of state, extra
  infrastructure, debugging harder.
- **Alternatives:** read-optimized queries/indexes, caching (Redis), materialized
  views.

## Vroom examples
None — documented as an avoid-until-needed pattern. See `platform/ROADMAP.md`
(observability phase) for the data that would justify revisiting.

## Common mistakes
- Adopting CQRS before measuring.
- Read model drifting from write model (consistency bugs).
- Adding a message bus just for CQRS's sake.

## Required tests
- Read model reflects writes within the agreed consistency window.
- Write paths still enforce invariants (CQRS never relaxes them).

## Security review
Read model must respect the same tenant isolation; no read-side leaks.

## Performance review
CQRS is justified by measured read/write divergence — document the numbers that
trigger adoption.
