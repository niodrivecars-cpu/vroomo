# Meta Engineering

Who reviews the reviewers? The platform's agents review the project. The meta
layer reviews the **platform itself**: its agents, prompts, knowledge, and
gates. This is what makes the platform self-governing instead of self-repeating.

```text
engineering/meta/
  README.md               the meta loop and how it runs
  agent-quality.md        how to assess agent output
  prompt-quality.md       how to assess prompts / agent definitions
  knowledge-quality.md    how to assess knowledge documents
  hallucination-review.md how to detect unsupported claims
  duplication-review.md   how to detect duplicated sources of truth
  consistency-review.md   how to detect cross-document contradiction
```

## The meta loop

```text
Project work → gates → evidence ──► meta review of the platform ──► drift found?
                                              │                          │ no
                                              ▼                          ▼
                                   fix platform (kernel wins)       platform is healthy
```

## When to run
- After a phase (1.5, 1.6, 2A, 2A.5, …) — the platform must have improved or
  at least not regressed.
- When a drift mode in `kernel/failure-model.md` is suspected.
- When an agent or doc produces a claim that "feels off".

## Detectors
| Review | Drift mode it detects |
|---|---|
| `hallucination-review.md` | Documentation drift (mode 1) |
| `duplication-review.md` | Duplicated truth (mode 6) |
| `consistency-review.md` | Terminology / model–code drift (modes 1, 8) |
| `agent-quality.md` | Gate theater, silent gaps (modes 2, 5) |
| `prompt-quality.md` | Gate theater (mode 2) |
| `knowledge-quality.md` | Evidence rot (mode 3) |

Enforced by the Meta Review Gate (`execution/gates/meta-review-gate.md`).
