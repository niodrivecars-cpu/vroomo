# Code Review Checklist

The human checklist applied to every code change, per
`governance/CODE_REVIEW_STANDARD.md`. The reviewer reviews against evidence, not
memory.

## Correctness
- [ ] The change does what its tests prove it does (red→green verified)
- [ ] No behavior change without a corresponding test change
- [ ] Edge cases from `domain/<context>/edge-cases.md` considered
- [ ] Existing invariants (B1–B6, F1–F6) not violated

## Tenancy & security (always)
- [ ] Every query tenant-scoped; no new IDOR surface
- [ ] No secrets, tokens, or PII logged
- [ ] Security-touching changes flagged for the security reviewer

## Style & structure
- [ ] Matches `patterns/` (use an approved pattern instead of inventing)
- [ ] Consistent with knowledge best-practices (`knowledge/`)
- [ ] No duplicate logic that a knowledge/pattern doc already covers

## Records
- [ ] Architecture/business impact → ADR/RFC record noted
- [ ] Review verdict recorded (PR description or artifact)

## Verdict
- [ ] Approved
- [ ] Changes requested (list them)
