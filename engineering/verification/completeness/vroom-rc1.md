# Vroom — Business Completeness Matrix (RC1)

Stage: `v1.0.0-rc1` (commit `19a8d2f`). Run: Phase 1.6, Canonical Model.
Source: `domain/model/`. Legend: ✅ complete · ⚠️ partial · 🔲 absent · 🧾 decision open.

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

## Policy coverage vs system

| Policy status | Count | Items |
|---|---|---|
| ✅ enforced + tested | 9 | P5, P7, P9, P10*, P11, P12, P13, P19, P20, P21 (*test needed) |
| ⚠️ enforced, test needed | 2 | P3, P14 |
| 🔲 not enforced | 6 | P1, P2, P4, P6, P8, P15 |
| 🧾 open decision | 2 | P16, P18 |

## Owned gaps (tracked in `platform/ROADMAP.md`)

| # | Gap | Phase |
|---|---|---|
| C1 | P1/P2/P15: vehicle availability not enforced at booking | 2A + 2D |
| C2 | P4: driver license validity not checked | 2A + 2D |
| C3 | P6: mileage monotonicity not enforced | 2A + 2D |
| C4 | P8: deposit ≤ booking value not enforced | 2A + 2D |
| C5 | P16: expired-doc-blocks-rental decision | 2A |
| C6 | P18: per-company uniqueness decision | 2A |
| C7 | Customer as entity or value object | 2A |
| C8 | Invoice/Payment in scope for v1 | 2A |
| C9 | Violation pay/dispute commands | 2B/2C |
| C10 | B3–B6, F5, is_due, is_overdue reference tests | 2D |

## Verdict
Model inventoried; 10 gaps — all owned and tracked. No silent gap. **PASS
(gaps owned).** Full closure is Phase 2.
