# Security — References

- `fleet/security.py` — rate limiting + signed URL helpers.
- `fleet/middleware.py` — proxy-aware client IP.
- `fleet/audit.py` — audit logging.
- `fleet/tests/test_ratelimit.py`, `test_client_ip.py`, `test_views.py` (IDOR/cross-tenant/download tests).
- `config/settings/production.py` — security headers, cookies, CSRF.
- `execution/gates/security-gate.md` — the release security gate.
- ADRs 0002, 0003, 0004 under `governance/adr/`.
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org
