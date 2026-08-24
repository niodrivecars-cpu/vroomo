# Project Instructions

Vroomo — multi-tenant fleet management system (vehicles, documents, drivers, bookings, maintenance, traffic violations). Django monolith, single app: `fleet`.

## Tech Stack
- Python 3.12 / Django 6.0.7, MySQL 8 via `dj-database-url` (`DATABASE_URL`) + PyMySQL
- django-bootstrap5 templates, django-ratelimit (+ Redis), Pillow, python-magic
- i18n: en / fr / ar (`locale/`, gettext catalogs)
- Deploy: gunicorn + Docker on Hostinger (`passenger_wsgi.py`, `scripts/deploy-hostinger.sh`)

## Commands
- Tests: `python manage.py test fleet --settings=config.test_settings --verbosity=2`
- Lint: `ruff check .`
- Security scan: `bandit -r fleet config -q -ll`
- Dependency audit: `pip-audit -r requirements.txt -r requirements-dev.txt`
- Migration drift check: `python manage.py makemigrations --check --dry-run --settings=config.test_settings`
- Dev server: `python manage.py runserver` (MySQL via `docker compose up -d`; or `.\setup.ps1`)
- Translations: `python manage.py compilemessages --ignore venv`

## Code Style
- ruff enforced (`ruff.toml`); no unused imports, keep it clean before committing
- Function-based views in `fleet/views.py`; business helpers live in dedicated modules (`pricing.py`, `downloads.py`, `security.py`, `audit.py`)
- All user-facing strings wrapped in gettext (`_()` / `gettext_lazy`); verbose names on every model field
- Single quotes for Python strings (match existing code)

## Architecture Rules
- Multi-tenant: every business model inherits `TenantScopedModel` (company FK, `fleet/models.py`). Never query tenant-scoped models without company filtering; views resolve `request.company` via `CompanyMiddleware`.
- Document downloads go through signed URLs (`get_signed_download_url`, `download_token_version` for revocation) — never expose raw media paths.
- File uploads validated by extension, size, and MIME type (`fleet/validators.py`).
- Audit trail is mandatory for state changes: use `fleet/audit.py` helpers (LOGIN, CREATE, UPDATE, DELETE, DOWNLOAD, PICKUP, RETURN...).
- Settings split: `config/settings/{base,development,production,test}.py`; all secrets via env/python-decouple, never hardcoded.

## Testing
- Django TestCase suite in `fleet/tests/` (`test_views.py`, `test_authz.py`, `test_idor.py`, `test_security.py`, ...). Run against `config.test_settings`.
- New features need tests covering authz + tenant isolation, not just happy path.
- k6 load/perf scripts live in `tests/performance/`.

## Workflow
- Branches: work on feature branches; releases via `release/1.0` → `main`. CI runs on both.
- Commits: conventional style — `type(scope): subject` (e.g. `fix(security): ...`, `feat(bookings): ...`).
- PR gate = full CI green: ruff + bandit + pip-audit + migration-drift + tests + `check --deploy`.
