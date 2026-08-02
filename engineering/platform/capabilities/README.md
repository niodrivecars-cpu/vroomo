# Capabilities

Each capability is a promise the platform makes to a project. It links the
standard (governance), the approved way (patterns), the execution step
(execution/gates), and the proof (evidence). The Capability Coverage Gate
(`execution/gates/capability-coverage-gate.md`) enforces that every slot below
is filled or explicitly "None — rationale".

## Coverage Matrix

| Capability | Knowledge | Pattern | Checklist | Review step | Gate | Evidence |
|---|---|---|---|---|---|---|
| Architect | `knowledge/django/`, `platform/ARCHITECTURE.md` | None — the capability *is* the structure, not a code solution | `execution/checklists/task-template.md` | maintainer sign-off on ADRs | release-gate | ADRs, `platform/ARCHITECTURE.md` |
| Security | `knowledge/security/` | `multi-tenant/`, `audit/`, `signed-download/` | `security-review-checklist.md` | security-reviewer sub-agent | security-gate | `evidence/security/` |
| Review | `knowledge/testing/` | None — review is a process, not a code solution | `code-review-checklist.md` | review-pipeline (reviewer) | review-pipeline | review artifacts |
| Performance | `knowledge/performance/`, `knowledge/load-testing/` | None — performance is measured, not patterned; see `performance-gate.md` | `performance-gate.md` | performance review on gate results | performance-gate | `evidence/performance/` |
| Release | `knowledge/hostinger/` | None — release is a procedure; see `release-playbook.md` | `release-checklist.md` | release-playbook sign-off | release-gate | `evidence/releases/` |
| Business Rule Review | `knowledge/business/`, `domain/` | None — rule review is a methodology; see `business-traceability-gate.md` | `business-rule-review-checklist.md` | business-rule-review sub-agent | business-traceability + business-completeness gates | `evidence/traceability/`, `evidence/verification/` |

## Capability files

- `architect.md` — testable, layered structure; decisions recorded.
- `security.md` — hardened posture, reviewed changes.
- `review.md` — every change reviewed against a written standard.
- `performance.md` — load-tested releases with recorded thresholds.
- `release.md` — gated, evidence-backed releases.
- `business-rule-review.md` — rules are the source of truth, traced to tests.

See `platform/CAPABILITIES.md` for the matrix mapped to Vroom's RC1.
