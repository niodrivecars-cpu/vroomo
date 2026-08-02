# Policies — Governance Register

The **source of truth** for business policies. Phase 2A is **Business Rule
Validation & Ownership**: the question is not "how do we implement everything"
but "is each policy itself correct?" — then approve, implement, test, and prove.

The cycle:

```text
Policy → Validate → Approve → Implement → Test → Evidence
```

## Status (Decision) legend

| Status | Meaning |
|---|---|
| ✅ Enforced | Correct commercially AND implemented AND proven by tests |
| 🟡 Validated | Correct commercially, approved, **not yet implemented** (or not fully tested) |
| 🔵 Proposed | A proposal awaiting a decision |
| ⚪ Out of Scope | Deliberately not in v1.0 |
| ❌ Rejected | Reviewed and rejected, reason documented |

## Priority matrix

| Priority | Focus | Policies |
|---|---|---|
| P0 | Double booking, maintenance, isolation | P1, P3, P11, P15, P20, P21 |
| P1 | License, vehicle status, documents | P2, P4, P6, P12, P13, P16, P17 |
| P2 | Money, deposits, deadlines | P5, P7, P8, P9, P10, P19 |
| P3 | Future improvements | P14, P18 |

## Risk dimensions

`Operational` · `Financial` · `Security` · `Legal` · `Customer Experience`
(plus specific flags like `Fraud`, `Audit`, `Safety` where relevant).

## Source types
`Law` · `Business Requirement` · `Operational Practice` · `Internal Decision` ·
`Security Requirement` · `Engineering Proposal`

---

# P1 — Vehicle cannot be booked while under maintenance

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Critical |
| Source | Moroccan Rental Business Practice (safety) |
| Risk | Operational · Safety · Customer Experience |
| Priority | P0 |
| Decision | 🟡 Validated |
| Implementation | Missing — booking checks window overlap only (B1) |
| Tests | Missing |

**Chain:** P1 → *new invariant (2B)* → Vehicle/Booking → CreateBooking →
BookingCreated → 2D → Missing → —

---

# P2 — Only active vehicles may be reserved

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | High |
| Source | Internal Decision |
| Risk | Operational · Customer Experience |
| Priority | P1 |
| Decision | 🟡 Validated |
| Implementation | Missing — `out_of_service`/inactive not consulted at booking |
| Tests | Missing |

**Chain:** P2 → *new invariant (2B)* → Vehicle → CreateBooking → BookingCreated →
2D → Missing → —

---

# P3 — A vehicle is effectively reserved from pickup to expected return

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | High |
| Source | Internal Decision |
| Risk | Operational · Customer Experience |
| Priority | P0 |
| Decision | 🟡 Validated (derived behavior exists; not proven by dedicated test) |
| Implementation | Present — derived from confirmed/rented bookings |
| Tests | Missing (2D) |

**Chain:** P3 → B1 → Vehicle/Booking → CreateBooking/ReturnVehicle →
BookingPickedUp/BookingReturned → 2D → view/query layer → k6 + suite (partial)

---

# P4 — Driver license must be valid at pickup

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Critical |
| Source | Moroccan Rental Business Practice (regulatory) |
| Risk | Legal · Operational |
| Priority | P1 |
| Decision | 🟡 Validated |
| Implementation | Missing — `license_expiry` stored, never checked |
| Tests | Missing |

**Chain:** P4 → *new invariant (2B)* → Driver → StartRental → — → 2D → Missing → —

---

# P5 — Booking cannot finish before it starts

| Field | Value |
|---|---|
| Owner | Operations |
| Criticality | High |
| Source | Internal Decision |
| Risk | Customer Experience · Operational |
| Priority | P2 |
| Decision | 🟡 Validated |
| Implementation | Present — form validation (B3) |
| Tests | Missing (2D) |

**Chain:** P5 → B3 → Booking → CreateBooking → — → 2D → form validation → suite

---

# P6 — Mileage must never decrease

| Field | Value |
|---|---|
| Owner | Fleet Manager / Finance |
| Criticality | High |
| Source | Internal Decision |
| Risk | Financial · Fraud · Audit |
| Priority | P1 |
| Decision | 🟡 Validated |
| Implementation | Missing — `current_km`/`return_km` have no monotonic guard |
| Tests | Missing |

