# Consistency Review

Detects contradictions and terminology drift across documents. Complements the
Knowledge Consistency Gate (`execution/gates/knowledge-consistency-gate.md`),
which is automated; this review is the human/judgment pass on top.

## What to check
| Check | Detail |
|---|---|
| Terminology | every doc uses the glossary term for each concept |
| Model ↔ context | `domain/<ctx>/` files reference `domain/model/`, never redefine |
| State machines | context state files match `domain/model/state-machines.md` |
| Policy status | any doc that states a policy status matches the register |
| Evidence refs | every `evidence/…` path cited in docs exists and is current |
| Gate wiring | every capability's gate column resolves to a real gate file |

## Method
1. Pick a layer (e.g. `domain/`) and cross-check it against the canonical model.
2. Flag contradictions, not style preferences.
3. Fix by updating the lower-priority document to reference the source of truth.

## Verdict
PASS if no contradiction; FAIL with the pairs — recorded as meta evidence.
