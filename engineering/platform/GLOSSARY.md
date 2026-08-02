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
| **Canonical Model** | The single official definition of the business model (`domain/model/`) | Everything else references it; nothing redefines it |
| **Entity** | A thing with identity and lifecycle (Vehicle, Booking, Driver…) | Defined in `domain/model/entities.md` |
| **Policy** | A business policy: what must/must not happen (P1…) | The source of truth in `domain/model/policies.md` |
| **Policy owner** | The accountable person/role for a policy (Fleet Manager, Finance…) | Recorded per policy in `policies.md` |
| **Policy source** | Where a policy comes from: Law, Business Requirement, Operational Practice, Internal Decision, Security Requirement | Recorded per policy in `policies.md` |
| **Policy status** | The decision state of a policy: ✅ Enforced, 🟡 Validated, 🔵 Proposed, ⚪ Out of Scope, ❌ Rejected | See `domain/model/policies.md` |
| **Policy risk** | Impact dimensions of a policy: Operational, Financial, Security, Legal, Customer Experience | Recorded per policy in `policies.md` |
| **Policy priority** | Work-order tier (P0–P3), assigned by risk, not by policy number | See the priority matrix in `policies.md` |
| **Use Case** | An end-to-end business scenario (UC1…) binding Commands → Policies → Events → Tests | Cataloged in `domain/model/use-cases.md` |
| **Kernel** | The brain of the platform: how we think (mission, principles, decision tree, execution model, confidence, failure) | `engineering/kernel/` |
| **Business Rule Language (BRL)** | The formal, machine-readable statement of a policy (rule block) from which invariants, tests, docs, playbooks, threat models, and code derive | Spec in `kernel/rule-language.md` |
| **Predicate** | The formal boolean expression of a rule (`NOT exists(Booking b: overlaps(b, new))`) — the invariant form, one of the three rule dimensions | BRL v2, replaces v1's `GUARD` |
| **Severity** | The break-impact of a rule: `BLOCKER` · `ERROR` · `WARNING` · `INFO` — a `BLOCKER` below `TESTED` blocks a release | BRL v2 field |
| **Enforcement** | The implementation reality of a rule: `PLANNED` · `DOCUMENTED` · `IMPLEMENTED` · `TESTED` — independent of `DECISION` | BRL v2 field |
| **Engineering Compiler** | The machine that turns a rule block into every downstream artifact: Parser → Validator → Generator → (tests, threat model, checklist, docs, ADR references, review questions) | `kernel/engineering-compiler.md`, executable at `kernel/compiler/validate_rules.py` |
| **Decision Graph** | The relation map of architecture decisions: ADR → `affects` / `superseded by` → ADR, ADR → `implements` → RFC | `governance/adr/GRAPH.md` |
| **Policy Graph** | The end-to-end proof chain per policy: P* → `implements` → Invariant → `tested by` → Test → `verified by` → Evidence → `approved by` → Release | `verification/traceability/vroom-graph.md` |
| **Ontology** | The formal relations between platform concepts (Entity → Aggregate → Policy → Rule → Invariant → Test → Evidence → Decision) | `kernel/ontology.md` |
| **Capability Graph** | The relation map of capabilities (provides / depends_on / feeds) | `platform/capabilities/GRAPH.md` |
| **Confidence** | How much a claim is trusted (Unverified → Recorded → Tested → Gated → Proven) | `kernel/confidence-model.md` |
| **Evidence Engine** | The pipeline Evidence → Confidence → Risk → Decision → Approval | `execution/pipelines/evidence-pipeline.md` |
| **Decision Engine** | The decision workflow Proposal → RFC → Discussion → ADR → Implementation → Evidence → Accepted | `execution/pipelines/decision-pipeline.md` |
| **Meta Review** | Review of the platform itself (agents, prompts, knowledge, gates) | `engineering/meta/`, `execution/gates/meta-review-gate.md` |
| **Drift** | The platform failing its own discipline (documentation drift, gate theater, evidence rot, …) | `kernel/failure-model.md` |
| **Event** | A business fact, past tense (BookingPickedUp) | Cataloged in `domain/model/events.md` |
| **Command** | An allowed action with a guard (CreateBooking) | Cataloged in `domain/model/commands.md` |
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
