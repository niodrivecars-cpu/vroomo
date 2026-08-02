# Pattern: Domain Events

## Why we use it
When a state change should trigger side effects that don't belong in the
command path (notifications, sync, derived aggregates) without coupling the
caller to them.

## When NOT to use it
- When side effects are few, synchronous, and already fine inline — events add a
  bus, ordering rules, and failure handling for no benefit. Vroom does not use
  domain events.
- When "event" really means "call another function."

## Trade-offs
- **Advantages:** loose coupling, extensibility (new subscribers without
  touching the source).
- **Disadvantages:** out-of-order processing, failure/retry handling, harder to
  trace causality.
- **Alternatives:** plain function calls, signal-based hooks (Django signals),
  transactional outbox for real async.

## Vroom examples
None — audit logging is synchronous via `fleet/audit.py`; the audit use case is
simpler than events. Revisit when real async requirements exist.

## Common mistakes
- In-process events pretending to be async (ordering surprises).
- Not handling subscriber failure (partially applied side effects).
- Publishing events outside the transaction that produced them.

## Required tests
- Side effects fire exactly once on the state change (idempotency).
- Subscriber failure does not corrupt the source transaction.

## Security review
Event payloads respect tenant scope; subscribers cannot bypass authorization.

## Performance review
Synchronous subscribers add latency — measure; consider async + outbox when it
matters.
