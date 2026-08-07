# MCP Orchestration

MCP (Model Context Protocol) servers extend coding sessions with live data and
tooling. This directory documents each server: when to use, when NOT to use,
call order, common mistakes, and examples.

## Configured servers (opencode.jsonc)

| Server | Purpose | When to use |
|---|---|---|
| `postgres` | **Legacy/disabled** — DB is now MySQL 8 (ADR 0006) | Not used; see `postgres.md` |
| `playwright` | Browser automation for E2E/visual verification | RTL UI, form flows, accessibility checks |

## Not yet configured (planned)

| Server | Purpose | Status |
|---|---|---|
| `context7` | Live library documentation | Available; see `context7.md` |
| `docker` | Container lifecycle | When docker compose is the dev path |
| `github` | PR/issues/releases automation | When a remote is added |
| `sequential-thinking` | Structured reasoning for hard problems | Optional |

## Orchestration rules

1. **Prefer MCP for facts, not for opinions.** Live DB state, real docs, real
   browser behavior — yes. Design judgment — that belongs to the engineer.
2. **Check the resource first.** If a question can be answered from the repo,
   read the repo; MCP is for what the repo cannot tell you.
3. **Call order for a DB-dependent change:** context7 (library docs) → MySQL
   inspection (once an MCP is configured) → test-writer (tests) →
   django-verifier (gate).
4. **Never assume an MCP is up.** An inspection MCP needs the DB running (MySQL
   dev container via `docker compose up -d`); playwright needs `npx` + a browser.
   Verify before relying on it.
