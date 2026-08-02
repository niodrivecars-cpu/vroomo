# Gate: Capability Coverage

**Purpose:** every capability the platform promises is actually backed by the
full machinery — a standard, a pattern (or explicit rationale), knowledge,
a checklist, a review step, a gate, and evidence. A capability that exists only
as a promise is a debt.

## The coverage contract

Each capability must fill these slots:

| Slot | Where it lives | Required? |
|---|---|---|
| Definition / Promise | `platform/capabilities/<name>.md` | always |
| Skills | same file (sub-agents, scanners, MCP) | always |
| Knowledge | `knowledge/` topic(s) | always |
| Pattern(s) | `patterns/<name>/` | always, or "None — rationale" |
| Checklist | `execution/checklists/` | always |
| Review step | reviewer role + pipeline | always |
| Gate | `execution/gates/` | always |
| Evidence | `evidence/` | always (produced by the gate) |

## The coverage matrix

Maintained in `platform/capabilities/README.md`. Every row lists the concrete
artifacts per slot. An empty cell is a **gate failure** unless it says
"None — <rationale>" explicitly.

## Checks

| # | Check | Pass |
|---|---|---|
| 1 | Every capability row exists in the matrix | 1 row per capability file |
| 2 | Every slot filled or marked "None — rationale" | 0 empty cells |
| 3 | Every referenced artifact exists (links resolve) | no dead references |
| 4 | Every capability maps to a review step (T3 evidence) | yes |
| 5 | Every capability's evidence location is populated or has a plan | yes |

## Evidence

The gate run records the matrix review in
`evidence/verification/capability-coverage-<date>.json`. Gaps are debts and are
tracked in `platform/ROADMAP.md`.
