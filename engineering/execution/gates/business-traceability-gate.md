# Gate: Business Traceability

**Purpose:** every business rule is traceable through an unbroken chain to
executable proof. If the chain breaks at any link, that is a recorded gap that
must be owned — never a silent hole.

This is the **most important** platform gate. It enforces the source-of-truth
ordering:

```text
Business Rule  →  Invariant  →  Code  →  Tests  →  Evidence
```

and forbids the reverse: code may never redefine the business without the rule
documented first.

## The chain

| Link | Where it lives | Verified by |
|---|---|---|
| Business Rule | `domain/<context>/business-rules.md` | written rule |
| Invariant | `domain/<context>/invariants.md` (numbered: B1, F1…) | every rule maps to ≥1 invariant |
| Code | `fleet/models.py`, services, views | invariant names the enforcing code |
| Test | `fleet/tests/`, `tests/performance/` | every invariant has a `test-matrix.md` row |
| Evidence | `evidence/` (suite, k6, gate manifests) | test exists AND green for the commit |

## Checks

| # | Check | Pass |
|---|---|---|
| 1 | Rule → Invariant | every rule in `business-rules.md` is restated as a numbered invariant |
| 2 | Invariant → Code | every invariant names its enforcement (form, model, FK, service, view) |
| 3 | Invariant → Test | every invariant has a row in `test-matrix.md` |
| 4 | Test → Evidence | every **existing** test is green for the current commit (release gate) |
| 5 | Gaps owned | every "needed"/"open" row in a `test-matrix.md` is listed in the traceability snapshot and tracked in the roadmap |

## Output

The gate run produces a traceability snapshot per project and stage:

`verification/traceability/<project>-<stage>.md`

with one row per rule and a gap list. The snapshot is recorded as evidence
(`evidence/traceability/<project>-<stage>.json`).

## Pass criteria for Phase 1.5
The chain *structure* exists for every rule (rule + invariant + code + a test
matrix row). Full closure — every invariant green — is the Phase 2 deliverable;
the gate passes 1.5 when every break is a recorded, owned gap.