**Chain:** P6 → *new invariant (2B)* → Vehicle/Booking → ReturnVehicle →
— → 2D → Missing → —

---

# P7 — Money is Decimal(10,2) and non-negative

| Field | Value |
|---|---|
| Owner | Finance |
| Criticality | High |
| Source | Internal Decision |
| Risk | Financial |
| Priority | P2 |
| Decision | 🟡 Validated |
| Implementation | Present — model/form validation (B4) |
| Tests | Missing (2D) |

**Chain:** P7 → B4 → Booking/Violation → CreateBooking/CreateViolation →
— → 2D → validation → suite

---

# P8 — Deposit cannot exceed the booking value

| Field | Value |
|---|---|
| Owner | Finance |
| Criticality | Medium |
| Source | Engineering Proposal |
| Risk | Financial · Customer Experience |
| Priority | P2 |
| Decision | 🔵 Proposed — a security deposit may legitimately exceed one rental's
value (high-value vehicle, long window); needs a domain decision |
| Implementation | Missing |
| Tests | Missing |

**Chain:** P8 → *new invariant (2B)* → Booking → CreateBooking → — → 2D → Missing → —

---

# P9 — Violation total = fine + surcharge

| Field | Value |
|---|---|
| Owner | Finance |
| Criticality | High |
| Source | Law (fine majoration) |
| Risk | Financial · Legal |
| Priority | P2 |
| Decision | ✅ Enforced |
| Implementation | Present — `total_due` property |
| Tests | Present |

**Chain:** P9 → *property test* → Violation → CreateViolation → — → model test →
suite

---

# P10 — Violation is overdue past deadline and unpaid

| Field | Value |
|---|---|
| Owner | Finance |
| Criticality | High |
| Source | Internal Decision |
| Risk | Legal · Financial |
| Priority | P2 |
| Decision | 🟡 Validated |
| Implementation | Present — `is_overdue` property |
| Tests | Missing (2D) |

**Chain:** P10 → *new invariant (2B)* → Violation → — → — → 2D → `is_overdue` →
suite

---

# P11 — Every entity is tenant-scoped; cross-tenant access denied

| Field | Value |
|---|---|
| Owner | Platform / Security |
| Criticality | Critical |
| Source | Security Requirement |
| Risk | Security |
| Priority | P0 |
| Decision | ✅ Enforced |
| Implementation | Present — `TenantScopedModel` + view-layer scoping |
| Tests | Present — IDOR + k6 |

**Chain:** P11 → F1/F2 → all entities → all commands → — → IDOR tests →
suite + k6 → RC1 evidence

---

# P12 — Documents are private and expire

| Field | Value |
|---|---|
| Owner | Platform / Security |
| Criticality | Critical |
| Source | Security Requirement |
| Risk | Security · Legal |
| Priority | P1 |
| Decision | ✅ Enforced |
| Implementation | Present — signed URLs with TTL |
| Tests | Present |

**Chain:** P12 → F3 → VehicleDocument → DownloadDocument → DocumentDownloaded →
signed/expired/tampered tests → suite + k6 `dl-*` → RC1 evidence

---

# P13 — Revoked links stop working

| Field | Value |
|---|---|
| Owner | Platform / Security |
| Criticality | Critical |
| Source | Security Requirement |
| Risk | Security |
| Priority | P1 |
| Decision | ✅ Enforced |
| Implementation | Present — `download_token_version` |
| Tests | Present |

**Chain:** P13 → F4 → VehicleDocument → RevokeDownloadLinks →
DocumentLinksRevoked → revoke test → suite → RC1 evidence

---

# P14 — Superseded document files are removed best-effort

| Field | Value |
|---|---|
| Owner | Engineering |
| Criticality | Low |
| Source | Internal Decision |
| Risk | Operational |
| Priority | P3 |
| Decision | 🟡 Validated |
| Implementation | Present — `VehicleDocument.save/delete` best-effort cleanup |
| Tests | Missing (2D) |

**Chain:** P14 → F5 → VehicleDocument → UploadDocument → — → 2D → save/delete →
suite

