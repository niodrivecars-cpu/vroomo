# Patterns Library

Approved solutions — the "how we do X" reference. Each pattern is a decision
with trade-offs, evidence, and review points, so teams reuse judgment, not just
code.

## Index

| Pattern | Use when | Status |
|---|---|---|
| `multi-tenant/` | Data is owned by many tenants; isolation is a requirement | Approved (Vroom) |
| `audit/` | Security-relevant actions must be traceable | Approved (Vroom) |
| `rbac/` | Fine-grained permissions are needed | Reference (Vroom uses session-level auth) |
| `signed-download/` | Private files served to authorized users with expiry | Approved (Vroom) |
| `django-service-layer/` | Business logic needs a testable home outside views | Approved (Vroom) |
| `cqrs/` | Read vs write scaling divergence (heavy, rare) | Reference — avoid unless needed |
| `repository/` | Isolate data access for testability | Reference |
| `domain-events/` | Loosely-coupled reactions to state changes | Reference |
| `soft-delete/` | Logical delete with audit/history | Reference — carries complexity |

## Pattern file contract
Each pattern documents: why / when not to / trade-offs / Vroom examples / common
mistakes / required tests / security review / performance review. See
`TEMPLATE.md`.
