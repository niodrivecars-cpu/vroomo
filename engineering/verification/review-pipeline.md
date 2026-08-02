# Review Pipeline (Verification)

The human-in-the-loop half of verification — how review produces T3 evidence.

## Roles
- **Author** — writes the change + tests + evidence claims.
- **Reviewer** — checks against `governance/CODE_REVIEW_STANDARD.md`.
- **Security reviewer** — for security-touching changes
  (`execution/checklists/security-review-checklist.md`).
- **Maintainer** — owns acceptance and the release verdict.

## Sequence
1. Automated stage (T1/T2) runs first — human time is not spent on lint.
2. Author states the evidence claims (which tests prove which behavior).
3. Reviewer verifies claims against tests + code (not "it should work").
4. Security review if security-touching.
5. Verdict recorded: approved / changes-requested, with rationale.

## Recording
Review verdicts and sign-offs are recorded (PR description or review artifact)
so evidence of review exists — part of the T3 tier.

## Review against evidence, not memory
When reviewing, the reviewer trusts only:
- Tests that fail without the change and pass with it.
- Scans and thresholds recorded for this commit.
- Standards written in `governance/`.
Not "we discussed this before" or "this is how we always do it."
