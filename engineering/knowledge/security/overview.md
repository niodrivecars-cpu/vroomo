# Security — Overview

The threat model and defense posture for multi-tenant Django services.

## What it is
Security is a property, not a feature (Principle #2). Every release carries a
security gate with automated scanners plus a dedicated security review for
anything security-touching.

## How it fits
- **Layers:** tenant isolation → auth → rate limiting → signed private downloads →
  audit → secure headers/cookies → proxy-aware client IP.
- **Tooling:** bandit (static), pip-audit (deps), security-reviewer sub-agent,
  k6 attack profile.
- **Records:** ADR 0002 (signed downloads), 0003 (client IP), 0004 (rate limits).

## Where it's heading
Full CSP enforcement after a Report-Only period; production observability
(Sentry). See `platform/ROADMAP.md`.
