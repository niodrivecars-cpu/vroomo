# Engineering Compiler

The machine that turns a rule block into **every downstream artifact**. This is
what makes the platform's knowledge *executable*: the rule is the single input,
everything else is generated or verified against it.

```text
Rule ─→ Parser ─→ Validator ─→ Generator ─→ Artifacts
                                            ├── tests
                                            ├── threat model
                                            ├── checklist
                                            ├── documentation
                                            ├── ADR references
                                            └── review questions
```

## Stages

### 1. Parser
Reads every `rule` block from `domain/model/policies.md` (spec:
`kernel/rule-language.md`). Output: a structured rule object
(`ID`, `PREDICATE`, `WHEN`, `EVIDENCE`, `RISKS`, `SEVERITY`, `DECISION`,
`ENFORCEMENT`, …).

Implemented: `engineering/kernel/compiler/validate_rules.py`.

### 2. Validator
Checks each rule object:

| Check | Fails when |
|---|---|
| Required fields | a required field is missing |
| Enum values | `SEVERITY`/`DECISION`/`ENFORCEMENT`/`PRIORITY` not in their sets |
| ID uniqueness | two blocks share an `ID`, or `ID` ≠ its heading |
| Decision ↔ enforcement | `DECISION: Enforced` with `ENFORCEMENT: PLANNED`; `ENFORCEMENT: TESTED` with `DECISION != Enforced` |
| Release block | a `BLOCKER` below `TESTED` exists (report, not hard fail) |
| Evidence resolvability | `EVIDENCE` ids are not listed in the context `test-matrix.md` (report) |

Implemented in `validate_rules.py`; gate hook: Business Completeness Gate.

### 3. Generator
One generator per artifact family. All **derive from the rule object** — none of
them introduce new facts. Worked example for P20
(`NOT exists(... overlaps ...) WHEN Booking.create`, `SEVERITY: BLOCKER`,
`RISKS: Operational, Financial, Customer Experience`):

| Artifact | Generated from | P20 example output |
|---|---|---|
| **Test template** | `PREDICATE` + `EVIDENCE` | "same vehicle, same window → 1 success (k6)"; "adjacent windows → both allowed"; "overlapping → blocked" |
| **Threat model** | `RISKS` + `SEVERITY` | "double-booking (Operational, Financial) — BLOCKER: concurrency race; mitigation: check-then-insert + retry (ADR 0005)" |
| **Checklist** | all fields | "CreateBooking checks exclusivity before insert"; "retry on write-lock"; "owner Fleet Manager signs off" |
| **Documentation** | `STATEMENT` + `WHEN` | "Two non-cancelled bookings of one vehicle never overlap. Asserted at Booking.create." |
| **ADR references** | `OWNER`/`DECISION` + graph | "see ADR-0005 (write-lock retry); re-review if ADR-0005 changes" |
| **Review questions** | `UNLESS` + `REQUIRES` | "Who may override overlap? Manager — is that sufficient?" |

### 4. Artifacts
Generated artifacts are stored *next to* the rule, marked as derived. When the
rule changes, the artifacts are regenerated — never hand-edited
(`kernel/principles.md`, derivation rule).

## Current state
- Parser + Validator: **implemented and run** (`validate_rules.py`, PASS on
  P1–P21).
- Generators: specified above; automated output is Phase 2B.2 (Rule Coverage)
  work. Manual derivation already happens in the completeness matrix
  (`verification/completeness/vroom-rc1.md`), traceability snapshot
  (`verification/traceability/vroom-rc1.md`), and the policy graph
  (`verification/traceability/vroom-graph.md`).

## Fit with the platform
- Input source of truth: `domain/model/policies.md` (rule blocks)
- Spec: `kernel/rule-language.md`
- Validator: `engineering/kernel/compiler/validate_rules.py`
- Gate: `execution/gates/business-completeness-gate.md` (checks 7–8)
- Roadmap: generators land in Phase 2B.2; scenario compilation in 2B.4
  (`domain/model/scenarios.md`).
