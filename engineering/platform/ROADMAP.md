# Platform Roadmap

Phases are ordered by value, not by effort. Each phase should land as a commit
with evidence attached.

## Phase 1 — Foundation

- [x] Layered structure: platform / governance / knowledge / patterns / domain /
      execution / verification / evidence / projects
- [x] Governance standards (principles, code review, quality, decision process)
- [x] ADR + RFC process with templates
- [x] Knowledge library seeded from Vroom lessons
- [x] Pattern library seeded with Vroom's real patterns
- [x] Execution: release/security/performance/migration gates + playbooks
- [x] Evidence system with RC1 as the first manifest

## Phase 1.5 — Platform Validation

Validates the platform itself before it becomes the base for Phase 2. No new
product features — only platform coherence.

- [x] Glossary (`platform/GLOSSARY.md`) — one term per concept
- [x] Knowledge Consistency Gate — links, terminology, no duplication
- [x] Capability Coverage Gate — every capability fully slotted
- [x] Business Traceability Gate — Rule → Invariant → Code → Test → Evidence
- [x] New capability `business-rule-review` + its checklist
- [x] Code review checklist (closed the Review capability gap)
- [x] Traceability snapshot for Vroom (gaps owned → Phase 2)

## Phase 1.6 — Business Model Inventory (current)

A complete map of the business model **before** any rule discovery, so Phase 2
builds on one agreed model, not scattered code inferences.

- [x] Canonical Model (`domain/model/`): entities, relationships, state
      machines, events, commands, policies
- [x] Truthful inventory: Invoice/Payment marked not-modeled; Customer marked as
      value object; Vehicle has no `reserved` state
- [x] Business Completeness Gate — every entity has state machine + policies +
      events + commands + invariants + tests
- [x] Completeness matrix for Vroom (10 owned gaps C1–C10)

## Phase 2 — Business Rules Review

The goal is a **source of truth** for business rules, traced to code, tests,
and evidence. Built **on the canonical model** — discovery asks "is every policy
(P1–P21) valid, owned, and proven?" rather than "are there missing rules?".
Ordered parts:

### 2A. Business Rule Validation & Ownership
- [x] Governance register in `domain/model/policies.md`: every policy has
      Owner, Source, Criticality, Risk, Priority, and Decision status
      (✅ Enforced / 🟡 Validated / 🔵 Proposed / ⚪ Out of Scope / ❌ Rejected)
- [x] Use Cases in `domain/model/use-cases.md` (UC1–UC12) binding
      Use Case → Commands → Policies → Events → Tests
- [ ] Decide every 🔵 Proposed question: P8 (deposit ≤ value), P16
      (expired-doc blocks rental), P18 (per-company uniqueness), Customer as
      entity, Invoice/Payment in scope
- [ ] Reconcile `knowledge/business/` with the canonical policies
- [ ] Approve the validated-but-prose P0/P1 set — implementation happens in 2B.1

### 2A.5. Engineering Kernel & Rule Engine
The platform becomes self-governing before rule expansion continues — stops
Engineering Drift (see `kernel/failure-model.md`) so the platform can be reused
for Nio Drive without restructuring.

- [x] Engineering Kernel (`kernel/`): mission, principles, decision-tree,
      execution-model, confidence-model, failure-model
- [x] Business Rule Language (`kernel/rule-language.md`) — every policy P1–P21
      carries a formal `rule` block (PREDICATE / WHEN / UNLESS / EVIDENCE /
      RISKS / PRIORITY / SEVERITY / DECISION / ENFORCEMENT / OWNER / SOURCE)
- [x] Engineering Ontology (`kernel/ontology.md`) — formal relations between
      every platform concept
- [x] Capability Graph (`platform/capabilities/GRAPH.md`) — provides /
      depends_on / feeds relations
- [x] Evidence Engine (`execution/pipelines/evidence-pipeline.md`) —
      Evidence → Confidence → Risk → Decision → Approval (+ schema fields)
- [x] Decision Engine (`execution/pipelines/decision-pipeline.md` +
      decision-checklist) — Proposal → RFC → Discussion → ADR → Evidence → Accepted
- [x] Meta Engineering (`meta/` + `meta-review-gate.md`) — agents, prompts,
      knowledge, hallucination, duplication, consistency
- [x] Meta review evidence manifest (`evidence/verification/kernel-2026-08-02.json`)

### 2A.6. Executable Knowledge
Knowledge stops being prose: rule blocks are the single input, the Engineering
Compiler is the machine, graphs are the queryable view. The Decision Graph and
Policy Graph are **derived** — they never define new facts.

- [x] BRL v2 (`kernel/rule-language.md`) — the three dimensions: DECISION
      (agreed?) independent of ENFORCEMENT (real?), plus SEVERITY (break impact)
- [x] Engineering Compiler (`kernel/engineering-compiler.md`) — Parser →
      Validator → Generator → Artifacts (tests, threat model, checklist, docs,
      ADR references, review questions)
