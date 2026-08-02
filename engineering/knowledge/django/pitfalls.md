# Django — Pitfalls

Mistakes that cost time on Vroom. Read before touching Django code.

## Settings and env
- **Running against the wrong settings** — `manage.py test` without
  `--settings=config.test_settings` falls back to the default DB and can hit
  your real data. Always pass `config.test_settings` for tests.
- **Forgetting `DEBUG=False` + `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS` for
  `check --deploy`** — the deploy check needs a full production-like env
  (SECRET_KEY, DB URL, allowed hosts) or it fails/misleads.
- **`SECRET_KEY` in code** — never; it lives in `.env` / `.env.production` only.

## Concurrency & the ORM
- **SQLite ignores `select_for_update`** (ADR 0005). Code that relies on it must
  prove exclusivity another way or be validated against Postgres.
- **`database is locked` on SQLite under concurrency** — surfaces as HTTP 200
  form re-render with no error markup; see `withSqliteRetry` in
  `tests/performance/common.js`. Not a production path.
- **Bulk save patterns** — don't assume `create()` is atomic against your
  business invariants; enforce invariants at the view/service layer and test.

## i18n
- **Editing `.po` files by hand** then shipping stale `.mo` breaks
  `test_mo_files_are_valid_and_in_sync_with_po`. Recompile with `compilemessages`
  (needs gettext/msgfmt).
- **RTL** — a translated string can flip layout. Mirrored pagination and LTR
  isolation were reworked for Arabic (see `knowledge/i18n/`).

## Migrations
- **Squashing/edit history** — migration files are part of the record; changing a
  shipped migration that others may have applied is a release bug.
- **Data drift** — `makemigrations --check --dry-run` must stay clean in CI.

## Middleware ordering
- Proxy-aware IP resolution must run before rate-limit/audit reads the client IP
  (see `fleet/middleware.py`). Ordering bugs silently break rate limiting.
