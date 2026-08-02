# Release Gate

The complete verification gate a release must pass. Run every step; stop on the
first failure.

## Steps (from `django-verifier` sub-agent)

1. `ruff check .` → `All checks passed!`
2. `bandit -r fleet config -q -ll` → exit 0
3. `pip-audit -r requirements.txt -r requirements-dev.txt` → no known vulns
4. `makemigrations --check --dry-run --settings=config.test_settings` → no drift
5. `compilemessages` → OK (needs gettext/msgfmt; CI installs it)
6. `manage.py test fleet --settings=config.test_settings --verbosity=2` →
   `Ran N tests ... OK` (278 at RC1; run detached on low-RAM machines)
7. `collectstatic --noinput --settings=config.test_settings` → exit 0
8. `check --deploy` with production-like env → exit 0 (warnings only)

## Pass criteria
- All 8 steps pass (or a step is documented as env-blocked with a CI
  substitute, e.g. compilemessages).
- Test count reported and recorded.

## Known env caveats
- `msgfmt` missing on Windows dev → compilemessages fails; CI installs gettext.
  Catalog integrity is still verified by `test_i18n_catalog`.
- `check --deploy` needs production env vars set for the run.
