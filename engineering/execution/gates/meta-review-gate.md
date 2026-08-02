# Gate: Meta Review

**Purpose:** the platform reviews itself. After every phase (or on suspicion of
drift), this gate checks that the platform's agents, prompts, knowledge, and
gates still comply with the kernel — and that no drift mode
(`kernel/failure-model.md`) has a silent detector gap.

This is the **entry gate for reusability**: a platform that passes its own meta
review can be trusted for the next project (Nio Drive).

## Checks

| # | Check | Source |
|---|---|---|
| 1 | Agents start at the kernel | `meta/agent-quality.md` |
| 2 | Prompts are scoped, current, and evidence-requiring | `meta/prompt-quality.md` |
| 3 | Knowledge is sourced, current, non-duplicative | `meta/knowledge-quality.md` |
| 4 | No unanchored/contradicted claims | `meta/hallucination-review.md` |
| 5 | No concept defined twice | `meta/duplication-review.md` |
| 6 | No cross-document contradiction | `meta/consistency-review.md` |
| 7 | Every drift mode has a detector | `kernel/failure-model.md` |

## Output
A meta review record listing per-check PASS/FAIL, filed as evidence:

`evidence/verification/meta-review-<date>.json`

## Pass criteria
All checks pass, **or** every failure is an owned gap with an owner and a phase.
The gate cannot "pass by silence": a check that was not run is a FAIL.
