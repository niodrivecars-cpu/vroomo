# Confidence Model

How much the platform can trust its **own** claims — e.g. "policy P20 is
enforced", "the model is complete", "this doc is the source of truth".

This is the platform-self confidence ladder. It complements (and never replaces)
the product evidence tiers in `verification/confidence-model.md` and
`verification/verification-standard.md` (T1–T4).

## Confidence ladder

| Level | Meaning | Evidence needed | Example |
|---|---|---|---|
| **Unverified** | Claimed, nothing recorded | none | "the API is fast" |
| **Recorded** | A manifest/artifact exists | JSON manifest, doc | `evidence/testing/rc1-suite.json` |
| **Tested** | Executable proof exists and runs | T1 test / T2 scan | exclusivity k6 test |
| **Gated** | A gate evaluated the proof | gate pass + gate artifact | release gate on RC1 |
| **Proven** | Accepted for a stage, residual risk recorded | all of the above + approval | v1.0.0-rc1 release |

## Rules
1. A claim inherits the confidence of its **weakest** link. "P20 enforced" is
   only `Tested` if the test exists, regardless of how good the docs are.
2. Staleness drops confidence: evidence is valid only for the commit it ran
   against (same rule as `verification/confidence-model.md`).
3. Compounding: independent evidence types (unit + load + review) raise
   confidence; repeating the same type does not.
4. A platform doc that asserts a claim about Vroom must cite the evidence link
   or it is `Unverified` by definition.

## Evidence Engine wiring
This ladder is step 2 of the Evidence Engine:

```text
Evidence → Confidence → Risk → Decision → Approval
```

`execution/pipelines/evidence-pipeline.md` orchestrates the five steps.
