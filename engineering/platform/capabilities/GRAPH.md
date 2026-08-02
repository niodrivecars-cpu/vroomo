# Capability Graph

The platform knows how its capabilities **relate** — not just that they exist.
The graph is derived from the ontology (`kernel/ontology.md`) and the coverage
matrix (`platform/capabilities/README.md`). It is the answer to "what else is
affected when I change this?"

## Nodes (capabilities)

`Architect` · `Security` · `Review` · `Performance` · `Release` ·
`Business Rule Review` · plus the assets `Verification` · `Evidence` ·
`Knowledge` · `Patterns`.

## Edges (kinds: `provides` / `depends_on` / `feeds`)

| From | Kind | To |
|---|---|---|
| Security | provides | Multi-tenant isolation, Audit, Auth, Signed Downloads |
| Performance | provides | ORM discipline, Caching, Indexes & migrations |
| Business Rule Review | provides | Policy governance, Invariant spec, Traceability, Rule engine |
| Architect | provides | Layered structure, Decision records (ADR/RFC) |
| Release | provides | Release gate, Migration gate, Evidence manifests |
| Review | provides | Code review, Security review, Business rule review |
| Business Rule Review | depends_on | Security (isolation invariants) |
| Business Rule Review | depends_on | Architect (structure) |
| Release | depends_on | Review, Performance, Security (their evidence feeds release) |
| Review | depends_on | Knowledge, Patterns (standards to review against) |
| Business Rule Review | feeds | Evidence (`evidence/traceability/`, `evidence/verification/`) |
| Verification | feeds | Evidence |
| Evidence | feeds | Release |
| Knowledge, Patterns | feeds | every capability (reference material) |

## Read it as
```text
                    ┌─────────────── Knowledge · Patterns (feed everything) ───────────────┐
                    ▼                                                                      │
Architect ──provides──► Business Rule Review ──provides──► Policy · Invariant · Rule · Trace │
  │                       │  │                                                            │
  │  depends_on           │  └──feeds──► Evidence (verification)                           │
  ▼                       ▼             │                                                 │
Security ──────────────► Review ◄───────┤                                                 │
  │                      │              │                                                 │
  │  feeds               │  feeds       ▼                                                 │
  └──────────────────────┴─────────► Release ──evaluated by──► Release Gate               │
                                        ▲                                                  │
Performance ──feeds─────────────────────┘                                                  │
                                                                                           │
                                        └────────── feeds back to Knowledge ◄──────────────┘
```

## Use
- Before changing a capability, read its incoming and outgoing edges and
  re-check the affected gates/evidence.
- A capability that neither provides, depends on, nor feeds anything is a
  candidate for removal (kernel principle 8, simplicity).
- The graph is maintained by the Capability Coverage Gate
  (`execution/gates/capability-coverage-gate.md`) — every edge must resolve to a
  real doc/gate/evidence path or be marked "None — rationale".