- [x] Validator executable: `kernel/compiler/validate_rules.py` — parses
      P1–P21, enforces fields/enums/uniqueness/decision↔enforcement, reports
      release blockers (PASS)
- [x] `policies.md` rewritten to v2 rule blocks (21/21), every Enforced policy
      at TESTED, validated gaps owned
- [x] Architecture Decision Graph (`governance/adr/GRAPH.md`) — ADR → affects /
      superseded by / implements → RFC
- [x] Policy Graph (`verification/traceability/vroom-graph.md`) — P* →
      implements → Invariant → tested by → Test → verified by → Evidence →
      approved by → Release
- [ ] Generate phase: per-rule test templates, threat models, checklists from
      the rule object (picks up in 2B.2)
- [ ] First RFC through the Decision Engine (none exist yet) to exercise the
      ADR graph `implements` edge

### 2B. Rule Engineering
Rules become executable artifacts in four ordered parts. Each part keeps the
source of truth: Rule → Invariant → Test → Evidence.

### 2B.1. Invariant Specification
- [ ] Convert every policy/invariant decision to a numbered invariant (B1…, F1…),
      including the prose-only validated set: P1 (maintenance blocks booking),
      P2 (active-only), P4 (license validity), P6 (mileage monotonic), P15
      (status ↔ bookings)
- [ ] Complete `domain/model/state-machines.md` for every decision
- [ ] Complete edge-case catalogs per context

### 2B.2. Rule Coverage
The per-rule compile loop: Rule → Code → Test → Evidence → Review → Release.
- [ ] For each rule: enforce in code, pin with a reference test, produce
      evidence, review the diff, keep the rule at TESTED
- [ ] Generators from 2A.6 produce the test templates; reference tests close
      G1–G8 (B3, B4, B5, B6, B1-adjacent, F5, maintenance-due, violation
      derived-state)
- [ ] Close the Rule → Model → View → Test → Evidence chain for every invariant
- [ ] Maintain the snapshot at `verification/traceability/vroom-<stage>.md`
      and re-run the Business Traceability Gate; 0 unowned gaps

### 2B.3. Business State Machines
Transition-level proof: each transition → guard → rule → test → evidence.
- [ ] State machines compiled per entity: Booking, Vehicle, Maintenance,
      Violation, VehicleDocument
- [ ] Every transition in `domain/model/state-machines.md` has a guard bound to
      a rule, a reference test, and evidence

### 2B.4. Scenario Library
End-to-end scenarios compiled from use cases (UC1–UC12) — e.g. Customer books →
Late return → Damaged → Insurance → Repair → Available.
- [ ] `domain/model/scenarios.md` — each scenario threads its use case, rules,
      state transitions, tests, and evidence
- [ ] Scenario coverage vs use cases: every UC has at least one scenario with a
      reference test

## Phase 3 — Autonomous Engineering

The platform drives its own rule → planning → agents → review → evidence →
decision → merge loop; humans approve decisions, not diffs.

- [ ] Rule-driven planning: a change enters as a rule/requirement, not a diff
- [ ] Agent loop with a decidable goal and a judge independent of the builder
- [ ] Automated evidence capture per change (confidence field set, not claimed)
- [ ] Merge gated on evidence + Meta Review, not on human inspection alone

## Phase 4 — Deployment Automation & Observability

Deployment stops being manual: a tag ships itself, the DR story is quantified,
and production is observable.

- [x] CI pipeline (`github/workflows/ci.yml`) — ruff, bandit, pip-audit,
      migration-drift, tests with coverage, collectstatic, `check --deploy`
- [x] Docker image (`Dockerfile` + build/push to GHCR in CI)
- [x] CD pipeline (`github/workflows/cd.yml`) — tag `v*` → SSH →
      `scripts/deploy.sh` → `/health/` → automatic `scripts/rollback.sh`
- [x] Zero-downtime deploys — graceful reload (`ExecReload` HUP) in
      `scripts/deploy.sh` + docs
- [x] Disaster recovery objectives documented (RPO ≤ 15 min target / RTO
      ≤ 30 min) with the current-reality gap called out in `docs/deployment.md`
- [x] Post-deploy monitoring checklist in `docs/deployment.md`
- [ ] Close RPO: Postgres WAL archiving + base backups (daily `backup.sh` = 24 h
      loss window today)
- [ ] Structured JSON logging + correlation IDs
- [ ] Sentry error tracking
- [ ] Metrics (Prometheus/Grafana) if volume justifies
- [ ] SLA/SLO definitions and dashboards
- [ ] Blue/Green deployment (when volume justifies two app slots)

## Phase 5 — Platform harden

- [ ] RFC/ADR index automation (check for missing records on changed architecture)
- [ ] Evidence CI job (re-run gates, refresh evidence/index.json)
- [ ] Cross-project adoption: spin up `projects/nio/`
- [ ] Playbook automation (release-playbook as runnable script)
- [ ] Knowledge Consistency Gate as a committed script (link checker)
