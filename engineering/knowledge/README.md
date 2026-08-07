# Knowledge Library

What we know — written once, reused across every project on the platform. This
is distinct from `patterns/` (approved solutions) and `domain/` (business rules).

## Structure

Every topic folder follows the same 4-file shape:

```
topic/
  overview.md        What it is and how it fits
  pitfalls.md        Mistakes that cost us time
  best-practices.md  The patterns and rules that work
  references.md      Links, docs, and where to look next
```

## Topics

| Topic | Scope |
|---|---|
| `django/` | Framework conventions, settings split, middleware, ORM |
| `mysql/` | Production DB truth, concurrency, migrations (since 2026-08, ADR 0006) |
| `postgres/` | Legacy reference — the VPS-era production DB; superseded by `mysql/` |
| `redis/` | Caching (planned) |
| `security/` | Threat model, headers, rate limiting, audit |
| `performance/` | What makes it slow, what to measure |
| `testing/` | Test strategy, fixtures, coverage policy |
| `fleet/` | Fleet domain model knowledge |
| `booking/` | Booking domain model knowledge |
| `pricing/` | Pricing domain model knowledge |
| `i18n/` | Locale handling, RTL, translation catalogs |
| `hostinger/` | Deployment environment specifics |
| `load-testing/` | k6 methodology and thresholds |
| `business/` | Cross-domain business patterns |
