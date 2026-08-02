# Django — Best Practices

Rules that consistently worked on Vroom.

## Settings hygiene
- Split settings: base / test / production; keep env secrets out of code.
- Test settings: `:memory:` SQLite, MD5 password hashers (fast tests),
  `InMemoryStorage` (no disk) — see `config/settings/test.py`.
- Production: `DEBUG=False`, `SECURE_*` cookies, security headers, Postgres URL.

## Structure
- Keep views thin; push cross-cutting concerns into helpers
  (`fleet/security.py`, `fleet/audit.py`, middleware) so they are applied
  consistently, not reimplemented per view.
- Tenant scoping is a helper you reuse on every query — never inline-and-forget.

## Testing
- One test file per concern under `fleet/tests/` (`test_views`, `test_ratelimit`,
  `test_client_ip`, `test_i18n_catalog`).
- Tests run against `config.test_settings`; concurrency tests are explicit and
  load-verified.
- Security-related tests are first-class: IDOR, cross-tenant, expired/tampered
  downloads, rate-limit behavior.

## Verification
- Every non-trivial change runs: ruff → bandit → pip-audit → migration check →
  full test suite → collectstatic → `check --deploy`.
- Concurrency claims get a load-test proof (`same_vehicle_booking_success == 1`).
