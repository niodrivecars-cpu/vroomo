# Security — Pitfalls

- **Trusting `X-Forwarded-For` blindly** — lets any client spoof an IP and
  bypass rate limits. Trust only configured proxies (ADR 0003, `TRUSTED_PROXY_IPS`).
- **Serving private documents from static files** — kills tenant isolation,
  expiry, and audit in one stroke. Downloads go through the signed-URL view only
  (ADR 0002).
- **Cross-tenant access (IDOR)** — any query that doesn't filter by the current
  company can leak data. Every query must carry the tenant scope.
- **429 without `Retry-After`** — breaks clients that can't back off; k6 asserts
  `login_429_without_retry_after == 0`.
- **Logging secrets** — never log passwords, signed tokens, or session keys.
- **Weak/committed `SECRET_KEY`** — `check --deploy` flags keys under 50 chars;
  a CI placeholder is fine, a real one must be env-only.
- **Session cookies over insecure transport** — production enforces
  `SESSION_COOKIE_SECURE`.
