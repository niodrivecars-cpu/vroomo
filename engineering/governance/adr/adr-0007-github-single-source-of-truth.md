# ADR 0007: GitHub as the Single Source of Truth

- **Status:** Accepted
- **Date:** 2026-08-07
- **Author:** Vroom team

## Context
The project has a working local repo and a Hostinger Business shared-hosting
target (ADR 0006), but no remote yet. CI (MySQL 8) exists but has never run
because there is nowhere to push. Without a canonical remote, the team would
fall back to ad-hoc deploys (SSH, manual file uploads), losing the evidence and
governance built so far (gates, ADRs, verification). Vroom needs one authoritative
copy of the code, one place where every change is reviewed and tested, and a
deploy path that is repeatable and auditable.

## Decision
**GitHub is the single source of truth for Vroom's code, releases, and
deployment trigger.**

- GitHub is the only canonical remote (`origin`). The repo is created with no
  auto-init (the local history is the seed) and pushed to `release/1.0`.
- **No manual production deploys outside GitHub-driven automation.** Deploys to
  Hostinger are triggered by the GitHub connection (auto-deploy on push to the
  selected branch) and/or the deploy script run against the pulled code — never
  by ad-hoc file edits on the host.
- **All releases are anchored to Git tags.** A release does not exist until an
  annotated tag is pushed; the GitHub Release is created from that tag
  (`docs/github/05-first-release.md`).
- **Any production change passes through a Pull Request and CI.** `main` and
  `release/1.0` are protected; direct pushes are blocked; CI (ruff, bandit,
  pip-audit, migration drift, 278 tests on MySQL 8, collectstatic,
  `check --deploy`) must be green before merge (`docs/github/02-branch-strategy.md`,
  `03-github-actions.md`).

## Alternatives considered
- **Hostinger Git as the single source** — rejected: no branch protection,
  no PR review, no CI integration; the deploy tool would also become the
  repository, conflating source and artifact.
- **SSH-only deploys** — rejected: untested, unaudited, no rollback safety, and
  no single version of truth; conflicts with ADR 0006's scripted path.
- **Self-hosted Git** — rejected: more ops burden on shared hosting with no
  CI/review tooling to show for it.

## Consequences
- **Positive:** one canonical history; every change reviewed + CI-gated;
  releases traceable to tags; deploys repeatable and documented; evidence
  records (ADR 0007) keep the governance enforceable.
- **Negative:** GitHub is a dependency — a GitHub outage blocks merges and
  auto-deploys until restored (deploys can still be run manually from the pulled
  code, but not merged).
- **Trade-offs accepted:** the CI MySQL run only executes after the first push
  (the PyMySQL pin fix, `CHANGELOG.md` rc2, makes that run green); until then
  "CI green on MySQL" is unverified.

## Evidence
- `docs/github/` (6 guides + README) — the operational implementation of this ADR.
- `CHANGELOG.md` — rc2 entry documenting the PyMySQL fix that unblocks the
  MySQL CI run.
- `docs/releases/v1.0-release-checklist.md` — the release process this ADR gates.

## Compliance
- `git remote -v` shows a single `origin` pointing at GitHub.
- `main` and `release/1.0` have branch protection (reviews + required CI).
- No tagged release exists without a pushed annotated tag and a GitHub Release.
- Production changes land via PR + green CI, never by direct host edits.
