# Pattern: Audit Logging

## Why we use it
Security-relevant actions (login, download, admin operations) must be
reconstructable. Audit answers "who did what, when, from where, on which tenant."

## When NOT to use it
- High-frequency non-sensitive operations (page views, health checks) — log
  noise buries real signals.
- When a simple `created_at`/`updated_at` on the entity is enough.

## Trade-offs
- **Advantages:** traceability, compliance, forensics.
- **Disadvantages:** write amplification (every event is a row), storage growth,
  and the temptation to log too much.
- **Alternatives:** DB-level audit triggers (rigid), streaming logs (ephemeral),
  app-level audit table (current choice).

## Vroom examples
- `AuditLog` model with company + session-key context (migrations 0004, 0009).
- Written by `fleet/audit.py` from the middleware/views layer.
- Records login and download actions.

## Common mistakes
- Logging secrets (passwords, tokens, session keys).
- Audit outside a transaction → inconsistent with the action.
- No retention policy → unbounded growth.
- Forgetting tenant/session context → audit can't reconstruct "which company."

## Required tests
- Audit row created for the action, with correct company + session context.
- No secrets in audit payloads.

## Security review
Audit never contains credentials; audit writes are not attacker-controlled
(no unbounded reflection); audit trail is append-mostly.

## Performance review
Audit writes are indexed by company/time; bulk/aggregate reads don't scan the
whole table. Watch write amplification under load.
