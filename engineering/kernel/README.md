# Engineering Kernel

The **brain** of the Engineering Platform. Every agent, pipeline, and gate starts
here before touching `platform/`, `governance/`, or any project.

The kernel is the *philosophy* layer; the platform is the *operating system*
layer. The kernel says **how we think** (mission, principles, decision tree,
execution model, confidence, failure); the platform says **how we operate**
(pipelines, gates, capabilities, playbooks).

```text
engineering/
  kernel/        ← THE BRAIN (this directory): how we think
  platform/      ← the operating system: how we operate
  governance/    ← how decisions are recorded (principles, standards, ADR, RFC)
  meta/          ← who reviews the platform itself (meta engineering)
  knowledge/     ← what we know
  patterns/      ← approved solutions
  domain/        ← the canonical business model
  execution/     ← pipelines, gates, playbooks, runbooks
  verification/  ← how we prove correctness
  evidence/      ← what the proof is
  projects/      ← products built on the platform
```

## What lives here

| File | Answers |
|---|---|
| `mission.md` | Why does the platform exist? What does it refuse? |
| `principles.md` | What meta-principles govern the platform itself? |
| `decision-tree.md` | Which capability / pipeline / gate / record do I use when? |
| `execution-model.md` | How work actually flows through the platform |
| `confidence-model.md` | How much does the platform trust its own claims? |
| `failure-model.md` | How does the platform fail (drift), and how is drift detected? |
| `rule-language.md` | The formal Business Rule Language (BRL) — the engine |
| `ontology.md` | The formal relations between every platform concept |

## The one rule of the kernel
> Every agent starts here. If an agent's plan contradicts the kernel, the
> kernel wins and the plan is wrong.