---

# P15 — Vehicle status stays consistent with active bookings

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Critical |
| Source | Internal Decision |
| Risk | Operational · Financial |
| Priority | P0 |
| Decision | 🟡 Validated |
| Implementation | Missing — status edits can contradict a booking window |
| Tests | Missing |

**Chain:** P15 → *new invariant (2B)* → Vehicle → SetVehicleStatus → — →
2D → Missing → —

---

# P16 — An expired document blocks rental

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Medium |
| Source | Engineering Proposal (compliance consideration) |
| Risk | Legal · Operational · Customer Experience |
| Priority | P1 |
| Decision | 🔵 Proposed — blocking may be wrong for some doc types (e.g. vignette);
needs a per-type decision |
| Implementation | Missing |
| Tests | Missing |

**Chain:** P16 → *new invariant (2B)* → VehicleDocument → CreateBooking →
— → 2D → Missing → —

---

# P17 — License plates and CINs are unique

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | High |
| Source | Internal Decision |
| Risk | Legal · Operational |
| Priority | P1 |
| Decision | ✅ Enforced (globally) |
| Implementation | Present — `unique=True` |
| Tests | Present — model tests |

**Chain:** P17 → F6 → Vehicle/Driver → CreateVehicle/CreateDriver → — → model
tests → suite

---

# P18 — Plates/CINs unique per company

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Medium |
| Source | Engineering Proposal |
| Risk | Operational |
| Priority | P3 |
| Decision | 🔵 Proposed — global uniqueness is safer; per-company needs a
multi-tenant expansion decision |
| Implementation | Missing |
| Tests | Missing |

**Chain:** P18 → *new invariant (2B)* → Vehicle/Driver → — → — → 2D → Missing → —

---

# P19 — Violations auto-link to the active booking driver

| Field | Value |
|---|---|
| Owner | Operations |
| Criticality | High |
| Source | Internal Decision |
| Risk | Legal · Operational |
| Priority | P2 |
| Decision | ✅ Enforced |
| Implementation | Present — view logic |
| Tests | Present |

**Chain:** P19 → *view behavior* → Violation/Booking/Driver → CreateViolation →
ViolationRecorded → auto-link test → suite

---

# P20 — Two non-cancelled bookings of one vehicle never overlap

| Field | Value |
|---|---|
| Owner | Fleet Manager |
| Criticality | Critical |
| Source | Moroccan Rental Business Practice (double-booking) |
| Risk | Operational · Financial · Customer Experience |
| Priority | P0 |
| Decision | ✅ Enforced |
| Implementation | Present — check-then-insert + retry (ADR 0005) |
| Tests | Present — k6 `sameVehicleBooking`; adjacent-window unit test needed (2D) |

**Chain:** P20 → B1 → Booking → CreateBooking → BookingCreated → k6 + view test
→ RC1 evidence

---

# P21 — Derived states are computed, never stored

| Field | Value |
|---|---|
| Owner | Platform |
| Criticality | High |
| Source | Internal Decision |
| Risk | Operational |
| Priority | P0 |
| Decision | ✅ Enforced |
| Implementation | Present — `is_late`, `is_due`, `is_overdue`, `is_expired` |
| Tests | Present (derivations covered; per-entity tests in 2D) |

**Chain:** P21 → B5 + derived-state invariants → Booking/Maintenance/Violation/
VehicleDocument → state commands → — → derivation tests → suite

---

## Register summary

| Status | Count | Policies |
|---|---|---|
| ✅ Enforced | 8 | P9, P11, P12, P13, P17, P19, P20, P21 |
| 🟡 Validated | 10 | P1, P2, P3, P4, P5, P6, P7, P10, P14, P15 |
| 🔵 Proposed | 3 | P8, P16, P18 |
| ⚪ Out of Scope | 0 | — |
| ❌ Rejected | 0 | — |

## Phase 2A acceptance
Every policy has owner, source, decision, risk, priority, and chain — verified by
the Business Completeness Gate. Validated-but-missing policies (P1, P2, P4, P6,
P15) then move through Approve → Implement → Test → Evidence. Proposed policies
(P8, P16, P18) get a domain decision.
