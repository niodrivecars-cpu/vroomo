# Capability: Business Rule Review

**Promise:** business rules are the source of truth, never the code. Every rule
is written (`domain/`), restated as an invariant, protected by a reference test,
and traceable to evidence. Reviews check the methodology of the rules — not
Python.

This capability is **distinct from `booking-domain-review`** (which reviews the
booking context itself). Business Rule Review is the general methodology:
how every rule, edge case, state machine, and transition is represented and
traced, across all bounded contexts.

## Skills
- `business-rule-review` (sub-agent) — reviews rules, edge cases, state
  machines, forbidden transitions, cross-domain consistency, rule→test tracing.
- `booking-domain-review` (sub-agent) — context-specific review of booking.
- `test-writer` (sub-agent) — turns invariants into reference tests.
- `execution/checklists/business-rule-review-checklist.md` — the review checklist.

## Requirements
1. **Source of truth order** is Rule → Invariant → Tests → Implementation. If
   code changes and the rule didn't, tests must fail. If the rule changes, the
   invariant is updated first, then tests, then implementation.
2. **Every rule is traceable** through the Business Traceability Gate chain
   (`execution/gates/business-traceability-gate.md`).
3. **State machines are explicit.** Allowed/forbidden transitions are documented
   (`domain/<context>/state-machine.md`) and tested.
4. **Edge cases are catalogs**, not discoveries. `edge-cases.md` is reviewed for
   completeness before new logic is written.
5. **Cross-domain consistency** is checked (e.g. booking exclusivity vs vehicle
   status vs violation linking).
6. **A rule in prose only is debt.** A rule without a reference test row is a
   recorded gap with an owner.

## Gate
`execution/gates/business-traceability-gate.md` — Rule → Invariant → Code →
Test → Evidence, with gaps owned and tracked.

## Evidence
Traceability snapshots in `evidence/traceability/`. Review verdicts recorded as
T3 artifacts.
