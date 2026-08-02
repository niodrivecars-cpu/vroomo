# Decision Checklist

Used by the decision pipeline (`execution/pipelines/decision-pipeline.md`).

## Proposal → RFC
- [ ] Problem stated in business language, no premature solution
- [ ] Options listed with trade-offs (at least 2, including "do nothing")
- [ ] Decision is written down in `governance/rfc/` (or a commit + tests is
      honestly sufficient — `governance/DECISION_PROCESS.md` thresholds)

## Discussion
- [ ] Objections are recorded, not deleted
- [ ] Every objection has a resolution (accepted, rejected-with-reason, or
      parked with an owner)

## Decision → ADR
- [ ] Decision line: Accepted / Rejected / Superseded with reason
- [ ] ADR numbered, immutable, filed in `governance/adr/`
- [ ] ADR records context, decision, consequences, and evidence pointers

## Implementation → Evidence → Verification
- [ ] Implementation followed source-of-truth order (rule → invariant → test →
      code → evidence)
- [ ] Evidence recorded with confidence (Evidence Engine step 2)
- [ ] Residual risk recorded for the stage
- [ ] A gate evaluated the evidence (not just "tests passed locally")

## Closure
- [ ] ADR is the reference; no competing definition exists (duplication review)
- [ ] If it was a policy decision: register status updated
      (🔵 → 🟡/⚪/❌) in `domain/model/policies.md`
