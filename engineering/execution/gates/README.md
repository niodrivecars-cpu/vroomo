# Gates

Pass/fail thresholds that protect releases. A gate is only satisfied by
evidence, not intention.

| Gate | Verifies | Key commands | Evidence |
|---|---|---|---|
| `release-gate.md` | Overall correctness | ruff, bandit, pip-audit, migrations, tests, collectstatic, check --deploy | `evidence/testing/`, `evidence/releases/` |
| `security-gate.md` | Security posture | bandit -ll, pip-audit, security review, k6 attack | `evidence/security/` |
| `migration-gate.md` | Schema integrity | makemigrations --check, migration review | — |
| `performance-gate.md` | Load behavior | k6 smoke + attack, thresholds | `evidence/performance/` |
