# 03 — GitHub Actions (CI)

The CI workflow is `.github/workflows/ci.yml`. It is the quality gate for every
change on `main` and `release/1.0` (and every pull request). CI must be **green
before any deploy or tag**.

## When it runs

| Event | Runs CI? |
|---|---|
| Push to `main` | yes |
| Push to `release/1.0` | yes |
| Pull request (any base) | yes |
| Tag push (`v*`) | yes (on the tagged commit) |
| Other branches | no |

## What it does (single `test` job)

1. Spins up a **MySQL 8** service container (mirrors production Hostinger MySQL).
2. Installs dependencies (`requirements.txt` + `requirements-dev.txt`) and
   system packages (`gettext`, `libmagic1`).
3. **Lint:** `ruff check .`
4. **Security scan:** `bandit -r fleet config -q -ll`
5. **Dependency audit:** `pip-audit`
6. **Migration drift check:** `makemigrations --check --dry-run`
7. **Compile translations:** `compilemessages` (`.po` → `.mo`, all locales)
8. **Tests with coverage:** the full suite runs **against MySQL 8** via
   `DATABASE_URL=mysql://...`, then uploads `coverage.xml` as an artifact.
9. **Static files:** `collectstatic --noinput`
10. **Production settings check:** `check --deploy` with production-style env.

## What counts as a failure

The job fails if **any** step fails:
- any ruff issue, any bandit finding above `-ll`
- any known vulnerability from `pip-audit`
- any migration drift (`makemigrations --check` is not clean)
- any translation catalog mismatch
- **any test failure** — especially the concurrency/security ones
  (`same_vehicle_booking_success`, tenant isolation, rate limits)
- any `check --deploy` error

## Reading artifacts and coverage

- Coverage upload → the job's **Artifacts** section (`coverage.xml`).
- Download it and open locally, or wire **Codecov/Code Climate** later.
- Coverage policy: new behavior ships with tests that fail without the change
  (see `engineering/knowledge/testing/`).

## Practical notes

- The MySQL service health-check waits before tests run; a red job right after a
  fresh GitHub Actions outage is worth a re-run before debugging.
- **The MySQL CI run is the proof** that production-DB code works — the whole
  point of the RC1→RC2 fix was making this actually execute (PyMySQL pin, see
  `CHANGELOG.md`).

Next: `04-hostinger-auto-deploy.md`.
