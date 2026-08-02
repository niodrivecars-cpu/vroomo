# Release Report — v1.0.0-rc1

**Project:** Vroom — multi-tenant fleet management
**Tag:** `v1.0.0-rc1` · **Branch:** `release/1.0` · **Date:** 2026-08-02
**Commit:** `2fb8606` (the commit that passed every gate below)

## Scope

| Area | Status |
|---|---|
| Multi-tenancy (vehicle/document bookings, tenant boundary enforcement) | Done — attack-tested |
| Security hardening (auth, signed/expiry-gated downloads, audit, rate limits, CSRF, secure headers) | Done |
| Proxy-aware client IP resolution | Done |
| i18n infrastructure (ar/fr/en catalogs) | Done |
| Deployment config (production settings, static, Hostinger VPS) | Done |
| Load-testing framework (k6, smoke + attack profiles) | Done |
| Documentation | Done |

## Gates

- Static/unit/CI gate: **PASS** — see `verification.md` (ruff, bandit, pip-audit, no migration drift, 278 tests OK, collectstatic, `check --deploy`).
- Load gate: **PASS** — two k6 smoke runs (default + attack), both exit 0, all 9 thresholds green.
  - Default: 356/358 checks, p95 980 ms.
  - Attack (cross-tenant, expired/tampered/oversized downloads): 414/415 checks, p95 3.21 s.
  - 2/1 residual check failures were the SQLite dev-backend write-lock artifact (HTTP 200 form re-render, no row persisted); error thresholds (`unexpected_http_4xx/5xx`, `booking_http_500`) all 0.
  - Post-attack DB audit: 46 bookings, 0 overlapping pairs, 0 rate-limit denials.

## Artifacts

- `k6-default-output.txt` / `k6-attack-output.txt` — full console output.
- `k6-default-summary.json` / `k6-attack-summary.json` — parsed thresholds, checks, and metrics.
- `verification.md` — full verification-gate details and how to reproduce.
- Source logs + post-attack SQLite snapshot archived (see `docs/load-testing.md`).

## Known caveats

- `compilemessages` requires GNU gettext (`msgfmt`); installed in CI, not on the dev machine. Catalog integrity is enforced by the test suite (`test_i18n_catalog`).
- Load gate ran against the SQLite test backend on a dev machine (1 GB free RAM); Postgres on the Hostinger VPS has no `select_for_update` swallow path, so the SQLite-lock artifact is dev-only.

## Verdict

**Release Candidate 1 — ready for external review.** Tagged only after the load gate (the final operational gate) passed with recorded evidence.
