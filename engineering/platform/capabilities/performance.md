# Capability: Performance

**Promise:** a release only ships with recorded, threshold-checked load results —
not with an assumption that "it's probably fast enough."

## Skills
- k6 smoke + attack profiles (`tests/performance/`).
- performance-gate — thresholds that must pass.
- `knowledge/load-testing/` — the methodology (fresh state, exit-0 + thresholds).

## Requirements
1. **Two profiles minimum.** A default smoke run and an attack run (adversarial:
   cross-tenant, expired/tampered/oversized requests, rate-limit abuse).
2. **Thresholds over impressions.** Every run asserts numeric thresholds
   (p95 latency, error counts, isolation invariants), not "looked fine."
3. **Fresh, reproducible state.** Runs need a restarted server + fresh cache/DB
   so results aren't poisoned by prior state.
4. **Results are archived** as evidence (see `evidence/performance/`).

## Vroom numbers (RC1)
- default: 358 checks, exit 0, p95 = 980.07 ms.
- attack: 415 checks, exit 0, p95 = 3.21 s.
- 9/9 thresholds green in both runs.

## Coverage
- Knowledge: `knowledge/performance/` + `knowledge/load-testing/`.
- Pattern: None — performance is measured, not patterned; the gate is the
  method.
- Checklist: `execution/gates/performance-gate.md`.
- Review step: performance review on gate results.
- Gate: performance-gate · Evidence: `evidence/performance/`.

## Gate
`execution/gates/performance-gate.md` — exit 0 AND all thresholds green in both
profiles.
