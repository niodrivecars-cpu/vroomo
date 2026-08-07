# Architecture Decision Records

Sequential, immutable decisions about the systems built on this platform.
Highest number is the most recent. Superseded records stay with a
`Status: superseded by NNNN` pointer. The relation map (affects / superseded by
/ implements / requires) lives in `GRAPH.md`.

| # | Title | Status | Date |
|---|---|---|---|
| 0001 | SQLite dev / Postgres production split | Superseded by 0006 | 2026-07 |
| 0002 | Private document downloads via signed, expiry-gated URLs | Accepted | 2026-07 |
| 0003 | Proxy-aware client IP resolution | Accepted | 2026-07 |
| 0004 | Rate limiting on auth and downloads | Accepted | 2026-07 |
| 0005 | SQLite write-lock retry for concurrent booking | Accepted | 2026-07 |
| 0006 | Production deployment strategy — Hostinger shared hosting | Accepted | 2026-08 |
| 0007 | GitHub as the single source of truth | Accepted | 2026-08 |

New ADRs: copy `TEMPLATE.md` to `NNNN-short-title.md`, follow
`../DECISION_PROCESS.md`.
