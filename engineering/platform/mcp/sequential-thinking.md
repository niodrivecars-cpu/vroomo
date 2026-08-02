# sequential-thinking MCP

Planned, optional. Adds explicit structured reasoning steps for hard, ambiguous
problems.

## When to use (planned)
- Multi-step debugging where the failure path is not obvious.
- Decisions with several interacting trade-offs (architecture, data model).

## When NOT to use
- Routine changes with a clear path — it adds ceremony without value.
- When the platform's own process (RFC, ADR, decision-process) already forces
  structure.

## Status
Optional. Not configured. Turn on only if it measurably improves hard-debug
outcomes; the platform prefers the written RFC/ADR discipline over in-session
reasoning traces for durable decisions.
