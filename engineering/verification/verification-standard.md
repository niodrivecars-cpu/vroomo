# Verification Standard

What "verified" means on this platform.

## Evidence tiers

| Tier | Kind | Example | Verdict value |
|---|---|---|---|
| T1 | Automated executable proof | unit test, migration check | High — deterministic |
| T2 | Automated measurement | k6 thresholds, bandit/pip-audit | High — numeric, machine-checked |
| T3 | Structured human review | security review sign-off, code review | Medium — reproducible process |
| T4 | Assertion without record | "I tested it", "looks fine" | Low — no evidence |

## Rules
1. A verification claim cites a tier. T4 ("I checked, trust me") is not
   verification — it's a starting point.
2. T1/T2 evidence is the default for anything executable. Human review (T3) is
   required on top where judgment matters (security, architecture).
3. Every claim maps to a test or scan or measurement in `evidence/`. If it
   can't, it's a documented risk (see `risk-matrix.md`).

## What counts as a release-ready proof
A release is ready when:
- Static/security scans pass (T2).
- Test suite passes (T1).
- Load thresholds pass on fresh state (T2).
- Security + code review signed off (T3).
- Residual risks recorded and accepted for the stage (risk matrix).

## Enforced by
- CI (`.github/workflows/ci.yml`).
- The release gate (`execution/gates/release-gate.md`).
- Evidence manifests (`evidence/releases/<version>.json`).
