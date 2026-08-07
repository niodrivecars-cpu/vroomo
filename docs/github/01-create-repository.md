# 01 — Create the GitHub Repository

GitHub is the **single source of truth** for Vroom's code (ADR 0007). This guide
takes the local repo to a hosted, protected remote — the prerequisite for CI and
Hostinger auto-deploy.

> Before starting: this repo already has commits and no `origin`. Do **not**
> let GitHub seed a README/`.gitignore`/license, or you will get a divergent
> history to reconcile.

## 1. Create the repository (no auto-init)

1. github.com → **New repository**.
2. Owner: your org or user. Name: `vroomo` (matches the project).
3. **Do not** check *Add a README*, *Add .gitignore*, or *Choose a license* —
   the local repo already has all three.
4. Set visibility per policy (private until launch unless a public repo is
   intended).
5. **Create repository**. GitHub shows the "quick setup" page — copy the SSH
   URL: `git@github.com:<owner>/vroomo.git` (SSH) or `https://github.com/<owner>/vroomo.git` (HTTPS).

## 2. Link `origin` and push

```bash
git remote add origin git@github.com:<owner>/vroomo.git   # or the HTTPS URL
git remote -v                                              # confirm
git push -u origin release/1.0                             # first push
git branch -a                                              # confirm tracking
```

After the first push, CI runs on `release/1.0` automatically (workflow triggers
on push to `main` and `release/1.0`, plus PRs).

## 3. Protect the branches

Repository → **Settings → Branches → Add branch protection rule**.

**`main`** (or apply to both `main` and `release/1.0`):
- [x] Require pull request reviews before merging (≥ 1 approval)
- [x] Require status checks to pass before merging — select the `test` job
- [x] Require branches to be up to date before merging
- [x] Require conversation resolution
- [x] Do not allow bypassing (administrators included)

`release/1.0` is where release work lands; `main` tracks stable production.

## 4. Enable Issues and Releases

- **Issues:** already on by default. Add issue templates if the team grows.
- **Releases:** no setup needed — GitHub Releases page activates on the first
  tag (see `05-first-release.md`).

## 5. Verify

- [ ] `git remote -v` shows `origin`
- [ ] `git push -u origin release/1.0` succeeded
- [ ] GitHub Actions ran the `test` job on the push (Actions tab)
- [ ] Branch protection shows on `main` / `release/1.0`

Next: `02-branch-strategy.md`.
