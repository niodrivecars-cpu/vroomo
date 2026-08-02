# Execution Model

How work actually flows through the platform. One loop governs every change;
roadmap phases (1, 1.5, 1.6, 2A, 2A.5, …) are checkpoints on this loop, not
separate machines.

## The loop

```text
Route ─→ Plan ─→ Build ─→ Verify ─→ Evidence ─→ Learn ─→ (back to Route)
 │        │         │         │          │
decision  task      source    gates      evidence
tree      template  of truth             pipeline
```

| Stage | What happens | Where |
|---|---|---|
| **Route** | Decide which capability/pipeline/record applies | `kernel/decision-tree.md` |
| **Plan** | Structure the work, state the claim to be proven | `execution/checklists/task-template.md` |
| **Build** | Change the source of truth first, then invariants, then code | source-of-truth order (below) |
| **Verify** | Gates evaluate evidence against thresholds; gates block | `execution/gates/` |
| **Evidence** | Record proof, rate confidence, assess risk, get approval | `execution/pipelines/evidence-pipeline.md` |
| **Learn** | Review the platform itself; capture lessons in knowledge/ | `meta/`, `knowledge/` |

## Source-of-truth order (build)
`Rule → Invariant → Tests → Implementation`. Code that changes without its rule
or invariant updating must fail its tests. The rule language block is the head
of this chain (`kernel/rule-language.md`).

## The roles
- **Capability** — a promise the platform makes (Security, Release, Business
  Rule Review, …). `platform/capabilities/`.
- **Skill** — a tool that executes part of a capability (sub-agent, CLI, MCP).
- **Gate** — a pass/fail threshold backed by evidence; blocks a release or a
  phase when not met. `execution/gates/`.
- **Pipeline** — the orchestration that runs gates, reviews, and sign-offs in
  order. `execution/pipelines/`.
- **Evidence** — a recorded, confidence-rated proof artifact keyed to a commit.
  `evidence/`.

## When a loop iteration is "done"
- The claim is proven: evidence exists, is rated, and a gate evaluated it.
- OR the gap is owned: recorded with an owner and a phase, never silent.
- AND the platform itself still complies with the kernel (no drift introduced).
