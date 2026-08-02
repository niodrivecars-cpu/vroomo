# Review Pipeline

The ordered sequence every change goes through. Automated first, human last.

## Stage 1 — Automated checks (fail → back to author)
1. `ruff check .` — lint.
2. `bandit -r fleet config -q -ll` — static security.
3. `pip-audit -r requirements.txt -r requirements-dev.txt` — dependencies.
4. `makemigrations --check --dry-run --settings=config.test_settings` — drift.
5. `compilemessages` — i18n (requires gettext; CI installs it).

## Stage 2 — Tests
6. `manage.py test fleet --settings=config.test_settings` — full suite
   (278 tests at RC1). Slow on low-RAM machines — run detached and poll.

## Stage 3 — Security review (if security-touching)
7. security-reviewer sub-agent + human: tenant isolation, IDOR, rate limits,
   CSRF, audit, downloads. See `governance/CODE_REVIEW_STANDARD.md`.

## Stage 4 — Human review
8. Review per `CODE_REVIEW_STANDARD.md`; record verdict.

## Stage 5 — Deploy-level checks
9. `collectstatic --noinput` and `check --deploy` (production env).
10. Load gate for performance-touching changes (k6 smoke + attack).

## Exit criteria
Every stage passes; results recorded as evidence. Nothing merges through a
skipped stage.
