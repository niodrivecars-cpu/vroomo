# Performance Evidence

Recorded load-gate artifacts for the performance gate.

| Id | Commit | Status | Key metric | Artifacts |
|---|---|---|---|---|
| `performance/rc1-default` | `19a8d2f` | pass | p95 980.07ms, 356/358 checks | `k6-default-output.txt`, `k6-default-summary.json` |
| `performance/rc1-attack` | `19a8d2f` | pass | p95 3.21s, 414/415 checks | `k6-attack-output.txt`, `k6-attack-summary.json` |

Raw outputs live in `docs/releases/v1.0.0-rc1/`; structured summaries are the
`*.json` files in this directory. See `engineering/execution/gates/performance-gate.md`.
