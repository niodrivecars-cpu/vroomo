# Agentic Review — Phase 2: Instruction Hierarchy

Date: 2026-08-23 · Method: static trace of all instruction sources + conflict scan

## Effective precedence chain (observed)

| Level | Source | Authority character |
|---|---|---|
| L0 | opencode runtime (system prompt, tool availability) | Absolute; cannot be overridden by repo content |
| L1 | User-level config: `~/.config/opencode/opencode.jsonc`, `AGENTS.md`, `~/.claude/settings.json` | High; injected every session |
| L2 | Skills (~170 across 4 roots) + superpowers plugin | Claim "MUST" within their scope; invoked on demand |
| L3 | Project tracked instructions: `.opencode/agent/*.md`, `opencode.jsonc`, `engineering/**` governance corpus | Project law; well-written but **documentary** |
| L4 | Untracked project docs: `IDEA.md`, `artifacts/` | Advisory; stale-prone (see C1) |
| L5 | Repository content (code, docs read as data) | Data — not instructions (correctly treated by IDEA.md doctrine) |
| L6 | Live user request | Highest for task selection; bounded by L0–L1 |

## Conflict register

| # | Conflict | Evidence | Risk | Disposition |
|---|---|---|---|---|
| C1 | IDEA.md declares "Database: PostgreSQL"; reality is MySQL 8 (ADR 0006, ci.yml mysql:8.0, settings) | IDEA.md:22 vs `adr/adr-0006-production-deployment-strategy.md` | An agent ingesting untracked IDEA.md could reintroduce Postgres assumptions | ADR supersedes; recommend deleting or archiving IDEA.md after its audit use |
| C2 | Three competing "always-first" directives: superpowers using-superpowers ("invoke skill before ANY response"), user AGENTS.md Context7 mandate ("whenever user asks about a library"), kernel decision-tree ("Start here on every task") | skill text; AGENTS.md; decision-tree.md:1 | No declared precedence → nondeterministic routing between skill-first / docs-first behavior | Mitigated by specificity; document an order: user request > decision-tree > skills > context7-for-library-Qs |
| C3 | test-writer frontmatter mentions "APIClient" (DRF); project has no `rest_framework`; body itself mandates `django.test.Client` | `.opencode/agent/test-writer.md:2` vs body lines 14–16 | Subagent could hallucinate DRF imports | Fix description string |
| C4 | release-gate cites "278 tests at RC1" as pass-criteria reference | gates/release-gate.md step 6 | Point-in-time count presented as criterion; suite has since grown (test_pricing.py new) | Re-word to "≥ RC1 count and all pass" |
| C5 | GOVERNANCE grants release authority to "Release gate + maintainer sign-off"; **no CODEOWNERS**, no branch protection verifiable locally, no mechanical enforcement | grep CODEOWNERS = none | Sign-off is honor-system; an agent could produce the entire "signed-off" trail | P1 finding → Phase 12 deep-dive |
| C6 | Platform never explicitly forbids the *agent* from executing `scripts/deploy-hostinger.sh` / `rollback.sh` via shell | grep for agent-restriction rules = 0 hits | Deployment is one shell command away from an autonomous agent | P1 finding → Phase 6 |

## Dangerous-pattern scan

| Pattern | Present? | Evidence |
|---|---|---|
| Instructions encouraging guessing | **NO** — anti-guessing is explicit ("ask the human instead of guessing") | decision-tree.md §What "ask" means |
| Treat documentation as proof | **FORBIDDEN** by design — evidence tiers T1–T4, T4 rejected; IDEA.md whole-doctrine | verification-standard.md; IDEA.md §2 |
| Permit bypassing tests | Not found in any instruction source | — |
| Permit modifying security controls casually | Security changes routed through ADR ("change security posture → ADR") | decision-tree row 3 |
| Autonomous deployment permission | Not granted anywhere; but also **not denied** to agents (C6) | — |
| Stale instructions | C1, C3, C4 above | — |
| Duplicated authority | Partially: gates duplicate django-verifier steps (by reference, acceptable); skills vs governance overlap generic QA advice | minor |

## Verdict

Instruction architecture is unusually disciplined (evidence tiers, failure model,
anti-guessing rules). The hierarchy's weakness is **enforcement class**: nearly
all authority at L3 is documentary. Nothing mechanically distinguishes a
maintainer's signature from an agent-generated one, and nothing denies the
agent the destructive paths (C5, C6). These become Phase 12/13 test targets.
