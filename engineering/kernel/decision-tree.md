# Decision Tree

The routing map every agent follows. **Start here on every task.** If the task
does not match a row, ask — do not improvise a process.

| I need to… | Do | Record / gate |
|---|---|---|
| Route any task | Start at this decision tree | — |
| Set a big direction / new capability / cross-project change | Write an RFC → run the decision pipeline | `rfc/`, `execution/pipelines/decision-pipeline.md` |
| Change the shape of the system (data model, security posture) | Write an ADR | `adr/`, `governance/DECISION_PROCESS.md` |
| Define or change a business policy | Edit the canonical model → add/update its rule block | `domain/model/policies.md`, `kernel/rule-language.md`, completeness gate |
| Implement a **validated** policy | Follow source-of-truth order: rule → invariant → test → code → evidence | `domain/<ctx>/invariants.md`, test-matrix, evidence pipeline |
| Record what we know | Write to `knowledge/<topic>/` (overview / pitfalls / best-practices / references) | knowledge-consistency gate |
| Choose an approved solution | Read `patterns/` — never invent what a pattern already governs | — |
| Build a feature | Use the task template, then the review pipeline | `execution/checklists/task-template.md`, review-pipeline |
| Prove a change is safe | Run the verification standard + evidence pipeline | `verification/verification-standard.md`, `evidence/` |
| Release | Run the release pipeline + release gate | `execution/pipelines/release-pipeline.md`, `execution/gates/release-gate.md` |
| Decide a 🔵 Proposed policy | Record the decision in the register; status → 🟡/⚪/❌ | `domain/model/policies.md` |
| Question whether a doc/agent/claim is trustworthy | Run meta review / consult the failure model | `meta/`, `kernel/failure-model.md` |
| Reuse the platform for a new product | Add `projects/<name>/` — do not touch the kernel | `projects/` |

## Resolution order
1. If a **decision** is needed → `decision-tree` → decision pipeline.
2. If a **policy** is touched → rule language → completeness gate.
3. If **code** is touched → source-of-truth order → review pipeline.
4. If a **release** claim is made → evidence pipeline → release gate.
5. If you doubt the platform itself → meta review.

## What "ask" means
When the routing is ambiguous, ask the human instead of guessing. An
improvised process is how drift starts.
