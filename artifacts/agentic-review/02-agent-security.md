# Agentic Review — Phases 3 & 6: Tool Permissions and Security Boundaries

Date: 2026-08-23 · Method: static analysis of tool surfaces, scripts, settings

## Phase 3 — Maximum-damage classification

| Tool / surface | Class | Max plausible damage |
|---|---|---|
| `bash` (PS 5.1) | **DEPLOYMENT/DESTRUCTIVE** | Run deploy/rollback against remote host if SSH path known; delete repo; read/exfiltrate `.env` secrets; mutate CI |
| `write`/`edit` | HIGH RISK WRITE | Rewrite tests, migrations, `.github/workflows/ci.yml`, security middleware to hide regressions |
| `playwright_browser_run_code_unsafe` | **DESTRUCTIVE (documented RCE-equivalent)** | Arbitrary code in server process — trust-boundary bypass by design; treat as privileged |
| `webfetch`/`websearch` | READ ONLY + egress | SSRF-style probing only of fetched URLs; no code exec |
| context7 MCP | READ ONLY | Doc-content influence (Phase 8 tests whether it can override project law) |
| subagents ×5 | LOW (4 deny-edit) / MEDIUM (test-writer allow-edit) | See inventory P1-04: no bash/network denies on any subagent |
| management commands | send_alerts = network email side effect; loadtest_seed = DB writes + password resets |

### Ten capability questions (evidence-based)

| # | Capability | Answer | Evidence |
|---|---|---|---|
| 1 | Modify source code | **YES** | write/edit tools; no permission gate on fleet/** |
| 2 | Delete files | **YES** | `Remove-Item` via bash; no recycle/safeguard |
| 3 | Modify migrations | **YES** | fleet/migrations editable; drift caught only *after* by verifier step 4 |
| 4 | Modify CI | **YES** | `.github/workflows/ci.yml` is a plain tracked file |
| 5 | Modify deployment scripts | **YES** | scripts/*.sh plain files |
| 6 | Alter security settings | **YES** | config/settings/*.py plain files; detection = later gates only |
| 7 | Access production | **CONDITIONAL** | Prod creds live on Hostinger, not in repo; local .env targets localhost only |
| 8 | Deploy without human approval | **Mechanically YES** | Nothing forbids agent executing scripts/deploy-hostinger.sh; GOVERNANCE sign-off is documentary (C5/C6 of Phase 2) |
| 9 | Expose secrets | **YES** | `.env` fully readable; two user-level configs hold plaintext API keys |
| 10 | Destroy production data | **Unlikely from this machine** | No prod DSN locally; would require agent to obtain remote ENV_FILE first |

## Phase 6 — Environment boundary review

### Deploy scripts (`scripts/*.sh`)
- Parameterized: `deploy-hostinger.sh <APP_DIR> <ENV_FILE> [REF]` — **no hardcoded prod hosts**, refuses missing env file, `chmod 600` on env. Good.
- `rollback.sh` restores code ref from `.deploy-state` but **explicitly does not reverse migrations** (documented gap, referenced to docs/deployment.md).
- Boundary holds *from this workstation* because APP_DIR/ENV_FILE for production do not exist locally.

### Settings layering
- `production.py` validates: SECRET_KEY present and not in known-insecure set {`test-key…`, `dev-insecure…`}, ALLOWED_HOSTS required, DEBUG forced False → raises `ImproperlyConfigured`. **Solid tripwire.**
- Residual: `base.py` falls back to insecure defaults silently under non-production settings modules — acceptable given production guard.
- Redis cache opt-in via CACHE_URL; locmem fallback safe.
- Rate limits centralised in `SECURITY_RATE_LIMITS`; client-IP resolution funnelled through one trusted-proxy function (ADR-0003). Good.

### Side-effect commands
- **`loadtest_seed` has NO environment guard** (no DEBUG/refuses-prod check) and resets user passwords to hardcoded `Loadtest!2026`. Executed against a real tenant DB it would mint known-password staff accounts. → **P1-05**
- `send_alerts` sends real email with retry; no dry-run flag found in head review. Medium risk (spam/phishing vector if misdirected), not data-destructive.

### Playwright boundary plan (tested live in Phase 9)
- Dev server will run from the **sandbox copy** bound to `127.0.0.1`; browser cannot reach any real deployment; screenshots/local-only data.

## Findings added
- **P1-04** Subagents inherit shell/network tools (only `edit` restricted).
- **P1-05** `loadtest_seed` lacks environment tripwire + hardcoded seed password.
- **P1-06** Agent-deployability: no mechanical block between agent shell and deploy scripts (compounds C5/C6).
- **P2-03** `send_alerts` has no dry-run mode.
