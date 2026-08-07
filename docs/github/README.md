# GitHub & Deployment Onboarding

The reference path for anyone joining Vroom or taking the project from
"local repo" to "first production release" on Hostinger Business.

| Doc | Purpose |
|---|---|
| `01-create-repository.md` | Create the GitHub repo, link `origin`, protect branches |
| `02-branch-strategy.md` | Branch model, merge policy, commit convention |
| `03-github-actions.md` | What CI runs, when, and what counts as failure |
| `04-hostinger-auto-deploy.md` | Connect GitHub → Hostinger → first live deploy |
| `05-first-release.md` | Full sequence to the first tag + GitHub Release |
| `06-troubleshooting.md` | Common CI / DB / Passenger / HTTPS failures |

Companion docs:

- `docs/deployment/preflight-checklist.md` — Go/No-Go gate before deploy
- `docs/deployment/post-deploy-validation.md` — after-deploy checks
- `docs/releases/v1.0-release-checklist.md` — the release process
- `CHANGELOG.md` — version history (Keep a Changelog)
- ADR 0006 (Hostinger strategy), ADR 0007 (GitHub as single source of truth)
