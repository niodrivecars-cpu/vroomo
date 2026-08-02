# Business Rule Language (BRL)

A **formal, machine-readable statement of every business policy** — the engine
of the platform. From one rule block we derive: invariants, reference tests,
documentation, playbooks, threat models, and (where possible) code.

A policy in prose ("P1: no booking during maintenance") is a *human* statement.
A rule block is the *formal* statement the platform executes against.

## Syntax

Each policy carries exactly one rule block, fenced in a Markdown `rule` block:

````markdown
```rule
ID: P1
STATEMENT: A vehicle must not be booked while it is under maintenance
GUARD: Vehicle.status != MAINTENANCE
WHEN: Booking.create
UNLESS: override.approved(role=manager)
REQUIRES: role.manager
EVIDENCE: B1-tests
RISKS: Operational, Safety, Customer Experience
PRIORITY: P0
STATUS: Validated
OWNER: Fleet Manager
SOURCE: Operational Practice
```
````

## Fields

| Field | Required | Grammar |
|---|---|---|
| `ID` | yes | `P<number>`, unique |
| `STATEMENT` | yes | business language, no implementation jargon |
| `GUARD` | yes | boolean expression (see below) |
| `WHEN` | yes | comma-separated trigger commands from `domain/model/commands.md`; `ALL` = every command |
| `UNLESS` | no | override clauses, `override.approved(role=<role>)` |
| `REQUIRES` | no | roles/evidence that must exist before operating or waiving |
| `EVIDENCE` | yes | comma-separated test/evidence ids from `domain/<ctx>/test-matrix.md` or `evidence/`; `—` = gap |
| `RISKS` | yes | tags from `{Operational, Financial, Security, Legal, Customer Experience}` + specific flags (e.g. `Fraud`, `Audit`, `Safety`) |
| `PRIORITY` | yes | `P0`–`P3` (work order, distinct from policy ID) |
| `STATUS` | yes | `Enforced` · `Validated` · `Proposed` · `Out of Scope` · `Rejected` |
| `OWNER` | yes | accountable role/person |
| `SOURCE` | yes | `Law` · `Business Requirement` · `Operational Practice` · `Internal Decision` · `Security Requirement` · `Engineering Proposal` |

## GUARD grammar

`GUARD` is a boolean expression over canonical entities and fields
(`domain/model/entities.md`):

- Comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Booleans: `AND`, `OR`, `NOT`
- Quantifiers: `exists(Entity e: pred)`, `forall(Entity e: pred)`
- Field references: `Entity.field` (e.g. `Vehicle.status`, `Booking.return_km`)

Expressions read as **"this must hold at all times"** (the invariant form). The
`WHEN` clause scopes where the guard is asserted.

## Derivation rule

Changing a rule block propagates, in order:

1. **Ontology** (`kernel/ontology.md`) — the relations the rule participates in
2. **Invariant** (`domain/<ctx>/invariants.md`) — restate `GUARD` as B#/F#
3. **Test** (`domain/<ctx>/test-matrix.md`) — every `EVIDENCE` id gets a row
4. **Implementation** — enforce the guard in the service layer
5. **Evidence** — record proof at the implementing commit

A rule whose `EVIDENCE` references a test that does not exist is a **gap**
(owned, never silent). A `STATUS: Validated` rule must move to `Enforced` only
after its evidence exists and a gate ran.

## Conformance

- The Business Completeness Gate (checks 7–8) requires every policy to have a
  rule block with a valid `STATUS` and resolvable `EVIDENCE`.
- The Business Rule Review checklist verifies `GUARD` terms reference only
  canonical entities/fields.
- No two rule blocks may share an `ID`, and no policy may exist without a block.
