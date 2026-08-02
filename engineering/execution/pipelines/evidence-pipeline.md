# Pipeline: Evidence

The Evidence Engine. Turns raw proof artifacts into **rated, decided, approved
decisions** — instead of a directory of JSON files.

```text
Evidence → Confidence → Risk → Decision → Approval
```

## Steps

| # | Step | Input | Output | Source of truth | Gate hook |
|---|---|---|---|---|---|
| 1 | **Capture** | test run, scan, measurement, review | evidence artifact (manifest) | `evidence/` | gate artifacts |
| 2 | **Confidence** | manifest | confidence level (Unverified→Proven) | `kernel/confidence-model.md` | confidence field |
| 3 | **Risk** | confidence + claim | residual risk + acceptance | `verification/risk-matrix.md` | risk field |
| 4 | **Decision** | rated evidence | proceed / block / defer | `governance/DECISION_PROCESS.md` | gate verdict |
| 5 | **Approval** | decision | signed approval (role + date) | `execution/pipelines/decision-pipeline.md` | approval field |

## Rules
1. **No manifest without confidence.** A manifest that does not state its
   confidence level is a record, not a verdict — it cannot gate anything.
2. **Confidence never exceeds the evidence.** A human "looks fine" is `Recorded`
   at best; a deterministic test is `Tested`; a gate run is `Gated`.
3. **Staleness blocks.** Evidence for a changed commit must be regenerated
   (`verification/confidence-model.md` staleness rule). A stale manifest cannot
   support a release claim.
4. **Risk precedes decision.** You cannot decide "safe to release" without
   recording residual risk for the stage.
5. **Approval is a role, not a person.** `approval: {role, date}` so the record
   outlives the person.

## Manifest fields added by this engine
- `confidence`: `unverified | recorded | tested | gated | proven`
- `approval`: `{ role, date }`
- `risk`: reference to `verification/risk-matrix.md` row when residual risk exists

Schema: `evidence/schema.json`. Append-only: once a manifest is accepted it is
never rewritten; changes are new manifests with `superseded_by`.
