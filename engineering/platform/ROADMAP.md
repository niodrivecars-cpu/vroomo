# Platform Roadmap

Phases are ordered by value, not by effort. Each phase should land as a commit
with evidence attached.

## Phase 1 — Foundation (current, RC1)

- [x] Layered structure: platform / governance / knowledge / patterns / domain /
      execution / verification / evidence / projects
- [x] Governance standards (principles, code review, quality, decision process)
- [x] ADR + RFC process with templates
- [x] Knowledge library seeded from Vroom lessons
- [x] Pattern library seeded with Vroom's real patterns
- [x] Execution: release/security/performance/migration gates + playbooks
- [x] Evidence system with RC1 as the first manifest

## Phase 2 — Business Rules Review

- [x] Domain documents per bounded context (booking, fleet, pricing, vehicle,
      driver, customer)
- [ ] Convert every business rule into executable tests (test-matrix)
- [ ] Edge-case catalogs wired into the test suite
- [ ] Business knowledge (knowledge/business/) as general reference

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
