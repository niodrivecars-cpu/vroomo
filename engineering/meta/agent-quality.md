# Agent Quality Review

How to assess the output of a sub-agent (django-verifier, security-reviewer,
test-writer, business-rule-review, booking-domain-review).

## Criteria
| # | Criterion | Pass |
|---|---|---|
| 1 | **Started at the kernel** | agent plan routed via `kernel/decision-tree.md` before acting |
| 2 | **Claims are evidence-backed** | every verdict cites a test/scan/review, or is marked unverified |
| 3 | **No silent gaps** | every 🔲/🧾 it found has an owner + phase |
| 4 | **Respects source-of-truth order** | never wrote code before the rule/invariant |
| 5 | **Canonical discipline** | referenced `domain/model/`, never redefined an entity/policy |
| 6 | **Terminology** | used glossary terms exactly (`platform/GLOSSARY.md`) |
| 7 | **Honest scope** | refused tasks outside its capability instead of improvising |

## Anti-patterns (fail)
- Producing a confident verdict with no artifact to back it.
- "Fixing" a doc by rewriting the canonical source instead of referencing it.
- Inventing a process that the decision tree does not define.

## Verdict
PASS, or FAIL with the specific criterion violated — recorded as meta evidence.
