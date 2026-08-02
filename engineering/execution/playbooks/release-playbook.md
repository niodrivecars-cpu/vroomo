# Release Playbook

Step-by-step to ship a release. Uses `execution/pipelines/release-pipeline.md`
as the sequence and `execution/gates/` as the gates.

## Before
- [ ] Working tree clean; branch `release/<version>` exists.
- [ ] Release scope known (what's in, what's out).

## Execute
1. Run release gate (`gates/release-gate.md`) → all green.
2. Run security gate (`gates/security-gate.md`) → green.
3. Run performance gate (`gates/performance-gate.md`) → green (fresh state).
4. Record evidence manifest (`evidence/releases/<version>.json`).
5. Write release notes (`projects/<name>/release-history/<version>.md`).
6. `git tag -a <version>` on the gate-passing commit.
7. Verify `git rev-parse <version>` == gate-passing commit.
8. Deploy (`runbooks/deploy-runbook.md`), health-check.

## After
- [ ] Evidence committed.
- [ ] Tag verified.
- [ ] Deploy verified.
- [ ] Release notes linked from `evidence/index.json`.

## If a gate fails
Stop. Fix → re-run ALL affected gates → only then continue. Never ship a release
with a red gate.
