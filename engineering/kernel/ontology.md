# Engineering Ontology

The formal **relations** between every platform concept. The Glossary
(`platform/GLOSSARY.md`) defines *what each term means*; the ontology defines
*how the terms relate*. Both are single sources: the ontology derives from the
kernel, the rule language, and the glossary — it is never written in parallel.

## Nodes

| Node | Defined by |
|---|---|
| Entity, Aggregate, ValueObject, State, Event, Command, Guard, Policy, Rule, Invariant | `domain/model/*`, `kernel/rule-language.md` |
| Test, Evidence, Risk, Confidence, Review, MetaReview, Drift | `verification/*`, `kernel/confidence-model.md`, `kernel/failure-model.md`, `meta/` |
| Capability, Skill, Agent, Pipeline, Gate, Playbook, Runbook, Checklist | `platform/capabilities/`, `execution/` |
| RFC, Decision, ADR | `governance/rfc/`, `governance/adr/` |

## Edges

| From | Relation | To |
|---|---|---|
| Entity | has | StateMachine |
| StateMachine | permits / forbids | State (transition) |
| Entity | belongs to | Aggregate |
| Command | guarded by | Policy |
| Command | guarded by | Invariant |
| Command | emits | Event |
| Policy | expressed as | Rule (BRL block) |
| Rule | maps to | Invariant |
| Invariant | enforced by | Test |
| Test | produces | Evidence |
| Evidence | raises | Confidence |
| Risk | tags | Policy |
| RFC | proposes | Decision |
| ADR | records | Decision |
| Decision | references | Evidence |
| Capability | provides | Skill |
| Agent | executes | Skill |
| Pipeline | orchestrates | Gate |
| Gate | evaluates | Evidence (against threshold) |
| Review | assesses | Gate output / Agent output |
| MetaReview | reviews | Review, Agent, Prompt, Knowledge |
| Drift | detected by | MetaReview / FailureModel |

## The core chain (what must never break)

```text
Policy → Rule → Invariant → Test → Evidence → Confidence → Decision
   │                                    │                     │
 Entity/Command/Event ←── traceability ──┘                     └→ ADR → Implementation
```

Traceability means following this chain without a missing link. A missing link
is an owned gap (kernel `failure-model.md`, drift mode 4).

## Rules
1. Every node has exactly one defining document. A relation not listed here is
   either unsupported or must be added to the ontology first.
2. Derivation: graphs, matrices, and generated artifacts follow from these
   edges — they never define new relations.
3. When the glossary adds a term, the ontology is checked for its relations;
   when the rule language changes, the ontology's edges are re-validated.
