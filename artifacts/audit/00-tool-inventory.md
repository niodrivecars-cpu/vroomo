# Tool/Skill Inventory — Vroom Verification

## Available tools

| Tool/Skill | Available | Purpose | Used |
|---|---|---|---|
| terminal (bash) | YES | Run git, python, manage.py, ruff, bandit, pip-audit, k6 | YES — git, ls, cat, python version checks |
| read_file | YES | Read repository files | YES — settings, models, views, migrations, docs, tests, evidence JSON |
| search_files | YES | Ripgrep content/file search | YES — i18n pattern search, test file discovery |
| patch / write_file | YES | Edit files | Available; will use for fixes |
| python (local) | YES (3.11.16) | Run Django test suite, validators | YES — attempted to inspect |
| git | YES | Inspect history, diffs, status | YES — git log, git status |
| skills_list / skill_view | YES | Inspect Hermes skills | YES — listed 72 skills |
| vision_analyze | YES | Image analysis | Available; not needed yet |
| browser_exec | YES | Browser automation | Available; not needed yet |
| open_preview / drive_preview | YES | In-app browser | Available; not needed yet |

## Named skills detected vs required by spec

| Skill | Available | Notes |
|---|---|---|
| Apple Design skill | **UNAVAILABLE** | Not in skill list. `cb2c0f3` commit message references "Apple Design system" but no such Hermes skill exists. UI work is done via CSS in `base.html`. |
| UI/UX Pro Max | **UNAVAILABLE** | Not in skill list. |
| Context7 MCP | **UNAVAILABLE** | Not detected; no MCP server config references it. |
| Playwright MCP | **UNAVAILABLE** | Not in skill list. k6 is available for load testing instead. |
| security review workflow | **UNAVAILABLE as skill** | bandit + pip-audit run in CI (`.github/workflows/ci.yml`); security evidence in `engineering/evidence/security/`. Manual reproduction tests in `fleet/tests/test_security.py`, `test_idor.py`. |
| Claude security review | **UNAVAILABLE** | Not applicable to this agent. |
| hermes-agent | YES | For Hermes configuration (if needed). |
| opencode | YES | Can delegate to OpenCode CLI. |
| claude-code | YES | Can delegate to Claude Code CLI. |
| computer-use | YES | Desktop automation. |
| systematic-debugging | YES | 4-phase root cause debugging. |
| test-driven-development | YES | TDD enforcement. |
| dogfood | YES | Exploratory QA. |
| github-pr-workflow | YES | GitHub PR lifecycle. |

## Repository instruction files

| File | Present | Contents |
|---|---|---|
| AGENTS.md | YES | Present in `websi/ECC/` (separate project) |
| CLAUDE.md | YES | Present in `websi/ECC/` |
| .cursorrules | NO | Not found |
| OPENCLOAK.md | NO | Not found |
| pyproject.toml | YES | Python project config |
| .opencode* configs | YES | Present in `websi/ECC/` |
| ruff.toml | YES | Linter config |
| opencode.jsonc | YES | OpenCode configuration |

## Assessment

The Vroom project uses a **self-contained security review discipline** (bandit + pip-audit + custom regression tests in `fleet/tests/`), not a named "security review skill." The "Apple Design" reference in commit `cb2c0f3` is a CSS design language applied to `base.html`, not the Hermes Apple Design skill. Load testing uses **k6** (not Playwright MCP). The spec's Phase 17/19 mention of Apple Design skill and UI/UX Pro Max are **not available** — UI/UX review will be conducted via direct template inspection and manual verification instead.
