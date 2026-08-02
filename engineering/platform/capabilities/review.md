# Capability: Review

**Promise:** no change merges unseen. Every change is reviewed against a written
standard by code + security + test review, with the review result recorded.

## Skills
- security-reviewer (sub-agent) — security-focused review.
- test-writer (sub-agent) — ensures tests match conventions.
- CODE_REVIEW_STANDARD — the human checklist for every review.

## Requirements
1. **Automated first.** Ruff, bandit, pip-audit, migration check run before a
   human reviews.
2. **Security review for anything security-touching.** Auth, downloads, tenant
   scoping, rate limits, cookies — a security reviewer must sign off.
3. **Tests must match the change.** A behavior change without a test change is a
   review failure.
4. **Review result is recorded** (in the PR description or a review artifact),
   so evidence exists that review happened.

## Coverage
- Knowledge: `knowledge/testing/`.
- Pattern: None — review is a process, not a code solution.
- Checklist: `execution/checklists/code-review-checklist.md`.
- Review step: review-pipeline (reviewer) — this capability *is* the review.
- Gate: review-pipeline · Evidence: review artifacts.

## Gate
`execution/pipelines/review-pipeline.md` — the ordered sequence from automated
checks to human sign-off.
