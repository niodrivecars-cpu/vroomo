# Hostinger Knowledge — Best Practices

- **Run `check --deploy` against production-like env** (DEBUG off, SECRET_KEY,
  DB URL, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS set).
- **Set `TRUSTED_PROXY_IPS=127.0.0.1`** for the nginx→gunicorn layout (ADR 0003).
- **Automate deploy/rollback** with `scripts/` and verify health after deploy.
- **Test restore before you need it.**
- **Keep `.env.production` secrets out of the repo**; only `.example` files are
  committed.
