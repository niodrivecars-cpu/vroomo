# Capability: Architect

**Promise:** every change lands in a structure that is layered, testable, and
understood — and every architectural decision leaves a written record.

## Skills
- django-verifier (sub-agent) — runs the release gate.
- `governance/ENGINEERING_PRINCIPLES.md` — the principles a design must honor.
- `governance/adr/` — decision records (write one when a decision changes shape).

## Requirements
1. **Layer discipline.** Views → services/security helpers → models. Keep
   cross-cutting concerns (auth, tenant scoping, audit) in middleware/security
   modules, not scattered in views.
2. **Tenant boundary is structural.** Every multi-tenant query carries a
   tenant-scoped filter; isolation is not an afterthought (Vroom enforces this
   at the view layer + defensive `.filter(...)`).
3. **Decisions are recorded.** A change to data model, security posture, or
   cross-cutting flow needs an ADR. Small changes don't.
4. **Concurrency claims are provable.** If you claim a query is safe under
   concurrency, cite the test that proves it (Vroom: exclusivity smoke test).

## Coverage
- Knowledge: `knowledge/django/` + `platform/ARCHITECTURE.md`.
- Pattern: None — this capability *is* the structure, not a code solution.
- Checklist: `execution/templates/task-template.md`.
- Review step: maintainer sign-off on ADRs.
- Gate: release-gate · Evidence: ADRs + `platform/ARCHITECTURE.md`.

## Gate
`execution/gates/release-gate.md` — the Django verifier passes or the change
does not merge.
