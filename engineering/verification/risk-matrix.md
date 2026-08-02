# Risk Matrix

Categorizing residual risk and deciding if it's acceptable for the release
stage.

## Impact × Likelihood
| | Rare | Unlikely | Possible | Likely |
|---|---|---|---|---|
| **Critical** | Track | Track | Block | Block |
| **High** | Track | Track | Review | Block |
| **Medium** | Accept | Track | Review | Review |
| **Low** | Accept | Accept | Accept | Track |

- **Accept** — documented, no action needed now.
- **Track** — recorded as debt/roadmap item.
- **Review** — needs a mitigating review or explicit sign-off.
- **Block** — cannot release until resolved.

## Known Vroom risks (at RC1)
| Risk | Impact | Likelihood | Cell | Decision |
|---|---|---|---|---|
| SQLite dev artifact masks concurrency behavior | High | Possible | Review | Mitigated: ADR 0005 retry + Postgres validation plan |
| Missing per-company uniqueness (plates/CINs) | Medium | Unlikely | Track | Tracked in Business Rules Review |
| No production observability yet | High | Unlikely | Track | Phase 3 (Sentry/metrics) |
| Business rules not yet fully reference-tested | High | Possible | Review | Phase 2 (Business Rules Review) |
| Full CSP deferred (Report-Only) | Medium | Unlikely | Track | Roadmap |
| No production load data on Postgres | Medium | Possible | Review | Pilot phase measurement |

## Acceptance criteria
A release stage is "accepted" when no cell is **Block** for that stage, and all
**Review** cells have a recorded mitigation or explicit sign-off in the release
notes.
