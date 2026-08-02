# ADR 0002: Private document downloads via signed, expiry-gated URLs

- **Status:** Accepted
- **Date:** 2026-07
- **Author:** Vroom team

## Context
Vehicle documents must be private: only authorized tenants and users may
download them, and access must expire. Public static file serving is
unacceptable for documents (customer licenses, registration).

## Decision
Store document files in private storage; serve downloads only through a view
that (1) checks tenant ownership, (2) checks user authorization, (3) validates a
signed URL with an expiry (`DOCUMENT_SIGNED_URL_TTL`), and (4) enforces
per-user/per-anonymous download rate limits. See `patterns/signed-download/`.

## Alternatives considered
- **Public static serving** — rejected: no tenant isolation, no expiry, no audit.
- **In-DB storage** — rejected: unnecessary DB bloat, no streaming benefit.

## Consequences
- **Positive:** tenant-isolated, expiring, rate-limited, auditable downloads.
- **Negative:** download flow is not a plain file URL; frontends must request
  signed URLs. Offline/curl access requires the signing mechanism.
- **Trade-off accepted:** complexity of the signing flow in exchange for control
  over private data.

## Evidence
`fleet/tests/test_views.py` download tests (signed/expired/tampered/cross-tenant);
k6 attack run asserted cross-tenant download returns 404 and expired/tampered
return 403.

## Compliance
No document file is served from static; every download passes the authorized +
signed + expired + rate-limited view. Attack thresholds enforce
`download_body_mismatch == 0`, `unexpected_http_4xx == 0`.
