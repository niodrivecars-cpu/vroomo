# 05 — First Release (v1.0.0-rc2 → v1.0.0)

The complete sequence from code freeze to the first production tag. Each step is
a gate: do not proceed until the previous one passes.

## Sequence

```text
Code Freeze
    ↓
Update CHANGELOG
    ↓
Push release/1.0
    ↓
CI Pass (MySQL 8)
    ↓
Hostinger Deploy
    ↓
Preflight Checklist
    ↓
Post-Deploy Validation
    ↓
Smoke Tests
    ↓
Create Tag v1.0.0-rc2
    ↓
GitHub Release
```

## Steps

### 1. Code freeze

No functional changes until the first deploy lands. Any discovered bug becomes
a separate hotfix (`hotfix/*`) so the release history stays clean.

### 2. Update the CHANGELOG

Move the ready items from `[Unreleased]` into a `[1.0.0-rc2] - <date>` section.
This is a **required** pre-tag item (`docs/releases/v1.0-release-checklist.md`).

### 3. Push `release/1.0`

```bash
git push origin release/1.0
```

### 4. Verify CI

GitHub Actions `test` job must be green (all steps, MySQL 8 backend). See
`03-github-actions.md` for what failure looks like.

### 5. Deploy to Hostinger

Auto-deploy pulls on the push, or run `scripts/deploy-hostinger.sh` manually.
Verify `/health/` returns 200. See `04-hostinger-auto-deploy.md`.

### 6. Preflight checklist

Run `docs/deployment/preflight-checklist.md` — every box `[x]`, no blockers.
This is the **Go/No-Go gate**; an unchecked box blocks shipping.

### 7. Post-deploy validation

Run `docs/deployment/post-deploy-validation.md`: functional (login, customers,
vehicles, bookings, return, transactions, uploads, private downloads),
security (media blocked, CSRF, rate limits, HTTPS, audit), performance
(home < 2 s, dashboard < 3 s, `/health/` < 200 ms), data (backup runs, restore
proven).

### 8. Smoke tests

A quick browser pass of the critical user journey on the live site
(login → create → book → return → download). Log evidence (screenshots, URLs).

### 9. Create the tag

Only after steps 1–8 all pass:

```bash
git tag -a v1.0.0-rc2 -m "Release Candidate 2 — Hostinger Business production pivot"
git push origin v1.0.0-rc2
```

### 10. Create the GitHub Release

GitHub → **Releases → Create a release** → choose the `v1.0.0-rc2` tag →
paste the CHANGELOG entry. Mark as **Pre-release** for an RC.

## After the RC: promoting to v1.0.0

After the RC has soaked in production and all validation stays green:

```bash
git tag -a v1.0.0 -m "First production release"
git push origin v1.0.0
```

Create the GitHub Release (this one **not** pre-release). The RC remains in
history as the anchor; `v1.0.0` is the promoted version.

## Rules (ADR 0007)

- Tags are created **only** after CI + deploy + validation pass — never before.
- No release exists without a Git tag and a GitHub Release.
- Every production change is PR + CI gated.

Next: `06-troubleshooting.md`.
