# Governance

How decisions are made on this platform: written standards first, evidence
always, and every consequential decision recorded.

## Decision rights

| Decision type | Who decides | Record |
|---|---|---|
| Routine code change | Author + automated gates | commit + tests |
| Code style / quality interpretation | Reviewer | review comment |
| Architecture or data-model change | Author proposes, maintainer approves | ADR |
| New capability / roadmap item | Product + engineering lead | RFC |
| Release | Release gate + maintainer sign-off | evidence manifest |

## Rules

1. **Evidence over assertion.** A claim about correctness, security, or
   performance must be backed by a recorded artifact (test, scan, run log).
2. **Standards are written.** If a rule matters, it lives in this directory —
   not in someone's head or a past conversation.
3. **Every consequential decision leaves a trace.** Use ADR for "we decided X",
   RFC for "we are considering Y", and evidence for "we proved Z".
4. **Disagreements resolve by evidence.** When reviewers disagree, the tiebreaker
   is a concrete test or measurement, not seniority.

## Reading order

1. `ENGINEERING_PRINCIPLES.md` — the principles everything else derives from.
2. `QUALITY_STANDARD.md` — what "done and correct" means.
3. `CODE_REVIEW_STANDARD.md` — how changes are reviewed.
4. `DECISION_PROCESS.md` — when/how to write an ADR or RFC.
5. `adr/` + `rfc/` — the records themselves.
