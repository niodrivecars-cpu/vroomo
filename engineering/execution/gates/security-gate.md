# Security Gate

The security bar a release must clear.

## Automated
1. `bandit -r fleet config -q -ll` → exit 0, no HIGH/MEDIUM findings.
2. `pip-audit -r requirements.txt -r requirements-dev.txt` → no known vulns.
3. Security-specific tests green: IDOR/cross-tenant (`test_views.py`), rate
   limits (`test_ratelimit.py`), client IP (`test_client_ip.py`), downloads
   (signed/expired/tampered/cross-tenant).

## Review (security-reviewer sub-agent + human)
- Tenant isolation on every new query (no IDOR path).
- Rate limits on auth + downloads; 429 always carries `Retry-After`.
- Downloads private, signed, expiring; no static exposure of documents.
- Client IP resolved from trusted proxies only (`TRUSTED_PROXY_IPS`).
- Audit covers security-relevant actions; no secrets in logs.
- CSRF, secure cookies, security headers per production settings.

## Load (attack profile)
k6 `ATTACK=1` run: exit 0, thresholds `tenant_isolation_violation == 0`,
`unexpected_http_4xx == 0`, `unexpected_http_5xx == 0`,
`login_429_without_retry_after == 0`, `download_body_mismatch == 0`.

## Pass criteria
All automated checks green, security review signed off, attack profile green.
Evidence recorded under `evidence/security/`.
