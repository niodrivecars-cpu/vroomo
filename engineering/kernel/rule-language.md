# Business Rule Language (BRL) — v2

A **formal, machine-readable statement of every business policy** — the engine
of the platform. From one rule block we derive: invariants, reference tests,
documentation, playbooks, threat models, ADR references, review questions, and
(where possible) code. A policy is *described* by prose; a rule block is
*executed* by the Engineering Compiler (`kernel/engineering-compiler.md`).

## Syntax

Each policy carries exactly one rule block, fenced in a Markdown `rule` block:

````markdown
```rule
ID: P20
STATEMENT: Two non-cancelled bookings of one vehicle never overlap
PREDICATE: NOT exists(Booking b: b.vehicle == v AND b.status IN (confirmed, rented) AND overlaps(b, new_booking))
WHEN: Booking.create
UNLESS: —
REQUIRES: —
EVIDENCE: k6.sameVehicleBooking, B1-tests
RISKS: Operational, Financial, Customer Experience
PRIORITY: P0
SEVERITY: BLOCKER
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Fleet Manager
SOURCE: Operational Practice
```
````

## Fields

| Field | Required | Grammar |
|---|---|---|
| `ID` | yes | `P<number>`, unique |
| `STATEMENT` | yes | business language, no implementation jargon |
| `PREDICATE` | yes | **formal boolean expression** (see grammar) — the invariant form |
| `WHEN` | yes | comma-separated trigger commands from `domain/model/commands.md`; `ALL` = every command |
| `UNLESS` | no | override clauses, `override.approved(role=<role>)` |
| `REQUIRES` | no | roles/evidence that must exist before operating or waiving |
| `EVIDENCE` | yes | comma-separated test/evidence ids from `domain/<ctx>/test-matrix.md` or `evidence/`; `—` = gap |
| `RISKS` | yes | tags from `{Operational, Financial, Security, Legal, Customer Experience}` + specific flags (e.g. `Fraud`, `Audit`, `Safety`) |
| `PRIORITY` | yes | `P0`–`P3` (work order, distinct from policy ID) |
| `SEVERITY` | yes | `BLOCKER` · `ERROR` · `WARNING` · `INFO` (impact → action) |
| `DECISION` | yes | `Enforced` · `Validated` · `Proposed` · `Out of Scope` · `Rejected` (business decision state) |
| `ENFORCEMENT` | yes | `PLANNED` · `DOCUMENTED` · `IMPLEMENTED` · `TESTED` (implementation reality) |
| `OWNER` | yes | accountable role/person |
| `SOURCE` | yes | `Law` · `Business Requirement` · `Operational Practice` · `Internal Decision` · `Security Requirement` · `Engineering Proposal` |

## The three dimensions of a rule

| Dimension | Question | Values | What an agent does with it |
|---|---|---|---|
| `DECISION` | Is the policy *agreed*? | Enforced / Validated / Proposed / Out of Scope / Rejected | Proposed → run the Decision Engine; Validated → approve-then-implement |
| `ENFORCEMENT` | Is the policy *real* in the system? | PLANNED / DOCUMENTED / IMPLEMENTED / TESTED | TESTED → claim it; below → it is a gap, owned not silent |
| `SEVERITY` | What happens if it *breaks*? | BLOCKER / ERROR / WARNING / INFO | BLOCKER → gate the build; ERROR → blocking issue; WARNING → issue; INFO → note |

`DECISION` and `ENFORCEMENT` are independent: a policy can be `Validated`
(agreed) but `DOCUMENTED` (not implemented). The old single `Status` field
conflated the two — that was the v1 weakness.

## SEVERITY semantics

| Severity | If violated | Default action |
|---|---|---|
| `BLOCKER` | corrupts a core invariant (isolation, exclusivity, money, legal) | blocks build/release until `ENFORCEMENT: TESTED` |
| `ERROR` | breaks a milestone requirement | blocking issue for the phase; fix or decide |
| `WARNING` | degrades quality | opens an issue, does not block |
| `INFO` | aspirational / hygiene | informational only |

A `BLOCKER` with `ENFORCEMENT: PLANNED|DOCUMENTED` is a **release blocker** by
definition — the Business Completeness Gate fails the stage until it reaches
`TESTED` (or is formally re-scoped).

## PREDICATE grammar

`PREDICATE` is a boolean expression over canonical entities and fields
(`domain/model/entities.md`), written in the invariant form **"holds at all
times"**:

- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Booleans: `AND`, `OR`, `NOT`
- Quantifiers: `exists(Entity e: pred)`, `forall(Entity e: pred)`, `unique(field[, scope])`
- Field references: `Entity.field` (e.g. `Vehicle.status`, `Booking.return_km`)
- Derived helpers: `effective_reserved(v)`, `active_booking(v)`, `overlaps(b1, b2)`,
  `is_due`, `is_overdue`, `is_expired`

`WHEN` scopes where the predicate is asserted; the predicate itself is global.

## Derivation & compilation

Changing a rule block propagates through the **Engineering Compiler**
(`kernel/engineering-compiler.md`):

```text
Rule ─→ Parser ─→ Validator ─→ Generator ─→ Artifacts
                                       ├── tests          (from PREDICATE + EVIDENCE)
                                       ├── threat model   (from RISKS + SEVERITY)
                                       ├── checklist      (from ALL fields)
                                       ├── documentation  (STATEMENT + WHEN)
                                       ├── ADR references (from OWNER/DECISION)
                                       └── review questions (from UNLESS + REQUIRES)
```

A rule whose `EVIDENCE` references a test that does not exist is a **gap**
(owned, never silent). `DECISION: Enforced` requires `ENFORCEMENT` ≥
`IMPLEMENTED`; full closure is `ENFORCEMENT: TESTED`.

## Conformance

- **Validator**: `engineering/kernel/compiler/validate_rules.py` parses every
  rule block and enforces: required fields, enum values, `ID` uniqueness, and
  the cross-checks above. Run it before any rule change lands.
- **Gate**: the Business Completeness Gate (checks 7–8) requires a valid v2
  rule block per policy and no `BLOCKER` left below `TESTED` for a release.
- **Review**: the Business Rule Review checklist verifies `PREDICATE` terms
  reference only canonical entities/fields.
