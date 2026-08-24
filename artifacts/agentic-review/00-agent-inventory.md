# Agentic Review — Phase 1: Agent Inventory

Date: 2026-08-23 · Branch audited: `release/1.0` · Method: static enumeration + live probes

## 1. Instruction Sources

| Name | Location | Git-tracked | Verified | Notes |
|---|---|---|---|---|
| Platform system prompt (opencode core) | built-in | n/a | YES | Defines toolset, tone, commit rules |
| User AGENTS.md | `%USERPROFILE%\.config\opencode\AGENTS.md` | no | YES | Context7 usage mandate; MCP instructions |
| Project config comment-instructions | `opencode.jsonc` | YES | YES | Notes about subagents, legacy postgres MCP |
| Subagent prompts ×5 | `.opencode/agent/*.md` | YES | YES | Role, checklist, edit permissions |
| IDEA.md | repo root | no (untracked) | YES | 856-line doc-audit meta-prompt; evidence hierarchy |
| engineering/ governance corpus | `engineering/**` | YES | YES | kernel, gates, playbooks, ADRs |
| No project-level AGENTS.md / CLAUDE.md | — | — | VERIFIED ABSENT | Governance lives in `engineering/` instead |

## 2. MCP Servers (from both config layers)

| Server | Config layer | Type | Status probe | Trust notes |
|---|---|---|---|---|
| context7 | user (`~/.config/opencode/opencode.jsonc`) | remote | **PASS** (resolve-library-id returned results) | API key in plaintext config (see findings) |
| playwright | project + user | local (`npx`) | Tools present; live test deferred to Phase 9 | Project pins none; user uses `@latest` (unpinned) |
| openseo | user | remote | **INERT** — zero tools exposed in session; `list_mcp_resources` empty | Enabled-but-unusable; attack surface ≈ 0 today |
| postgres (crystaldba) | project | local (`uvx`) | **DISABLED** (`enabled: false`) | Residual risk: `--access-mode=unrestricted` + embedded creds remain in tracked config |

## 3. Subagents (`.opencode/agent/`, all git-tracked)

| Agent | Edit permission | Shell? | Purpose | Can deploy? | Secrets access |
|---|---|---|---|---|---|
| security-reviewer | **deny** | via inherited tools unless denied elsewhere* | diff/security review | no | inherits env |
| django-verifier | **deny** | yes (must run verify commands)* | full verification gate | no | inherits env |
| booking-domain-review | **deny** | not needed by prompt* | booking rules B1–B6 review | no | inherits env |
| business-rule-review | **deny** | not needed by prompt* | rule methodology review | no | inherits env |
| test-writer | **allow** | yes (runs suite) | writes tests in `fleet/tests/` | no | inherits env |

\* OpenCode subagents inherit the parent tool set except where front-matter denies; only `edit` is explicitly restricted. There is **no explicit deny for bash/web/deploy tools** on any subagent → a compromised or confused subagent could still execute shell. Finding P1-04.

## 4. Core Toolset Available to Primary Agent (live-verified)

| Tool | Class (Phase 3) | Can modify code | Shell | Deploy | Secrets | External net | Prod access |
|---|---|---|---|---|---|---|---|
| `bash` (PowerShell 5.1) | DEPLOYMENT/DESTRUCTIVE | yes | yes | yes (scripts/*.sh) | yes (.env readable) | yes | **yes if credentials present** |
| `write` / `edit` | HIGH RISK WRITE | yes | n/a | can alter CI/deploy files | n/a | no | indirect |
| `read`/`glob`/`grep` | READ ONLY | no | no | no | reads .env if asked | no | no |
| `playwright_browser_*` incl. `run_code_unsafe` | **DESTRUCTIVE (RCE-equivalent)** | via page JS | via run_code | no | no (unless pages leak) | yes | whatever URL it reaches |
| `webfetch` / `websearch` | READ ONLY (+egress) | no | no | no | no | yes | no |
| `context7_*` | READ ONLY | no | no | no | no | yes (MCP remote) | no |
| `task` (subagent dispatch) | orchestrator | delegated | delegated | no | delegated | delegated | no |
| `skill` (~170 skills across 4 dirs) | mixed per skill | per-skill | per-skill | some claim deploy knowledge | no | some | no |

Skill directory census: `.claude/skills` = 147 · `.opencode/skills` = 8 · `.config/opencode/skills` = 2 · `.agents/skills` = 13. Superpowers plugin loaded from `~/.config/opencode/node_modules/superpowers`.

## 5. Automation & CI

| Component | File | Trigger | Can it mutate prod? |
|---|---|---|---|
| GitHub Actions CI | `.github/workflows/ci.yml` (tracked) | push to main/release/1.0, PRs | No — MySQL 8 service container, tests/lint/audit only. **No deploy job exists** (verified). |
| setup.ps1 | repo root | manual | local only (db/migrate/superuser/runserver) |
| deploy.sh / deploy-hostinger.sh / rollback.sh / backup.sh / restore.sh | scripts/ (tracked) | **manual execution only** | YES — these are the only production-mutation paths, invoked via agent shell |
| management commands | `fleet/management/commands/loadtest_seed.py`, `send_alerts.py` | manual | seed = DB writes; send_alerts = **outbound email** (network side effect) |

## 6. Credentials / Environment Exposure to Agents

| Secret store | Values present | Git-tracked | Agent reachability |
|---|---|---|---|
| `.env` (repo root) | SECRET_KEY, DB creds, EMAIL_HOST_PASSWORD, ADMIN_EMAIL | **no** (gitignored ✓) | FULL via read/bash — unavoidable for shell agents |
| `.env.production.example` | template only | YES | safe |
| `~/.config/opencode/opencode.jsonc` | **Context7 API key plaintext** | outside repo | FULL |
| `~/.claude/settings.json` | **ANTHROPIC_AUTH_TOKEN + ANTHROPIC_API_KEY plaintext**, third-party model routing via local proxy 127.0.0.1:20128 | outside repo | FULL |
| `opencode.jsonc` (project) | embedded postgres DSN (`vroomo:vroomo@localhost`) | YES | FULL (tracked credential residue) |
| CI secrets | none referenced in ci.yml (env inline, non-secret) | — | n/a |

## 7. Probe Results Summary

- context7 resolve-library-id: **PASS**
- playwright tool surface: PRESENT (live behavioral test in Phase 9)
- openseo: configured+enabled, **0 tools surfaced** → inert
- postgres MCP: disabled → unreachable
- MCP resources/templates: none exposed by any server
- venv python (3.14.7 / Django 6.0.7): **PASS**

## Inventory Findings (feed Phase 15)

- **P0-01** Plaintext API keys/tokens in two user-level configs (rotation recommended).
- **P1-01** Tracked credential residue in `opencode.jsonc` postgres block.
- **P1-02** Unpinned dependency: user-level `@playwright/mcp@latest`.
- **P1-03** Disabled unrestricted-mode DB MCP left configured — one flag-flip from active.
- **P1-04** Subagents lack tool-level denies beyond `edit`; shell/network implicitly available.
