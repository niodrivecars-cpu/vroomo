# Performance — Best Practices

- **Set numeric thresholds, not impressions.** p95 latency, error counts,
  isolation invariants — every release asserts numbers (see
  `tests/performance/smoke.js`).
- **Run two profiles.** A default smoke run + an adversarial attack run
  (cross-tenant, expired/tampered/oversized, rate-limit abuse).
- **Fresh state per run.** Restart the server, clear cache, reset the DB so
  results aren't poisoned (see `docs/load-testing.md`).
- **Archive results.** Every run's output and summary become evidence
  (`evidence/performance/`).
- **Watch p95, not just mean.** Mean hides the tail that hurts users.

## Vroom baseline (RC1)
- default: 358 checks, p95 980.07 ms, exit 0.
- attack: 415 checks, p95 3.21 s, exit 0.
- 9/9 thresholds green in both.
