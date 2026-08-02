# ADR 0003: Proxy-aware client IP resolution

- **Status:** Accepted
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Rate limiting and audit logging depend on the real client IP. Behind nginx
(Hostinger VPS layout: nginx on `127.0.0.1` proxying to gunicorn), the app sees
proxy IPs unless `X-Forwarded-For` is trusted. Trusting it blindly lets clients
spoof any IP and bypass rate limits.

## Decision
Resolve client IP only from forwarding headers emitted by a configured,
trusted proxy set (`TRUSTED_PROXY_IPS`). All other forwarding headers are
ignored. Middleware implements this (see `fleet/middleware.py`); rate limiters
and audit use the resolved IP.

## Alternatives considered
- **Trust all X-Forwarded-For** — rejected: spoofing defeats rate limits.
- **Ignore proxies entirely** — rejected: all clients share the proxy IP,
  rate limits become useless.
- **nginx `proxy_set_header` only** — partial: correct header is set but the
  app still needs to trust only the right peer.

## Consequences
- **Positive:** accurate per-client rate limiting and audit IPs behind nginx.
- **Negative:** misconfiguration (missing `TRUSTED_PROXY_IPS`) degrades IP
  accuracy; the setting is required in production (documented in
  `.env.production.example`).
- **Trade-off accepted:** an explicit trust list is mandatory, enforced by docs.

## Evidence
`fleet/tests/test_client_ip.py` covers spoofed headers, untrusted peers, and
multi-hop chains.

## Compliance
Any IP consumed for security decisions (rate limit, audit) comes from the
proxy-aware resolver; `TRUSTED_PROXY_IPS` is set in production config.
