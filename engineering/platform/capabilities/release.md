# Capability: Release

**Promise:** a release is a deliberate, gated, evidence-backed event — never an
accident of accumulated commits.

## Skills
- django-verifier (sub-agent) — runs the full verification gate.
- release-playbook — the ordered steps.
- evidence — the release manifest.

## Requirements
1. **All gates green** (security, performance, release) with evidence recorded
   before tagging.
2. **Release notes** describing scope, gates, and caveats
   (`projects/<name>/release-history/`).
3. **Tag points at the exact commit that passed the gates.** If a fix lands
   after the tag, re-tag; a stale tag is a release bug.
4. **Verdict is recorded** — PASS with evidence, or not a release.

## Coverage
- Knowledge: `knowledge/hostinger/` (deploy env).
- Pattern: None — release is a procedure; see `release-playbook.md`.
- Checklist: `execution/checklists/release-checklist.md`.
- Review step: release-playbook sign-off.
- Gate: release-gate · Evidence: `evidence/releases/`.

## Evidence manifest
`evidence/releases/<version>.json` — links gate results, test summary, k6
artifacts, and the tagged commit.

## Gate
`execution/gates/release-gate.md` + `execution/playbooks/release-playbook.md`.
