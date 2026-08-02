# Policies

The **source of truth** for business policies. Phase 2A's question is not "are
there missing rules?" but "is every policy here represented in the system?".

Status per README:
- ✅ enforced + tested · ⚠️ enforced in code, no dedicated test · 🔲 **not
  enforced** (discovery gap) · 🧾 open decision.

## Rental & availability

| # | Policy | Status | Notes |
|---|---|---|---|
| P1 | A vehicle cannot be booked while under maintenance | 🔲 | Booking only checks window overlap (B1); vehicle.status is not checked. **Discovery gap.** |
| P2 | Only active vehicles may be reserved | 🔲 | `is_active`/`out_of_service` not consulted at booking. **Discovery gap.** |
| P3 | A vehicle is effectively reserved from pickup to expected return | ⚠️ | Derived from confirmed/rented bookings; no dedicated test |
| P4 | Driver license must be valid at pickup | 🔲 | `license_expiry` stored, never checked. **Discovery gap.** |
| P5 | Booking cannot finish before it starts (`expected_return > pickup_date`) | ✅ | B3, form validation (test needed) |
| P6 | Mileage must never decrease | 🔲 | `current_km`/`return_km` have no monotonic guard. **Discovery gap.** |

## Money

| # | Policy | Status | Notes |
|---|---|---|---|
| P7 | Money is Decimal(10,2) and non-negative | ✅ | B4, validation (test needed) |
| P8 | Deposit cannot exceed the booking value | 🔲 | No validation. **Discovery gap.** |
| P9 | Violation total = fine + surcharge | ✅ | `total_due` property + test |
| P10 | Violation is overdue past deadline and unpaid | ✅ | `is_overdue` (test needed) |

## Tenancy & documents

| # | Policy | Status | Notes |
|---|---|---|---|
| P11 | Every entity is tenant-scoped; cross-tenant access denied | ✅ | F1/F2, IDOR tests + k6 |
| P12 | Documents are private and expire | ✅ | F3, signed URLs + tests |
| P13 | Revoked links stop working | ✅ | F4, `download_token_version` + test |
| P14 | Superseded document files are removed best-effort | ⚠️ | F5, implemented, no test |
| P15 | Vehicle status stays consistent with active bookings | 🔲 | Status edits can contradict a booking. **Discovery gap.** |
| P16 | An expired document blocks rental | 🧾 | Policy question, not decided |

## Uniqueness & integrity

| # | Policy | Status | Notes |
|---|---|---|---|
| P17 | License plates and CINs are unique | ✅ | F6, model constraints + tests |
| P18 | Plates/CINs unique **per company** | 🧾 | Business question (open) |
| P19 | Violations auto-link to the active booking driver | ✅ | View logic + test |
| P20 | Two non-cancelled bookings of one vehicle never overlap | ✅ | B1, k6 + view test (adjacent-window unit test needed) |

## Derived-state discipline

| # | Policy | Status | Notes |
|---|---|---|---|
| P21 | Derived states are computed, never stored | ✅ | `is_late`, `is_due`, `is_overdue`, `is_expired` |

## How to read this file
- Every 🔲 row is a **Phase 2A discovery item** — the system does not enforce it
  today. It is either a bug (must fix) or a policy (must decide + implement).
- Every ⚠️ row needs a reference test (Phase 2D).
- Every 🧾 row needs a decision before it becomes a rule.
