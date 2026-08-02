# Pattern: Multi-Tenant Isolation

## Why we use it
Vroom serves many companies (tenants) with data that must never cross company
lines. Isolation is a security requirement, not a performance nicety.

## When NOT to use it
- Single-tenant products — the overhead is pure cost.
- When the tenant boundary is soft (shared data is a feature) — use explicit
  sharing rules instead of pretending tenants are hard walls.

## Trade-offs
- **Advantages:** clear ownership, hard security boundary, natural sharding key.
- **Disadvantages:** every query must carry tenant scope; cross-tenant joins are
  forbidden; admin/global features need explicit "all tenants" paths.
- **Alternatives:** row-level security (DB-level, powerful but harder to test),
  schema-per-tenant (migration cost per tenant), database-per-tenant (ops cost).

## Vroom examples
- `Company` is the tenant; every model carries a company FK.
- Enforced at the view layer + defensive `.filter(company=...)` on every access.
- Attack-tested: k6 asserts 0 tenant-isolation violations; cross-tenant download
  returns 404.

## Common mistakes
- Forgetting the filter on one query (IDOR).
- Caching/aggregations keyed globally instead of by tenant.
- Admin tools that bypass the tenant scope for "convenience."

## Required tests
- Cross-tenant read/write/delete attempts return 403/404 (IDOR cases).
- Isolation asserted under load (`tenant_isolation_violation == 0`).

## Security review
Every new query is tenant-scoped; no shared cache keys across tenants; admin
"global" paths are explicitly reviewed.

## Performance review
Tenant filter columns are indexed; tenant-scoped queries don't scan the whole
table.
