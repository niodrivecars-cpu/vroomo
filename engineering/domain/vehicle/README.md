# Vehicle — Domain Docs

Supporting files for the vehicle domain. This domain shares the tenant-isolation
and document rules with `fleet/`; its specific concern is lifecycle and status.

## Index
- `business-rules.md` — vehicle rules, invariants, edge cases, test matrix.
- `invariants.md` — (V1–V3 consolidated in `business-rules.md`; separate file
  added here for consistency once Phase 2 formalizes them).
- `state-machine.md` — vehicle status transitions live in `fleet/state-machine.md`
  (shared with fleet domain).
- `edge-cases.md` — included in `business-rules.md`.
- `test-matrix.md` — included in `business-rules.md`.

## Relationship to other domains
- `booking/` constrains vehicle availability (B1 exclusivity).
- `fleet/` owns Vehicle's documents and maintenance.
