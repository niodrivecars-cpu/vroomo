# 02 — Branch Strategy

## Model

```text
main            -> Stable Production
release/1.0     -> Current Release (source of the v1.0 tags)
develop         -> Optional, only if a second release track appears
feature/*       -> New Features
hotfix/*        -> Production Fixes
```

## Lifecycle

1. **`main`** — deployable stable. Protected; only fast-forward-style merges of
   `release/*` and hotfixes. No direct pushes.
2. **`release/1.0`** — the current release track. All release work (docs,
   fixes, prep) lands here; CI runs on every push. **Tags are created from this
   branch.**
3. **`feature/<slug>`** — branch from `release/1.0`, work, open a PR back into
   `release/1.0`. One feature per branch; delete after merge.
4. **`hotfix/<slug>`** — branch from `main` (or the affected release branch)
   for production-only fixes; merge back to `main` and to the active
   `release/*`.
5. **`develop`** — only when there are concurrent release tracks; not needed for
   a single-product v1.0.

## Merge policy

- **Default: squash merge** for `feature/*` → `release/1.0`. Keeps one logical
  commit per feature and a linear, bisectable history.
- **Merge commit** for `release/1.0` → `main` — preserves the release history.
- **Cherry-pick or merge** for hotfixes; never rebase a shared branch.

## Commit message convention

Follow conventional commits so `git bisect`, `git blame`, and the changelog stay
readable:

```text
feat(scope): summary            # new capability
fix(scope): summary             # bug fix
docs(scope): summary            # documentation
refactor(scope): summary        # behavior-preserving change
perf(scope): summary            # performance
test(scope): summary            # tests only
chore(scope): summary           # tooling / deps / housekeeping
```

Rules:
- Imperative mood, lowercase, ≤ 72 chars summary.
- `scope` is the area touched: `fleet`, `config`, `deploy`, `database`, `release`, ...
- One logical change per commit; use the release checklist's 3-commit pattern
  for multi-part releases.

## Rules for this repo (from ADR 0007)

- No direct pushes to `main` or `release/1.0` — all changes go through PR + CI.
- No manual production deploys outside GitHub-driven automation.
- Every release is anchored to a Git tag (see `05-first-release.md`).
- Any production change must pass CI before merge.

Next: `03-github-actions.md`.
