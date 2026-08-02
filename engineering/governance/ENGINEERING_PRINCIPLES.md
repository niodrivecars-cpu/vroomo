# Engineering Principles

The principles from which all other standards derive. If a standard contradicts a
principle, the principle wins and the standard is wrong.

## 1. Tenants are isolated by construction
Multi-tenant data must be scoped by the tenant at every access point. Isolation
is a structural guarantee, not a per-view afterthought. Defense in depth:
enforce at the view layer and defend at the query layer.

## 2. Security is a property, not a feature
Auth, rate limits, signed URLs, audit, and proxy trust are part of the default
posture — present from day one, not bolted on. Anything security-touching gets a
security review before merge.

## 3. Concurrency claims must be proven
If code claims to be safe under concurrency (exclusivity, rate limits, unique
constraints), a test must prove it under load. Assumptions here are where bugs
hide (SQLite ignores `select_for_update`; Postgres is the production truth).

## 4. Proof before release
A release is backed by evidence: static analysis, security scans, tests, and
load results. "It works on my machine" is a starting point, not a gate.

## 5. Decisions are written down
A decision without a record is a decision that will be silently re-litigated.
Architecture and data-model decisions get an ADR; big proposals get an RFC.

## 6. Simplicity is an asset
Prefer the boring, working solution. Add layers (services, CQRS, queues) only
when the current one demonstrably fails.

## 7. Knowledge outlives the conversation
Lessons learned live in `knowledge/` and `patterns/`, so the next project (and
the next engineer) starts from the answer, not the search.
