# Failure Model

How the Engineering Platform fails — and how each failure is detected. The point
is to name the failure modes so they can be *caught*, not wondered about. This
is the platform's answer to "who audits the auditors?"

## Drift modes

| # | Drift mode | Symptom | Detection | Response |
|---|---|---|---|---|
| 1 | **Documentation drift** | Doc says X, code does Y | Consistency review, business-rule review | Update source of truth first; fix code or doc |
| 2 | **Gate theater** | Gates "pass" without evaluating real evidence | Meta review of gate outputs | Re-run gate with evidence; block the phase |
| 3 | **Evidence rot** | Manifest references a stale/missing commit | Staleness rule (`confidence-model.md`) | Regenerate evidence at the new commit |
| 4 | **Orphaned rule** | Policy with no invariant, no test row | Business Completeness Gate (checks 3, 7–8) | Create the invariant/test or own the gap |
| 5 | **Silent gap** | 🔲/🧾 with no owner or phase | Every gate ("no silent gap") | Record owner + phase, or drop the claim |
| 6 | **Duplicated truth** | Same concept defined in two places | Duplication review (`meta/duplication-review.md`) | Keep one source; supersede the other |
| 7 | **Model–code drift** | Code changed before the canonical model | Source-of-truth order (build) | Roll back or update rule → invariant → test → code |
| 8 | **Terminology drift** | Same concept, different words | Knowledge Consistency Gate | Fix to glossary term |
| 9 | **Scope creep** | Platform grows without a failure it prevents | Principle 8 (simplicity) | Cut or defer the addition |

## Meta loop
Every drift mode has a detector in `meta/` or `execution/gates/`. If a drift
mode has **no** detector, the platform has an owned gap — record it in the
meta gate evidence, not in prose.

## Escalation
- A drift that a gate should have caught is a **meta failure** (the gate or the
  platform is wrong), not a product bug.
- Meta failures are reviewed by `meta/` and recorded as evidence, so the
  platform improves itself.
