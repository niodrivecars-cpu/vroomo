# Hostinger Knowledge — Pitfalls

- **Missing `TRUSTED_PROXY_IPS`** → all clients share the nginx IP; rate limits
  and audit lose per-client accuracy (ADR 0003).
- **Session cookie over HTTP** → production must set `SESSION_COOKIE_SECURE`;
  check `--deploy` catches this.
- **`DEBUG=True` in prod** → catastrophic; `.env.production.example` is the guard.
- **Backup never tested** → a restore that fails when needed is worse than none;
  test restore.
- **`ALLOWED_HOSTS` not set** → host header attacks; set to real domain.
- **CSRF behind proxy** → `CSRF_TRUSTED_ORIGINS` needed for the real origin.
