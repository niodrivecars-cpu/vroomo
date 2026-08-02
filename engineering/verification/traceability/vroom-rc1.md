# Vroom — Traceability Snapshot (RC1)

Stage: `v1.0.0-rc1` (commit `19a8d2f`). Run: Phase 1.5, Platform Validation.

Chain: **Rule → Invariant → Code → Test → Evidence**. Legend in `README.md`.

## Booking

| Rule | Invariant | Code | Test | Evidence | Status |
|---|---|---|---|---|---|
| Exclusivity: no overlapping non-cancelled windows for one vehicle | B1 | view check-then-insert + retry (ADR 0005) | k6 `sameVehicleBooking` exists; unit "adjacent windows" needed | RC1 k6 (1 success/window) | ⚠️ |
| Tenant scope: vehicle/driver must belong to booking's company | B2 | tenant-scoped manager + validation | IDOR/cross-tenant tests exist | RC1 suite + k6 `tenant_isolation_violation == 0` | ✅ |
| Window validity: `expected_return > pickup_date` | B3 | form validation | needed | — | ⚠️ |
| Money: `total_amount >= 0`, `deposit >= 0` | B4 | form/model validation | needed | — | ⚠️ |
| Status lifecycle (state machine) | B5 | choices + service enforcement | needed | — | ⚠️ |
| Vehicle/driver not deletable under a booking | B6 | FK `on_delete=PROTECT` | needed | — | ⚠️ |

## Fleet

| Rule | Invariant | Code | Test | Evidence | Status |
|---|---|---|---|---|---|
| Every entity created with company (structural) | F1 | `TenantScopedModel` | model tests exist | RC1 suite | ✅ |
| Cross-tenant read/write blocked | F2 | tenant-scoped manager | IDOR tests + k6 exist | RC1 suite + k6 | ✅ |
| Documents private + expiring signed URLs | F3 | `VehicleDocument.file` private, signed views | signed/expired/tampered/cross-tenant tests exist | RC1 suite + k6 `dl-*` | ✅ |
| Revoked links stop working | F4 | `download_token_version`, `revoke_download_links()` | revoke test exists | RC1 suite | ✅ |
| Superseded file deleted best-effort | F5 | file hygiene in view/service | needed | — | ⚠️ |
| Unique plate / CIN | F6 | `unique=True` | model tests exist | RC1 suite | ✅ |
| Maintenance due (km OR date) | — | `is_due` property | needed | — | ⚠️ |
| Violation overdue/paid derivation | — | `is_overdue` property | needed | — | ⚠️ |
| Violation auto-link to active booking driver | — | view logic | `test_violation_create_auto_links_driver_from_active_booking` exists | RC1 suite | ✅ |
| Expired doc blocks rental | — | — | — | — | 🔲 policy open |

## Pricing

| Rule | Invariant | Code | Test | Evidence | Status |
|---|---|---|---|---|---|
| Money is Decimal(10,2), non-negative | B4 | Decimal fields | form validation exists | RC1 suite | ✅ |
| `total_due = fine_amount + majoration_amount` | — | property | property test exists | RC1 suite | ✅ |
| Rate computation from `daily_rate` × duration | — | — | — | — | 🔲 not modeled |
| Deposit / rounding / currency policy | — | — | — | — | 🔲 Phase 2 |

## Uniqueness (cross-cutting)
- Plates/CINs globally unique today; **per-company uniqueness** is a Business
  Rules Review question → 🔲 tracked in Phase 2A.

## Gap list (owned)

| # | Gap | Context | Owner (tracked in) |
|---|---|---|---|
| G1 | B3 reference test (window validity) | booking | Phase 2D |
| G2 | B4 reference test (money non-negative) | booking/pricing | Phase 2D |
| G3 | B5 reference test (state machine) | booking | Phase 2D |
| G4 | B6 reference test (PROTECT) | booking | Phase 2D |
| G5 | B1 "adjacent windows allowed" unit test | booking | Phase 2D |
| G6 | F5 file-hygiene test | fleet | Phase 2D |
| G7 | maintenance-due derived-state test | fleet | Phase 2D |
| G8 | violation derived-state test | fleet | Phase 2D |
| G9 | expired-doc-blocks-rental policy | fleet | Phase 2A |
| G10 | per-company uniqueness of plates/CINs | fleet | Phase 2A |
| G11 | rate computation from daily_rate | pricing | Phase 2A |
| G12 | deposit/rounding/currency policy | pricing | Phase 2A |

## Verdict
Chain structure present for every represented rule. 12 gaps — all owned and
tracked in `platform/ROADMAP.md` Phase 2. No silent break. **PASS (gaps
owned).**
