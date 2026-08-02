# Business Rule Review Checklist

Used by the `business-rule-review` reviewer. It reviews the *methodology* of
rules across all contexts — not the Python.

## Rule representation
- [ ] Every business rule is written in `domain/<context>/business-rules.md` in
      business language, no implementation jargon
- [ ] Every rule maps to a numbered invariant (B1, F1, …) in `invariants.md`
- [ ] The invariant names its enforcement (form / model / FK / service / view)
- [ ] No rule exists only in code with no document

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

## Verdict
- [ ] Rules consistent, traceable, edge-cases complete, state machines explicit
- [ ] OR: gaps listed with owners (recorded in snapshot, tracked in roadmap)
