# Platform Capabilities

What the Engineering Platform provides to any product built on it. Each capability
has an owner document under `platform/capabilities/` and a matching skill in the
engineering toolchain. Full coverage contract per capability:
`platform/capabilities/README.md`.

| Capability | Delivers | Where |
|---|---|---|
| Architecture | Layered, testable structure with decision records | `capabilities/architect.md`, `governance/adr/` |
| Security | Hardened default posture, review pipeline | `capabilities/security.md`, `execution/gates/security-gate.md` |
| Review | Every change reviewed against a written standard | `capabilities/review.md`, `governance/CODE_REVIEW_STANDARD.md` |
| Performance | Load-tested releases with recorded thresholds | `capabilities/performance.md`, `execution/gates/performance-gate.md` |
| Release | Gated, evidence-backed releases | `capabilities/release.md`, `execution/playbooks/release-playbook.md` |
| Business Rule Review | Rules are the source of truth, traced to tests | `capabilities/business-rule-review.md`, `execution/gates/business-traceability-gate.md` |
| Verification | Proven correctness, not assumed correctness | `verification/` |
| Evidence | Queryable proof trail for every gate | `evidence/` |
| Knowledge | Captured lessons, reusable across projects | `knowledge/` |
| Patterns | Approved solutions with explicit trade-offs | `patterns/` |

## Capability Matrix (Vroom)

| Capability | Skill(s) | Gate | Evidence | Status |
|---|---|---|---|---|
| Security | security-reviewer, bandit, pip-audit | security-gate | `evidence/security/` | PASS (RC1) |
| Performance | k6 smoke + attack | performance-gate | `evidence/performance/` | PASS (RC1) |
| Testing | test-writer, django-tdd | release-gate | `evidence/testing/` | PASS (RC1, 278 tests) |
| Release | django-verifier | release-gate | `evidence/releases/v1.0.0-rc1.json` | DONE |
| Business Rule Review | business-rule-review, booking-domain-review | business-traceability-gate | `evidence/traceability/` | Phase 1.5 (gaps owned → Phase 2) |
