# Performance — Pitfalls

- **SQLite vs MySQL latency** — dev numbers (SQLite) understate MySQL
  network/connection cost; benchmark on MySQL for real conclusions.
- **Indexing tenant scoping columns** — a `company_id` filter without an index
  degrades with tenant data growth.
- **Loading entire documents into memory** — large signed downloads stream; don't
  `read()` whole files into RAM.
- **Per-request work that's cacheable** — repeated catalog lookups, signed-URL
  re-derivation, etc. become waste under load (Redis is on the roadmap).
- **Swallowed errors under concurrency** — the SQLite lock artifact looks like a
  "slow" 200; always verify error paths separately (error-budget thresholds).
