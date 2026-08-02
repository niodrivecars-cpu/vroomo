# Validation Patterns

How to validate business input without scattering rules.

## Layered validation
1. **Syntactic** (form field types, formats) — at the form boundary.
2. **Semantic** (business meaning: overlap, ownership, state) — in the service
   layer where it can be tested in isolation.
3. **Integrity** (constraints, uniqueness) — at the DB, as the last line of
   defense.

## Rules
- Validate at ONE owning layer per rule; don't re-validate differently in views.
- Render errors visibly (error markup) so load tests can distinguish real
  validation from swallowed errors.
- Keep validation testable: a pure function/service that returns structured
  errors beats assertions buried in a view.
- Concurrency-sensitive validation (e.g. booking overlap) needs DB/constraint
  backup + a load proof, not just a pre-check.

## Vroom example
Booking exclusivity: semantic check (window overlap) + load-proven guard
(`same_vehicle_booking_success == 1`). Cross-tenant access is a validation rule
enforced structurally (ADR 0002/0005, `patterns/multi-tenant/`).
