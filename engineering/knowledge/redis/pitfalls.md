# Redis — Pitfalls (planned)

Placeholder — populate when Redis lands. Anticipated pitfalls to avoid:

- **Cache invalidation gaps** — a stale tenant-scoped cache can leak old data
  across tenants if keys aren't tenant-aware.
- **Rate limiting in-process vs shared** — per-worker counters undercount when
  gunicorn runs multiple workers; use a shared store for coordinated limits.
- **Cache-as-truth** — never let the cache become the source of truth for
  business rules.
- **Unbounded keys** — key by tenant + object, and set TTLs.
