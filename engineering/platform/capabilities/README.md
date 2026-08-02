# Capabilities

Each capability is a promise the platform makes to a project. It links the
standard (governance), the approved way (patterns), the execution step
(execution/gates), and the proof (evidence).

| Capability | Definition | Standards | Gate | Evidence |
|---|---|---|---|---|
| Architect | Testable, layered structure; decisions recorded | `ENGINEERING_PRINCIPLES.md` | release-gate | ADRs |
| Security | Hardened posture, reviewed changes | `security.md`, CODE_REVIEW_STANDARD | security-gate | `evidence/security/` |
| Review | Every change reviewed against a written standard | CODE_REVIEW_STANDARD | review-pipeline | review artifacts |
| Performance | Load-tested releases with thresholds | `performance.md` | performance-gate | `evidence/performance/` |
| Release | Gated, evidence-backed releases | QUALITY_STANDARD | release-gate | `evidence/releases/` |

See `platform/CAPABILITIES.md` for the matrix mapped to Vroom's RC1.
