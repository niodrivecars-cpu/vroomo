# Platform Glossary

The platform's vocabulary, defined once. The Knowledge Consistency Gate
(`execution/gates/knowledge-consistency-gate.md`) treats any doc that uses a
different word for the same concept as a failure. When in doubt, use the term
here.

## Core concepts

| Term | Definition | Never call it |
|---|---|---|
| **Platform** | The Engineering Operating System: `engineering/` — how we build and prove products | "framework" |
| **Capability** | A promise the platform makes to a project (security, release, review…). Owned by a doc under `platform/capabilities/` | "skill" |
| **Skill** | Tooling that executes part of a capability (sub-agent, CLI, MCP server) | — |
| **Gate** | A pass/fail threshold with evidence; blocks a release if not met | "step", "check" |
| **Playbook** | An incident/decision-oriented procedure with branching (release, security incident) | "runbook" |
| **Runbook** | A routine, linear operational procedure (deploy, backup/restore) | "playbook" |
| **Checklist** | A pre-flight list used by a human or reviewer | "gate" |
| **ADR** | Accepted decision record; final and numbered | "RFC" |
| **RFC** | Change proposal, not yet accepted | "ADR" |
| **Evidence** | A recorded, timestamped proof artifact keyed to a commit | "result", "claim" |
| **Manifest** | A machine-readable evidence file (`evidence/**/*.json`) | — |

## Business vocabulary

| Term | Definition | Notes |
|---|---|---|
| **Business Rule** | A product requirement stated in business language | Lives in `domain/<context>/business-rules.md` |
| **Invariant** | A business rule restated as "holds at all times", numbered (B1, F1…) | Lives in `domain/<context>/invariants.md` |
| **Reference test** | An executable test that pins an invariant | Listed in `domain/<context>/test-matrix.md` |
| **Traceability** | The unbroken chain Rule → Invariant → Code → Test → Evidence | Verified by the Business Traceability Gate |
| **Tenant** | The isolation boundary; in Vroom this is **Company** | Vroom docs may say "company" — same concept |
| **Company** | Vroom's tenant model (`fleet/models.py`) | — |
| **Source of truth** | Business Rule → Invariant → Tests → Implementation; not the reverse | If code changes without the rule, tests must fail |
| **Bounded context** | A domain split: booking, fleet, pricing, vehicle, driver, customer | See `domain/` |

## Process vocabulary

| Term | Definition |
|---|---|
| **Gap** | A broken link in a traceability chain, or an uncovered capability slot. Must be recorded and owned before a gate passes |
| **Debt** | A rule that exists only in prose, or a capability slot explicitly deferred |
| **Supersede** | Replacing a stale record (ADR, evidence) with a pointer to its replacement; the old file is never rewritten |

## Mapping notes
- **capability/skill**: a capability declares *what* the platform guarantees; the
  skills listed inside it are *how* it executes (e.g. Capability Security → skill
  `security-reviewer`, bandit, pip-audit).
- **tenant/company**: Vroom's `Company` is the tenant. Platform docs say
  "tenant"; Vroom domain docs say "company". Both are correct in their layer.
- **playbook/runbook**: if the procedure branches on conditions or incidents →
  playbook. If it is a fixed sequence → runbook.
