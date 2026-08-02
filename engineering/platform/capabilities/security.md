# Capability: Security

**Promise:** the product ships with a hardened default posture, and every change
is checked against known vulnerability classes before it merges.

## Skills
- security-reviewer (sub-agent) — tenant-isolation/IDOR/ratelimit/CSRF/audit review.
- bandit (static) + pip-audit (dependencies) — automated scanners.
- `patterns/multi-tenant/`, `patterns/audit/`, `patterns/signed-download/` — approved solutions.

## Requirements
1. **Rate limiting** on auth and downloads (Vroom: login + download limits,
   `fleet/security.py`).
2. **Private downloads** behind signed, expiry-gated URLs; no public static
   exposure of documents.
3. **Audit logging** for security-relevant actions (login, download, admin ops).
4. **Proxy-aware client IP** — the app only trusts `X-Forwarded-For` from
   configured peers (`TRUSTED_PROXY_IPS`); see `fleet/middleware.py`.
5. **Security headers + CSRF + secure cookies** per `config/settings/production.py`.
6. **Tenant isolation tests** are part of the suite, not optional.

## Coverage
- Knowledge: `knowledge/security/`.
- Patterns: `multi-tenant/`, `audit/`, `signed-download/`.
- Checklist: `execution/checklists/security-review-checklist.md`.
- Review step: security-reviewer sub-agent sign-off.
- Gate: security-gate · Evidence: `evidence/security/`.

## Gate
`execution/gates/security-gate.md` — bandit `-ll`, pip-audit clean, security
reviewer pass, IDOR/tenant tests green.
