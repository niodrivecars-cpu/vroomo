# Release Pipeline

End-to-end sequence from "code is ready" to "release tagged with evidence."

1. **Feature complete** — code + tests on `release/<ver>` branch.
2. **Full verification gate** — run `execution/gates/release-gate.md` end to end
   (static, security, tests, collectstatic, check --deploy).
3. **Load gate** — k6 smoke + attack on fresh state; both exit 0, all thresholds
   green (`execution/gates/performance-gate.md`).
4. **Record evidence** — write `evidence/releases/<version>.json` linking the
   gate artifacts (security scans, test summary, k6 output).
5. **Release notes** — `projects/<name>/release-history/<version>.md` with scope,
   gates, caveats, verdict.
6. **Tag** — `git tag -a <version>` on the exact commit that passed the gates.
7. **Verify the tag** — `git rev-parse <version>` == the gate-passing commit.
8. **Deploy** — `scripts/deploy.sh` (see `runbooks/deploy-runbook.md`).
9. **Verify deploy** — `scripts/healthcheck.sh`.

## Rule
If any fix lands after the tag, re-run the affected gates and re-tag. A stale
tag is a release bug (the RC1 tag was moved for exactly this reason).
