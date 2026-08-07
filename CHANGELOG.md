# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- (planned) Sentry error tracking — documented, not yet configured.
- (planned) Hourly backups to close the RPO window on shared hosting.

### Changed

- (planned) MariaDB-vs-MySQL pin decision on Hostinger once the hPanel database
  flavor is confirmed.

### Fixed

- (planned) Verify the hPanel **Python App** option exists before first deploy.

## [1.0.0-rc2] - 2026-08-07

### Added

- Preflight checklist (Go/No-Go gate) — `docs/deployment/preflight-checklist.md`.
- Post-deployment validation guide — `docs/deployment/post-deploy-validation.md`.
- v1.0 release checklist — `docs/releases/v1.0-release-checklist.md`.
- Explicit MySQL migration declaration in `engineering/knowledge/mysql/overview.md`
  and `docs/deployment/hostinger-business.md` §11, so no new developer assumes a
  PostgreSQL dependency.

### Changed

- Production platform officially aligned with **Hostinger Business Shared**
  (Passenger + MySQL/MariaDB, no sudo/systemd/Docker/Redis).
- Development and CI environments migrated to **MySQL 8** (`docker-compose.yml`,
  `setup.ps1`, `README.md`, CI service container).
- GitHub Actions CI now validates against MySQL 8 instead of PostgreSQL.
- `knowledge/postgres/overview.md` renamed to `knowledge/mysql/overview.md`;
  remaining Postgres knowledge and the Postgres MCP are marked legacy/disabled.
- Hostinger deployment guide promoted to the primary deployment reference;
  the VPS layout (`docs/deployment.md`) is kept as a reference path.
- PostgreSQL no longer a production dependency — `psycopg2-binary` replaced by
  `PyMySQL` (Postgres path retained only in backup/restore scheme-branching).

### Fixed

- **PyMySQL pinned to 1.2.0** to satisfy Django 6.0's `mysqlclient >= 2.2.1`
  backend check. PyMySQL 1.1.1 reports `version_info=(1,4,6)` and failed to load
  the MySQL backend at import time (`ImproperlyConfigured`); 1.2.0 reports
  `(2,2,8)` and passes. This is what makes the "CI green on MySQL" claim true —
  the MySQL CI run had not actually executed before this fix.
- Release checklist now guards against dependency regression (the PyMySQL pin is
  a first-class pre-tag item).

### Removed

- Postgres-based local dev stack (Docker `postgres:16` service, Postgres env
  defaults in the README, enabled Postgres MCP).

### Security

- Booking exclusivity (`select_for_update`) verified to hold on MySQL/InnoDB,
  matching the PostgreSQL-era guarantee.
- Rate limiting, CSRF, signed/expiry-gated downloads, and audit logging remain
  unchanged from RC1.

## [1.0.0-rc1] - 2026-08-02

### Added

- Multi-tenant fleet management SaaS: drivers, vehicles, bookings, documents,
  financial transactions (Arabic RTL, i18n ar/fr/en).
- Security hardening: auth, rate limits, CSRF, secure headers, signed and
  expiry-gated private document downloads, audit logging, proxy-aware client-IP
  resolution.
- k6 load-testing framework (smoke + attack profiles).
- Production settings split, static/media handling, Hostinger VPS deployment
  documentation.

### Changed

- (n/a — initial release candidate.)

### Fixed

- Concurrency: `transaction.atomic()` + `select_for_update` on booking create/edit
  to enforce vehicle exclusivity (ADR 0005 retry layer for the SQLite dev backend).

### Security

- Load-gate proof: 2 k6 runs (default + attack), all thresholds green, 0
  overlapping bookings, 0 tenant-isolation violations, 0 rate-limit denials.
