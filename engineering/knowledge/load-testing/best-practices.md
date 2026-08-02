# Load Testing Knowledge — Best Practices

- **Always run both profiles** (default + attack) before a release; they assert
  different things.
- **Fresh server + fresh cache/DB per run** — this is a hard requirement.
- **Assert error budgets as thresholds**, so transient artifacts don't pass
  silently.
- **One concurrency assertion per claim** — e.g. exactly-one-success for booking
  exclusivity, 0 isolation violations for tenant safety.
- **Archive run output + parsed summaries as evidence** (`evidence/performance/`).
- **Keep VU→user mapping safe under rate limits** — cap per-user work below the
  configured limit.
