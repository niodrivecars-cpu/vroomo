# Security Review Checklist

Used by the security reviewer for any security-touching change.

## Tenant isolation
- [ ] Every new query is company/tenant scoped (no IDOR)
- [ ] Cross-tenant read/write/delete tested (403/404)
- [ ] Cache keys tenant-aware

## Auth & sessions
- [ ] Rate limit on login; 429 carries `Retry-After`
- [ ] Session cookies secure in production
- [ ] No role/permission bypass

## Downloads
- [ ] Private files only via signed, expiring URLs
- [ ] Ownership + authorization before signature validity
- [ ] Expired/tampered/cross-tenant cases tested (403/404)
- [ ] Body integrity asserted under load (`download_body_mismatch == 0`)

## Client IP
- [ ] IP resolved from trusted proxies only (`TRUSTED_PROXY_IPS`)
- [ ] Spoofed-header tests green

## Audit & logging
- [ ] Security actions audited with company + session context
- [ ] No secrets/passwords/tokens logged

## Headers & config
- [ ] Production: DEBUG off, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, secure cookies
- [ ] No secrets committed; `.env` ignored
