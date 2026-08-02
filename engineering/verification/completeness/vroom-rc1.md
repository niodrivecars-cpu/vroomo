# Vroom — Business Completeness Matrix (RC1)

Stage: `v1.0.0-rc1` (commit `19a8d2f`). Run: Phase 1.6 + Phase 2A governance,
Canonical Model. Source: `domain/model/`. Legend: ✅ complete · ⚠️ partial · 🔲 absent · 🧾 decision open.

| Entity | State Machine | Policies | Events | Commands | Invariants | Tests | Verdict |
|---|---|---|---|---|---|---|---|
| Company | ⚠️ (active flag only) | P11, P17 | 🔲 none | ⚠️ create only | F1 | ✅ | **Partial — deactivation semantics (P18 context)** |
| Vehicle | ✅ (4 states + ✗) | P1, P2, P6, P15, P17 | 🔲 aspirational | ⚠️ status guard | F1, F6 | ✅ (P1–P2/P15 🔲) | **Partial — availability policies unenforced** |
| Booking | ✅ (5 states + ✗) | P3, P5, P7, P8, P20 | 🔲 aspirational | ✅ create/cancel/return | B1–B6 | ⚠️ (B3–B6 needed) | **Partial — tests + P8 gap** |
| Customer | — (not an entity) | — | — | — | — | — | 🧾 **decision: entity or value object** |
| Driver | ⚠️ (active flag) | P4, P17 | 🔲 | ⚠️ assign | F1, F6 | ✅ | **Partial — license validity unenforced** |
| Maintenance | 🔲 (no status) | P1 (via vehicle) | 🔲 aspirational | ✅ | — | ⚠️ (is_due test needed) | **Partial — due-blocking not enforced** |
| Violation | ✅ (5 states + ✗) | P9, P10, P19 | 🔲 | 🔲 pay/dispute | — | ✅ (P10 test needed) | **Partial — payment commands absent** |
| VehicleDocument | ✅ (derived expiry) | P12, P13, P14, P16 | 🔲 real (upload/download) | ✅ upload/revoke | F3–F5 | ⚠️ (F5 needed) | **Partial — F5 test + P16 decision** |
| AuditLog | — (append-only) | — | ✅ real | — | — | ✅ | ✅ |
| Invoice | 🔲 **not modeled** | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 **in-scope? (Phase 2A)** |
| Payment | 🔲 **not modeled** | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 **in-scope? (Phase 2A)** |

## Policy coverage vs system (governance register)

| Policy status | Count | Items |
|---|---|---|
| ✅ Enforced (implemented + tested) | 8 | P9, P11, P12, P13, P17, P19, P20, P21 |
| 🟡 Validated (correct, not proven/implemented) | 10 | P1, P2, P3, P4, P5, P6, P7, P10, P14, P15 |
| 🔵 Proposed (awaiting decision) | 3 | P8, P16, P18 |
| ⚪ Out of Scope | 0 | — |
| ❌ Rejected | 0 | — |

Every policy also carries BRL v2 dimensions (SEVERITY / DECISION / ENFORCEMENT)
validated by `kernel/compiler/validate_rules.py` — see
`domain/model/policies.md` and the Policy Graph
(`verification/traceability/vroom-graph.md`).

## Use Case coverage (traceability)

| UC | Scenario | Status |
|---|---|---|
| UC1–UC4 | Create / Cancel / Pickup / Return booking | ⚠️ guards B3–B4, P4, P6 unproven |
| UC5 | Extend booking | 🔲 no command |
| UC6–UC7 | Record maintenance / set vehicle status | ⚠️ P15 unproven; emissions aspirational |
| UC8 | Upload document | ⚠️ P14 unverified |
| UC9–UC10 | Download / revoke document links | ✅ |
| UC11 | Record violation | ✅ |
| UC12 | Mark violation paid | 🔲 no payment flow |

## Owned gaps (tracked in `platform/ROADMAP.md`)

| # | Gap | Phase |
|---|---|---|
| C1 | P1/P2/P15: vehicle availability not enforced at booking | 2B.1 + 2B.2 |
| C2 | P4: driver license validity not checked | 2B.1 + 2B.2 |
| C3 | P6: mileage monotonicity not enforced | 2B.1 + 2B.2 |
| C4 | P8: deposit ≤ booking value not enforced | 2A (decision) + 2B.2 |
| C5 | P16: expired-doc-blocks-rental decision | 2A |
| C6 | P18: per-company uniqueness decision | 2A |
| C7 | Customer as entity or value object | 2A |
| C8 | Invoice/Payment in scope for v1 | 2A |
| C9 | Violation pay/dispute commands | 2B.2/2B.3 |
| C10 | B3–B6, F5, is_due, is_overdue reference tests | 2B.2 |

## Verdict
Model inventoried and **governed**: every policy has owner, source, status,
risk, priority, and chain; every UC is traced. 10 gaps — all owned and tracked.
No silent gap. **PASS (gaps owned).** Full closure is Phase 2.
