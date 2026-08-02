# Hallucination Review

Detects claims in platform docs that are not supported by code, tests, or
evidence. This is the platform's guard against "documentation drift" (kernel
`failure-model.md`, mode 1).

## Method
For each factual claim in a document, ask:
1. **Is it anchored?** It cites a file, test, command, or evidence id — not
   vague authority.
2. **Does the anchor exist and say this?** Open the cited file and check.
3. **Is it current?** The anchor matches the current canonical model and commit.

## Claim classes
| Class | Example | Verdict |
|---|---|---|
| Anchored + true | "Vehicle has no `reserved` state" → `fleet/models.py` | PASS |
| Anchored + stale | policy status contradicts `policies.md` register | FAIL (stale) |
| Unanchored + plausible | "the app scales to 10k users" | FAIL (unverified) |
| Contradicted | doc says X, model says not-X | FAIL (drift) |

## Sources to scan first
- `knowledge/` and `patterns/` claims about Vroom behavior
- capability docs' references to gates/evidence
- playbooks/runbooks step descriptions

## Verdict
PASS if every claim is anchored and current; FAIL with the offending claims —
recorded as meta evidence.
