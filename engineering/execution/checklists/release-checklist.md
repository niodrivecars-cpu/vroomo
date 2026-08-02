# Release Checklist

Quick verification before tagging a release.

- [ ] Working tree clean on the release branch
- [ ] Release gate green (ruff, bandit, pip-audit, migrations, 278 tests,
      collectstatic, check --deploy)
- [ ] Security gate green (scans + security review + attack profile)
- [ ] Performance gate green (smoke + attack, all 9 thresholds, exit 0)
- [ ] Load runs on fresh state
- [ ] Evidence manifest written (`evidence/releases/<version>.json`)
- [ ] Release notes written (`projects/<name>/release-history/<version>.md`)
- [ ] Tag points at the exact gate-passing commit (verified)
- [ ] Deploy plan ready (backup taken, runbook)
- [ ] Caveats documented (env limits, known dev-only artifacts)
