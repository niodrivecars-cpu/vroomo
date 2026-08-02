# Security — Best Practices

- **Tenant isolation by construction.** Enforce at the view layer, defend at the
  query layer with `.filter(company=...)` on every access (see
  `patterns/multi-tenant/`).
- **Signed, expiring downloads.** Authorize + sign + expire + rate-limit, in that
  order (see `patterns/signed-download/`).
- **Rate limit auth and downloads.** Per resolved client IP, with configurable
  limits and correct `Retry-After`.
- **Audit security-relevant actions.** Login, download, and admin operations go
  to the audit log (see `patterns/audit/`).
- **Run the security gate on every release.** bandit `-ll`, pip-audit, security
  review, and the k6 attack profile are part of the evidence chain
  (`execution/gates/security-gate.md`).
- **Defense in depth.** Headers + cookies + CSRF + proxy trust + rate limits +
  signed downloads — layers, not a single wall.
