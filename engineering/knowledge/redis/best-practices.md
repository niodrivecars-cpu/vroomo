# Redis — Best Practices (planned)

- **Tenant-aware cache keys** — `tenant:<id>:<object>:<id>` never global keys
  for tenant data.
- **Set TTLs on everything** — a cache without expiry grows stale and unbounded.
- **Fail-open or fail-closed consciously** — decide, don't default; rate-limit
  store failures should fail closed (deny) for security.
- **Use it for reads, not for authority** — DB constraints still rule.
