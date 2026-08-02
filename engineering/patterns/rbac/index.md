# Pattern: RBAC (Role-Based Access Control)

## Why we use it
When actions must be permitted per role (admin vs operator vs viewer), not just
per login.

## When NOT to use it
- When authentication alone is the real gate (small team, single role per
  tenant) — Vroom currently uses session-level auth with per-tenant isolation and
  does not need full RBAC. Adding RBAC before roles exist is speculative
  complexity.
- When permissions are per-instance (e.g. "can edit THIS vehicle") — attribute
 -based access fits better.

## Trade-offs
- **Advantages:** centralized permission model, auditable grants.
- **Disadvantages:** mapping surface, "permission explosion," and the classic
  mistake of checking role at call sites instead of centralizing.
- **Alternatives:** attribute-based access control, policy engine.

## Vroom examples
None yet — this is a reference pattern for when roles are introduced. The
session-auth + tenant-isolation model is the current posture.

## Common mistakes
- Role checks sprinkled across views (inconsistent, easy to miss one).
- Role named in code but stored as a string with no enum/constraint.
- Confusing "authenticated" with "authorized."

## Required tests
- Each role: allowed actions succeed, denied actions return 403.
- A role change takes effect (no stale cached permissions).

## Security review
Every sensitive view has an explicit permission check; default is deny;
permission grants are audited.

## Performance review
Permission lookups are cached per request/session; no per-row role queries.
