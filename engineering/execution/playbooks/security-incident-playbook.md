# Security Incident Playbook

What to do when a security issue is suspected or confirmed.

## Triage (immediate)
1. **Isolate** — determine blast radius: which tenants, which data, which
   surfaces (auth? downloads? tenant boundary?).
2. **Reproduce** — a test that shows the issue (red) before any fix.
3. **Assess severity** — data breach? unauthorized access? availability?

## Severity levels
| Level | Example | Response |
|---|---|---|
| Critical | Cross-tenant data exposure | Freeze deploy; revoke/rotate keys; notify affected tenants; hotfix |
| High | Rate-limit bypass, signed-URL forgery | Hotfix + rotate; review audit trail |
| Medium | Missing header, log leak | Patch in next release; document |
| Low | Best-practice gap | Track as debt |

## Response
1. Fix with a regression test (red → green).
2. Re-run security gate (`gates/security-gate.md`).
3. Rotate secrets if exposed (SECRET_KEY, signing keys, DB creds).
4. Check the audit log for exploitation windows; record findings.

## Post-incident
- Write/update the pattern in `patterns/` and pitfalls in `knowledge/security/`.
- Record the incident + outcome as evidence.
- Decide if it needs an ADR (posture change).

## Escalation
If the incident touches tenant data integrity or legal exposure (e.g. PII),
involve the pilot customer contract owner before any notification.
