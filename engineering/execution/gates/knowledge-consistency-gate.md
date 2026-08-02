# Gate: Knowledge Consistency

**Purpose:** the platform's reference material is coherent — no conflicts, no
duplication, one term per concept, and every internal link resolves.

This is a platform-self gate. It is run as part of **Phase 1.5 (Platform
Validation)** and must be re-run whenever `knowledge/`, `patterns/`,
`domain/`, or `governance/` gains material content.

## Checks

| # | Check | How | Pass |
|---|---|---|---|
| 1 | No conflicting advice | Review new knowledge against existing topics in the same space | No doc contradicts another for the same situation |
| 2 | No duplicated content | A topic lives in exactly one place; every other doc **links** to it | Knowledge links to patterns/domain; it does not restate them |
| 3 | One term per concept | Docs use `platform/GLOSSARY.md` vocabulary | No synonym for a defined concept without a glossary mapping note |
| 4 | Internal links resolve | Script: parse `](...)` links in `engineering/**/*.md`, resolve relative to the file's dir | 0 broken links |
| 5 | ADR/RFC coherence | Each ADR is current or explicitly superseded; no two ADRs conflict | No stale/superseded ADR remains unmarked |
| 6 | Rule vs invariant split | `business-rules.md` states intent; `invariants.md` restates as numbered hold-at-all-times | Every business rule in a domain maps to an invariant (see Business Traceability Gate) |

## Runbook

```powershell
# Check 4 (links)
Get-ChildItem -Recurse -File engineering -Include *.md | ForEach-Object {
  (Get-Content -Raw $_.FullName) } | ...   # see execution/ for the committed script when Phase 4 lands
```

Until automated: run the link-check, then grep for glossary synonyms
("framework", "step" for gate, "skill" for capability, etc.).

## Evidence

Record the run in `evidence/verification/knowledge-consistency-<date>.json`
(checks list + result). A failed check must be fixed or recorded as debt before
the gate passes.
