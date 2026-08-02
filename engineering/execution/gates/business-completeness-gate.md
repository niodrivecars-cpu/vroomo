# Gate: Business Completeness

**Purpose:** the business model is complete — every entity has a state machine,
policies, events, commands, invariants, and tests. If an entity lacks any of
these, the model is incomplete and that is a recorded, owned gap.

This is the **entry gate for Phase 2**: it runs against the Canonical Model
(`domain/model/`) and answers one question —

> Does every entity have State Machine · Policies · Events · Commands ·
> Invariants · Tests?

## The six slots

| Slot | Canonical home | Complete when |
|---|---|---|
| State Machine | `domain/model/state-machines.md` | states + legal + **forbidden** transitions |
| Policies | `domain/model/policies.md` | each policy has enforcement status |
| Events | `domain/model/events.md` | real / derived / aspirational classified |
| Commands | `domain/model/commands.md` | every command has a guard |
| Invariants | `domain/<ctx>/invariants.md` | every policy maps to ≥1 invariant |
| Tests | `domain/<ctx>/test-matrix.md` | every invariant has a row (green or owned gap) |

## Checks

| # | Check | Pass |
|---|---|---|
| 1 | Entity coverage | every entity in `entities.md` appears in the completeness matrix |
| 2 | Six slots | every entity row is filled or marked "none — rationale" |
| 3 | Policy → invariant | every policy (P#) maps to an invariant or an owned decision |
| 4 | Forbidden transitions | every state machine lists ✗ transitions |
| 5 | Gaps owned | every 🔲/🧾 row is tracked in the roadmap with an owner |
| 6 | Canonical discipline | no entity redefined outside `domain/model/entities.md` |

## Output

Completeness matrix per project/stage:

`verification/completeness/<project>-<stage>.md`

recorded as evidence (`evidence/verification/business-completeness-<date>.json`).

## Pass criteria (Phase 1.6)
The model is **inventoried** and every gap is owned. Full closure (all policies
enforced, all invariants green) is Phase 2's deliverable; the gate passes 1.6
when the completeness matrix is accurate and no gap is silent.
