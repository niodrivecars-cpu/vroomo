# Business Patterns

General, cross-domain patterns for modeling business logic — the reusable layer
above any specific product.

## What this folder is
Patterns that recur across business domains (validation, state, pricing) and the
discipline for turning business rules into protected code. Product-specific
rules live in `domain/`; this is the "how to think about it" layer.

## The core discipline
Business rules must be protected by tests with the same strength as code:

1. Write the rule as an invariant (`domain/*/invariants.md`).
2. Turn it into a reference test (`domain/*/test-matrix.md`).
3. Enforce it in code (service layer, not scattered views).
4. Prove it under load where concurrency is involved.

See `validation-patterns.md`, `pricing-patterns.md`, `state-machines.md`.
