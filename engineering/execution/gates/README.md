# Gates

Pass/fail thresholds that protect releases. A gate is only satisfied by
evidence, not intention.

| Gate | Verifies | Key commands | Evidence |
|---|---|---|---|
| `release-gate.md` | Overall correctness | ruff, bandit, pip-audit, migrations, tests, collectstatic, check --deploy | `evidence/testing/`, `evidence/releases/` |
| `security-gate.md` | Security posture | bandit -ll, pip-audit, security review, k6 attack | `evidence/security/` |
| `migration-gate.md` | Schema integrity | makemigrations --check, migration review | — |
| `performance-gate.md` | Load behavior | k6 smoke + attack, thresholds | `evidence/performance/` |

## Platform-self gates (Phase 1.5)

Validate the platform itself, not a product release:

| Gate | Verifies | Evidence |
|---|---|---|
| `knowledge-consistency-gate.md` | No conflicts, no duplication, one term per concept, valid links | `evidence/verification/knowledge-consistency-<date>.json` |
| `capability-coverage-gate.md` | Every capability has standard + pattern + knowledge + checklist + review + gate + evidence | `evidence/verification/capability-coverage-<date>.json` |
| `business-traceability-gate.md` | Rule → Invariant → Code → Test → Evidence chain per business rule | `evidence/traceability/<project>-<stage>.json` |
