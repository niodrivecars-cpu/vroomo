# ADR 0004: Rate limiting on auth and downloads

- **Status:** Accepted
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Login is a brute-force surface and document downloads are a bandwidth/abuse
surface. Unbounded access threatens tenant data and the VPS budget.

## Decision
Apply Django rate limiting:
- Login: per-client (resolved IP) limit with 429 feedback (no silent retry-after
  leak — verified by the k6 threshold `login_429_without_retry_after == 0`).
- Downloads: authenticated limit (`DOWNLOAD_RATE_LIMIT`, e.g. `20/h`) and an
  anonymous limit (`DOWNLOAD_ANON_RATE_LIMIT`, e.g. `10/h`).
Rate-limit keys use the proxy-aware client IP (ADR 0003).

## Alternatives considered
- **Application-level counters only** — rejected: fragile across processes.
- **Per-IP blocking at nginx** — partial: no per-user distinction, no 429 UX.
- **No limiting** — rejected outright.

## Consequences
- **Positive:** brute-force resistance, bounded download abuse.
- **Negative:** legitimate heavy users can be limited; limits are configurable
  via env so they can be tuned.
- **Trade-off accepted:** occasional 429 for automated/tools users in exchange
  for protection.

## Evidence
`fleet/tests/test_ratelimit.py`; k6 attack run asserted no 429-without-retry-after
and no unexpected 4xx/5xx.

## Compliance
Rate limits are active on login and download views; a 429 response never omits
`Retry-After`.
