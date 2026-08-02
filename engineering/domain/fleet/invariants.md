# Fleet — Invariants

| # | Invariant | Enforcement | Proof |
|---|---|---|---|
| F1 | Every Vehicle/Driver/Document/Maintenance/Violation belongs to exactly one company | `TenantScopedModel` + FK | tenant tests |
| F2 | No cross-tenant access to any entity (read or write) | view-layer scope + defensive `.filter(company=...)` | IDOR + k6 isolation |
| F3 | Document files are private; download only via signed, expiring URL | signed-download pattern (ADR 0002) | download tests |
| F4 | Revoked download links stop working | `download_token_version` bump invalidates signatures | revoke tests |
| F5 | Superseded document files are deleted best-effort | model `save`/`delete` overrides | file hygiene tests |
| F6 | License plates and CINs are unique | DB unique constraints | model tests |

## Open questions (Business Rules Review)
- Should uniqueness of plate/CIN be per-company rather than global?
- Should an inactive driver be un-bookable? (currently no rule).
