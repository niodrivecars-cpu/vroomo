# Knowledge Quality Review

How to assess a knowledge document (`knowledge/<topic>/overview.md`,
`pitfalls.md`, `best-practices.md`, `references.md`; patterns; playbooks).

## Criteria
| # | Criterion | Pass |
|---|---|---|
| 1 | **Sourced** | claims reference code, docs, or evidence; not "trust me" |
| 2 | **Current** | matches the canonical model and current code (no stale examples) |
| 3 | **Non-duplicative** | does not redefine a glossary term or canonical entity |
| 4 | **Structured** | follows its topic's four-file shape |
| 5 | **Actionable** | a reader can apply it; pitfalls say *why* and *how to avoid* |
| 6 | **Proportional** | length matches value; no padded sections |

## Anti-patterns (fail)
- A doc that asserts a behavior the code does not have (drift mode 1).
- A doc that restates a canonical entity with different fields.
- A doc with an empty "references" that claims authority.

## Verdict
PASS, or FAIL with criterion — recorded as meta evidence.
