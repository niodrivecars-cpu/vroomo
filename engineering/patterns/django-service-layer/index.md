# Pattern: Django Service Layer

## Why we use it
Business logic that lives in views is hard to test, duplicates across views, and
escapes the audit/isolation invariants. A service/helper layer gives rules a
testable home and a single enforcement point.

## When NOT to use it
- CRUD passthrough (form → save) — a service adds ceremony to nothing.
- When a form already owns the logic and there's exactly one caller.

## Trade-offs
- **Advantages:** testable business rules, single enforcement point, views stay
  thin.
- **Disadvantages:** an extra layer to navigate; risk of anemic services that
  just move code around.
- **Alternatives:** logic in models (fine for simple invariants, gets crowded),
  logic in forms (ties rules to HTTP), logic in views (current anti-pattern).

## Vroom examples
- `fleet/security.py` — signing, rate-limit helpers (cross-cutting, single
  implementation).
- Booking exclusivity handled via the view + retry wrapper rather than scattered
  checks (see `tests/performance/common.js`).
- Cross-cutting concerns (tenant scope, audit) centralized in helpers/middleware
  (`fleet/middleware.py`, `fleet/audit.py`).

## Common mistakes
- Service that re-implements form validation differently (two sources of truth).
- Logic still duplicated because "some is in the view, some in the service."
- Services with side effects that aren't transaction-safe.

## Required tests
- Each rule has a test at the service layer independent of HTTP.
- The same rule is not enforced differently in another path.

## Security review
Security invariants (tenant scope, authorization) are enforced in the service
layer, not re-argued per view; no bypass path skips the service.

## Performance review
Services don't add queries (N+1); batching/fetch related data once.
