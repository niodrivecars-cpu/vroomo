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
(P1–P21) represented?" rather than "are there missing rules?". Four parts:

### 2A. Business Rule Discovery
- [ ] Enforce-or-decide every 🔲 policy: P1 (maintenance blocks booking),
      P2 (active-only), P4 (license validity), P6 (mileage monotonic),
      P8 (deposit ≤ value), P15 (status ↔ bookings)
- [ ] Decide every 🧾 question: P16 (expired-doc blocks rental), P18
      (per-company uniqueness), Customer as entity, Invoice/Payment in scope
- [ ] Reconcile `knowledge/business/` with the canonical policies

### 2B. Invariant Specification
- [ ] Convert every policy/invariant decision to a numbered invariant (B1…, F1…)
- [ ] Complete `domain/model/state-machines.md` for every decision
- [ ] Complete edge-case catalogs per context

### 2C. Traceability
- [ ] Close the Rule → Model → View → Test → Evidence chain for every invariant
- [ ] Maintain the snapshot at `verification/traceability/vroom-<stage>.md`
- [ ] Re-run the Business Traceability Gate; 0 unowned gaps

### 2D. Reference Tests
- [ ] Write reference tests for every invariant
- [ ] Known gaps to close first: B3 (window validity), B4 (money non-negative),
      B5 (state machine), B6 (PROTECT), B1 "adjacent windows", F5 (file
      hygiene), maintenance-due, violation derived-state, plus new policies
      enforced in 2A (P1, P2, P4, P6, P8, P15)
- [ ] Full closure: every invariant green for the commit

## Phase 3 — Observability

- [ ] Structured JSON logging + correlation IDs
- [ ] Sentry error tracking
- [ ] Metrics (Prometheus/Grafana) if volume justifies
- [ ] SLA/SLO definitions and dashboards

## Phase 4 — Platform harden

- [ ] RFC/ADR index automation (check for missing records on changed architecture)
- [ ] Evidence CI job (re-run gates, refresh evidence/index.json)
- [ ] Cross-project adoption: spin up `projects/nio/`
- [ ] Playbook automation (release-playbook as runnable script)
- [ ] Knowledge Consistency Gate as a committed script (link checker)
