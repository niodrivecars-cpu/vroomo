# Pipeline: Decision

The Decision Engine. A decision is a **workflow with artifacts**, not a
one-line chat answer. Every step leaves a record, so a decision can be
re-litigated only deliberately.

```text
Proposal → RFC → Discussion → Decision → ADR → Implementation → Evidence → Verification → Accepted
```

## Steps

| # | Step | Artifact | Completeness |
|---|---|---|---|
| 1 | **Proposal** | problem + options in business language | `governance/rfc/<NNNN>-*.md` |
| 2 | **RFC** | formatted proposal for comment | RFC template |
| 3 | **Discussion** | recorded comments/objections in the RFC | RFC doc history |
| 4 | **Decision** | Accepted / Rejected / Superseded (+ why) | RFC decision line |
| 5 | **ADR** | the accepted decision, numbered, immutable | `governance/adr/<NNNN>-*.md` |
| 6 | **Implementation** | source-of-truth order changes | `kernel/execution-model.md` |
| 7 | **Evidence** | proof recorded + confidence rated | `execution/pipelines/evidence-pipeline.md` |
| 8 | **Verification** | a gate evaluates the evidence | `execution/gates/` |
| 9 | **Accepted** | closure; ADR is the reference | evidence manifest |

## Threshold guidance
From `governance/DECISION_PROCESS.md` — a small change takes a commit + tests,
not an RFC. Use the full pipeline when the change is architectural, a security
posture change, a new capability, or cross-project.

## Rules
1. **No ADR without an RFC** for uncertain proposals; no RFC without a decision.
   A decision with no record is drift (`kernel/failure-model.md`).
2. **Immutable ADRs.** A superseded ADR is marked, never rewritten.
3. **Decisions reference evidence.** An ADR that claims a benefit has a step-7
   evidence pointer or the claim is `Unverified`.
4. **🔵 Proposed policies are decisions too.** A policy decision follows this
   pipeline's steps 1–5; the register status moves 🔵 → 🟡/⚪/❌
   (`domain/model/policies.md`).

## Checklist
See `execution/checklists/decision-checklist.md`.
