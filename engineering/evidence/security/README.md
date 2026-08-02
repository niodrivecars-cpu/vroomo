# Security Evidence

Recorded security-gate artifacts (scans and reviews).

| Id | Commit | Status | Scan | Artifacts |
|---|---|---|---|---|
| `security/rc1-bandit` | `19a8d2f` | pass | bandit -r fleet config -q -ll (no HIGH/MEDIUM) | `verification.md` |
| `security/rc1-pip-audit` | `19a8d2f` | pass | pip-audit (no known vulnerabilities) | `verification.md` |

Full attack-profile load results in `performance/`. See
`engineering/execution/gates/security-gate.md` and
`engineering/execution/checklists/security-review-checklist.md`.
