# Platform Architecture

The platform is documentation plus executable tooling, not a framework. It never
ships inside the product; it governs how the product is built and proven.

## The five concerns

1. **Knowledge** (`knowledge/`) — what we know. A reference library written once,
   reused everywhere. Organized by technology (django, postgres) and by domain
   (fleet, booking). Each topic: `overview`, `pitfalls`, `best-practices`,
   `references`.

2. **Governance** (`governance/`) — how decisions are made. Written standards
   (principles, code review, quality) plus decision records (ADR) and change
   proposals (RFC). A change that touches architecture or business rules should
   leave a record, not just code.

3. **Patterns** (`patterns/`) — approved solutions. Each pattern documents why,
   when not to use it, trade-offs, Vroom examples, common mistakes, required
   tests, and security/performance review points.

4. **Execution** (`execution/`) — how work happens. Pipelines (review, release),
   gates (release, security, migration, performance), playbooks, runbooks,
   checklists, templates.

5. **Verification + Evidence** (`verification/`, `evidence/`) — how we prove and
   record. The verification standard defines a confidence model and risk matrix;
   the evidence system stores machine-verifiable artifacts keyed by gate.

## Projects layer

`projects/<name>/` is the only layer that is product-specific. A product pulls
from the platform's standards and patterns, and returns evidence and new
patterns. This keeps the platform reusable: adding Nio later means adding
`projects/nio/`, not restructuring the platform.

## Tooling integration

- `opencode.jsonc` — MCP servers (postgres, playwright) and sub-agents.
- `.opencode/agent/*` — django-verifier, security-reviewer, test-writer,
  business-rule-review, booking-domain-review.
- `.github/workflows/ci.yml` — CI gate for every commit.
- `docs/releases/` — project-level release artifacts (mirrored into evidence).
- `GLOSSARY.md` — one term per concept, enforced by the Knowledge Consistency Gate.
