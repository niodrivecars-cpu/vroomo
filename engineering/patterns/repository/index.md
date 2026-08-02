# Pattern: Repository

## Why we use it
To isolate data access behind an interface so domain logic doesn't know about
the ORM, enabling testability and swapping storage.

## When NOT to use it
- Small/medium Django apps where the ORM's queryset API is already the access
  layer and tests use the DB directly — wrapping it adds indirection with no
  benefit. Vroom does not use a repository layer.
- When it would only pass through querysets (an anemic repository).

## Trade-offs
- **Advantages:** storage-agnostic domain, easy mocking.
- **Disadvantages:** a layer that can hide ORM power (joins, prefetch), and
  leaks when it tries to expose everything.
- **Alternatives:** service layer using the ORM directly (Vroom's choice), or
  thin queryset managers as the "repository."

## Vroom examples
None — the service/helper layer (`fleet/security.py`, views) uses the ORM
directly. Documented so future decisions are deliberate.

## Common mistakes
- Repository that exposes raw querysets (no abstraction gain).
- Fetch-then-filter that kills efficiency.
- Ignoring tenant scope inside repository helpers.

## Required tests
- Data-access behavior (scoping, ordering) tested once, not per caller.

## Security review
If a repository exists, tenant scoping lives inside it, never in callers.

## Performance review
No accidental N+1; repository methods prefetch what the use-case needs.
