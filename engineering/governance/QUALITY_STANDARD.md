# Quality Standard

What "done and correct" means on this platform.

## Definition of done

A change is done when:

1. **Implements** the intended behavior (including edge cases).
2. **Tests** cover it — new behavior has new/updated tests; they fail without the
   change and pass with it.
3. **Static analysis** clean: ruff, bandit `-ll`, pip-audit.
4. **Migrations** checked — no drift (`makemigrations --check`).
5. **i18n** respected: user-facing strings in catalogs, RTL layout honored.
6. **Security** reviewed for security-touching changes.
7. **Recorded** if consequential (ADR/RFC/domain doc).

## Quality bar by change size

| Change size | Required evidence |
|---|---|
| Trivial (typo, one-line fix) | automated checks |
| Normal feature | checks + tests |
| Cross-cutting | + security/performance review |
| Release | full gate + evidence manifest |

## Regression policy

- A regression must be fixed with a test that reproduces it, so it cannot recur
  silently.
- A failing suite blocks merge; no "merge and fix later."

## Release quality

Releases run the full gate (`execution/gates/release-gate.md`) and produce a
release manifest in `evidence/releases/`. The bar is not "no risks" but "known
risks are documented, understood, and appropriate for the release stage"
(candidate / pilot / production).
