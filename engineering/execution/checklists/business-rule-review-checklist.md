# Business Rule Review Checklist

Used by the `business-rule-review` reviewer. It reviews the *methodology* of
rules across all contexts — not the Python.

## Rule representation
- [ ] Every business rule is written in `domain/<context>/business-rules.md` in
      business language, no implementation jargon
- [ ] Every rule maps to a numbered invariant (B1, F1, …) in `invariants.md`
- [ ] The invariant names its enforcement (form / model / FK / service / view)
- [ ] No rule exists only in code with no document
- [ ] **Canonical discipline:** the entity/state/event/command/policy is defined
      in `domain/model/` once; this context doc references it, not redefines it

## Edge cases
- [ ] Boundary values covered (adjacent windows, exactly equal dates, zero amounts)
- [ ] Empty / missing / null inputs defined
- [ ] Cross-tenant inputs defined (IDOR-shaped cases)
- [ ] Concurrent/duplicate submissions defined (exclusivity, idempotency)

## State machines
- [ ] Every statused entity has a `state-machine.md`
- [ ] Allowed transitions listed explicitly
- [ ] Forbidden transitions listed explicitly AND tested
- [ ] Derived states (late, overdue, is_due) have a definition, not just code

## Cross-domain consistency
- [ ] Booking exclusivity ↔ vehicle availability consistent
- [ ] Violation linking ↔ active booking consistent
- [ ] Vehicle status ↔ maintenance/expired-doc policy consistent
- [ ] Money rules consistent across booking/pricing/violation

## Traceability
- [ ] Every invariant has a `test-matrix.md` row
- [ ] Every "needed"/"open" row is a recorded, owned gap in the traceability
      snapshot + roadmap
- [ ] Every green row maps to a real test file/location
- [ ] No gap exists silently (all breaks are owned)

## Governance (Phase 2A)
- [ ] Every policy in `domain/model/policies.md` has an Owner and Source
- [ ] Every policy has a Decision status: ✅ Enforced / 🟡 Validated /
      🔵 Proposed / ⚪ Out of Scope / ❌ Rejected
- [ ] Every policy lists Risk (Operational/Financial/Security/Legal/Customer
      Experience) and Priority (P0–P3) from the matrix in `policies.md`
- [ ] 🔵 Proposed policies have an owner and a decision date/blocker, not silence
- [ ] Every Use Case in `domain/model/use-cases.md` binds Commands → Policies →
      Events → Tests
- [ ] Every policy is referenced by ≥1 Use Case; no policy is untraced
- [ ] Validated-but-unimplemented policies are the Phase 2A workload, tracked in
      the roadmap

## Verdict
- [ ] Rules consistent, traceable, edge-cases complete, state machines explicit,
      policies governed, use cases closed
- [ ] OR: gaps listed with owners (recorded in snapshot, tracked in roadmap)
