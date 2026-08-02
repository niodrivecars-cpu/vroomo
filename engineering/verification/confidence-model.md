# Confidence Model

How much to trust each type of evidence, and how confidence compounds.

## Per-evidence confidence
| Evidence type | Confidence | Why |
|---|---|---|
| Deterministic test (red→green, hermetic) | High | Machine-checked, reproducible |
| Load test on fresh state | High | Numeric thresholds, controlled setup |
| Static scanner (bandit/pip-audit) | Medium-High | Covers known classes only |
| Human security review | Medium | Process quality, subject to bias |
| Human code review | Medium | Judgment, checklist-driven |
| "It worked locally" | Low | Uncontrolled environment, one sample |

## Compounding
- Multiple independent evidence types for the same claim raise confidence
  (e.g. exclusivity: unit test + load test + code review).
- Same evidence type repeated does not add much (re-running the same test
  doesn't cover a different failure mode).
- Confidence drops with: stale evidence (run against older code), non-fresh
  state (dirty DB/cache), or missing review sign-off.

## Staleness rule
Evidence is only valid for the commit it ran against. After any code change,
affected evidence must be regenerated before a release claim.

## Confidence ↔ stage
| Stage | Required confidence |
|---|---|
| Everyday commit | T1 tests + T2 static |
| RC | + T2 load + T3 review, residual risk accepted |
| v1.0.0 | + pilot feedback + production-like verification |
| Production | + observability + measured SLOs |
