# Pattern: Signed Download

## Why we use it
Private files must be downloadable only by authorized users for a limited time,
with tenant ownership checks and rate limiting.

## When NOT to use it
- Files that are genuinely public (logos, marketing assets) — serve them from
  static/CDN.
- When you can rely on a storage CDN's own signed URLs end-to-end — but you still
  need the app-level authorization + tenant check on top.

## Trade-offs
- **Advantages:** fine-grained control, expiry, rate limiting, audit.
- **Disadvantages:** no plain-file URLs; every download goes through the app
  (CPU for signing/verification); more moving parts.
- **Alternatives:** public static (rejected: no control), CDN presigned (fine if
  the storage supports it; keep the authz gate).

## Vroom examples
- ADR 0002. Download view checks ownership → authorization → signed URL with
  expiry (`DOCUMENT_SIGNED_URL_TTL`) → rate limit.
- Tests: signed OK, expired 403, tampered 403, cross-tenant 404.
- k6 attack asserts `download_body_mismatch == 0` (body integrity) and
  `unexpected_http_4xx == 0`.

## Common mistakes
- Signing URLs with a weak/leaked secret.
- Expiry too long or absent.
- Skipping the ownership check because "the URL is signed."
- Streaming whole files into memory (use file streaming).

## Required tests
- Signed/expired/tampered/cross-tenant matrices (all four).
- Body integrity under load (`download_body_mismatch == 0`).

## Security review
Signature key is env-only and long; expiry is enforced server-side; ownership is
checked before signature validity (no signed-URL = access bypass); no secrets in
URLs (token is one-time or expiring, never credentials).

## Performance review
Downloads stream files, not buffer them; signing is cheap (HMAC); rate limits
prevent abuse; p95 latency threshold holds under attack profile.
