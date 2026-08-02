# Policies — Governance Register

The **source of truth** for business policies. Phase 2A is **Business Rule
Validation & Ownership**: the question is not "how do we implement everything"
but "is each policy itself correct?" — then approve, implement, test, and prove.

Every policy carries a formal **rule block** — Business Rule Language v2
(`kernel/rule-language.md`) — parsed and validated by the Engineering Compiler
(`kernel/engineering-compiler.md`, `kernel/compiler/validate_rules.py`).

```text
Policy → Validate → Approve → Implement → Test → Evidence
```

## The three dimensions

| Dimension | Question | Values |
|---|---|---|
| **DECISION** | Is the policy agreed? | `Enforced` · `Validated` · `Proposed` · `Out of Scope` · `Rejected` |
| **ENFORCEMENT** | Is it real in the system? | `PLANNED` · `DOCUMENTED` · `IMPLEMENTED` · `TESTED` |
| **SEVERITY** | What if it breaks? | `BLOCKER` · `ERROR` · `WARNING` · `INFO` |

`DECISION` and `ENFORCEMENT` are independent: `Validated` + `DOCUMENTED` means
agreed but not built.

## Priority matrix

| Priority | Focus | Policies |
|---|---|---|
| P0 | Double booking, maintenance, isolation | P1, P3, P11, P15, P20, P21 |
| P1 | License, vehicle status, documents | P2, P4, P6, P12, P13, P16, P17 |
| P2 | Money, deposits, deadlines | P5, P7, P8, P9, P10, P19 |
| P3 | Future improvements | P14, P18 |

## Risk dimensions
`Operational` · `Financial` · `Security` · `Legal` · `Customer Experience`
(plus specific flags like `Fraud`, `Audit`, `Safety`).

---

# P1 — Vehicle cannot be booked while under maintenance

```rule
ID: P1
STATEMENT: A vehicle must not be booked while it is under maintenance
PREDICATE: Vehicle.status != MAINTENANCE
WHEN: Booking.create
UNLESS: override.approved(role=manager)
REQUIRES: role.manager
EVIDENCE: — (missing)
RISKS: Operational, Safety, Customer Experience
PRIORITY: P0
SEVERITY: BLOCKER
DECISION: Validated
ENFORCEMENT: DOCUMENTED
OWNER: Fleet Manager
SOURCE: Operational Practice (Moroccan Rental Business Practice)
```

| Implementation | Missing — booking checks window overlap only (B1) |
|---|---|
| Tests | Missing |

**Chain:** P1 → *new invariant (2B.1)* → Vehicle/Booking → CreateBooking →
BookingCreated → 2D → Missing → —

---

# P2 — Only active vehicles may be reserved

```rule
ID: P2
STATEMENT: Only active vehicles may be reserved
PREDICATE: Vehicle.status != OUT_OF_SERVICE AND Company.is_active == true
WHEN: Booking.create
UNLESS: —
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Operational, Customer Experience
PRIORITY: P1
SEVERITY: ERROR
DECISION: Validated
ENFORCEMENT: DOCUMENTED
OWNER: Fleet Manager
SOURCE: Internal Decision
```

| Implementation | Missing — `out_of_service`/inactive not consulted at booking |
|---|---|
| Tests | Missing |

**Chain:** P2 → *new invariant (2B.1)* → Vehicle → CreateBooking → BookingCreated →
2D → Missing → —

---

# P3 — A vehicle is effectively reserved from pickup to expected return

```rule
ID: P3
STATEMENT: A vehicle is effectively reserved from pickup to expected return
PREDICATE: effective_reserved(v) == exists(Booking b: b.vehicle == v AND b.status IN (confirmed, rented))
WHEN: Booking.create, Booking.return
UNLESS: —
REQUIRES: —
EVIDENCE: B1 (partial)
RISKS: Operational, Customer Experience
PRIORITY: P0
SEVERITY: ERROR
DECISION: Validated
ENFORCEMENT: IMPLEMENTED
OWNER: Fleet Manager
SOURCE: Internal Decision
```

| Implementation | Present — derived from confirmed/rented bookings |
|---|---|
| Tests | Missing (2D) |

**Chain:** P3 → B1 → Vehicle/Booking → CreateBooking/ReturnVehicle →
BookingPickedUp/BookingReturned → 2D → view/query layer → k6 + suite (partial)

---

# P4 — Driver license must be valid at pickup

```rule
ID: P4
STATEMENT: Driver license must be valid at pickup
PREDICATE: Driver.license_expiry > now
WHEN: Booking.pickup
UNLESS: override.approved(role=manager)
REQUIRES: role.manager
EVIDENCE: — (missing)
RISKS: Legal, Operational
PRIORITY: P1
SEVERITY: BLOCKER
DECISION: Validated
ENFORCEMENT: DOCUMENTED
OWNER: Fleet Manager
SOURCE: Law (regulatory)
```

| Implementation | Missing — `license_expiry` stored, never checked |
|---|---|
| Tests | Missing |

**Chain:** P4 → *new invariant (2B.1)* → Driver → StartRental → — → 2D → Missing → —

---

# P5 — Booking cannot finish before it starts

```rule
ID: P5
STATEMENT: A booking cannot finish before it starts
PREDICATE: Booking.end_date >= Booking.start_date
WHEN: Booking.create
UNLESS: —
REQUIRES: —
EVIDENCE: B3
RISKS: Customer Experience, Operational
PRIORITY: P2
SEVERITY: WARNING
DECISION: Validated
ENFORCEMENT: IMPLEMENTED
OWNER: Operations
SOURCE: Internal Decision
```

| Implementation | Present — form validation (B3) |
|---|---|
| Tests | Missing (2D) |

**Chain:** P5 → B3 → Booking → CreateBooking → — → 2D → form validation → suite

---

# P6 — Mileage must never decrease

```rule
ID: P6
STATEMENT: Mileage must never decrease
PREDICATE: Booking.return_km >= Booking.pickup_km AND Vehicle.current_km >= max(Booking.return_km)
WHEN: Booking.return
UNLESS: —
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Financial, Fraud, Audit
PRIORITY: P1
SEVERITY: ERROR
DECISION: Validated
ENFORCEMENT: DOCUMENTED
OWNER: Fleet Manager
SOURCE: Internal Decision
```

| Implementation | Missing — `current_km`/`return_km` have no monotonic guard |
|---|---|
| Tests | Missing |

**Chain:** P6 → *new invariant (2B.1)* → Vehicle/Booking → ReturnVehicle →
— → 2D → Missing → —

---

# P7 — Money is Decimal(10,2) and non-negative

```rule
ID: P7
STATEMENT: Money is Decimal(10,2) and non-negative
PREDICATE: forall(m in money_fields): m >= 0 AND type(m) == Decimal(10,2)
WHEN: Booking.create, Violation.create
UNLESS: —
REQUIRES: —
EVIDENCE: B4
RISKS: Financial
PRIORITY: P2
SEVERITY: ERROR
DECISION: Validated
ENFORCEMENT: IMPLEMENTED
OWNER: Finance
SOURCE: Internal Decision
```

| Implementation | Present — model/form validation (B4) |
|---|---|
| Tests | Missing (2D) |

**Chain:** P7 → B4 → Booking/Violation → CreateBooking/CreateViolation →
— → 2D → validation → suite

---

# P8 — Deposit cannot exceed the booking value

```rule
ID: P8
STATEMENT: Deposit cannot exceed the booking value
PREDICATE: Booking.deposit <= Booking.value
WHEN: Booking.create
UNLESS: decision pending — a security deposit may exceed one rental's value
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Financial, Customer Experience
PRIORITY: P2
SEVERITY: WARNING
DECISION: Proposed
ENFORCEMENT: PLANNED
OWNER: Finance
SOURCE: Engineering Proposal
```

| Implementation | Missing |
|---|---|
| Tests | Missing |

**Chain:** P8 → *new invariant (2B.1)* → Booking → CreateBooking → — → 2D → Missing → —

---

# P9 — Violation total = fine + surcharge

```rule
ID: P9
STATEMENT: Violation total equals fine plus surcharge
PREDICATE: Violation.total_due == Violation.fine_amount + Violation.majoration_amount
WHEN: Violation.create
UNLESS: —
REQUIRES: —
EVIDENCE: violation-model-test
RISKS: Financial, Legal
PRIORITY: P2
SEVERITY: ERROR
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Finance
SOURCE: Law (fine majoration)
```

| Implementation | Present — `total_due` property |
|---|---|
| Tests | Present |

**Chain:** P9 → *property test* → Violation → CreateViolation → — → model test →
suite

---

# P10 — Violation is overdue past deadline and unpaid

```rule
ID: P10
STATEMENT: A violation is overdue past its deadline and unpaid
PREDICATE: Violation.is_overdue == (now > Violation.payment_deadline AND Violation.status != PAID)
WHEN: Violation.create
UNLESS: —
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Legal, Financial
PRIORITY: P2
SEVERITY: WARNING
DECISION: Validated
ENFORCEMENT: IMPLEMENTED
OWNER: Finance
SOURCE: Internal Decision
```

| Implementation | Present — `is_overdue` property |
|---|---|
| Tests | Missing (2D) |

**Chain:** P10 → *new invariant (2B.1)* → Violation → — → — → 2D → `is_overdue` →
suite

---

# P11 — Every entity is tenant-scoped; cross-tenant access denied

```rule
ID: P11
STATEMENT: Every entity is tenant-scoped; cross-tenant access is denied
PREDICATE: forall(query): query.tenant == session.tenant
WHEN: ALL
UNLESS: —
REQUIRES: —
EVIDENCE: idor-tests, k6
RISKS: Security
PRIORITY: P0
SEVERITY: BLOCKER
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Platform
SOURCE: Security Requirement
```

| Implementation | Present — `TenantScopedModel` + view-layer scoping |
|---|---|
| Tests | Present — IDOR + k6 |

**Chain:** P11 → F1/F2 → all entities → all commands → — → IDOR tests →
suite + k6 → RC1 evidence

---

# P12 — Documents are private and expire

```rule
ID: P12
STATEMENT: Documents are private and expire
PREDICATE: VehicleDocument.access == PRIVATE AND link.ttl <= MAX_TTL
WHEN: Document.download
UNLESS: —
REQUIRES: —
EVIDENCE: signed-download-tests
RISKS: Security, Legal
PRIORITY: P1
SEVERITY: BLOCKER
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Platform
SOURCE: Security Requirement
```

| Implementation | Present — signed URLs with TTL |
|---|---|
| Tests | Present |

**Chain:** P12 → F3 → VehicleDocument → DownloadDocument → DocumentDownloaded →
signed/expired/tampered tests → suite + k6 `dl-*` → RC1 evidence

---

# P13 — Revoked links stop working

```rule
ID: P13
STATEMENT: Revoked download links stop working
PREDICATE: link.valid == (download_token_version unchanged)
WHEN: Document.download
UNLESS: —
REQUIRES: —
EVIDENCE: revoke-test
RISKS: Security
PRIORITY: P1
SEVERITY: BLOCKER
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Platform
SOURCE: Security Requirement
```

| Implementation | Present — `download_token_version` |
|---|---|
| Tests | Present |

**Chain:** P13 → F4 → VehicleDocument → RevokeDownloadLinks →
DocumentLinksRevoked → revoke test → suite → RC1 evidence

---

# P14 — Superseded document files are removed best-effort

```rule
ID: P14
STATEMENT: Superseded document files are removed best-effort
PREDICATE: on_replace(VehicleDocument) => delete(old_file)
WHEN: Document.upload
UNLESS: best-effort — storage errors are logged, not fatal
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Operational
PRIORITY: P3
SEVERITY: INFO
DECISION: Validated
ENFORCEMENT: IMPLEMENTED
OWNER: Engineering
SOURCE: Internal Decision
```

| Implementation | Present — `VehicleDocument.save/delete` best-effort cleanup |
|---|---|
| Tests | Missing (2D) |

**Chain:** P14 → F5 → VehicleDocument → UploadDocument → — → 2D → save/delete →
suite

---

# P15 — Vehicle status stays consistent with active bookings

```rule
ID: P15
STATEMENT: Vehicle status stays consistent with active bookings
PREDICATE: (NOT exists(active booking) => Vehicle.status != RENTED) AND (Vehicle.status == MAINTENANCE => NOT exists(active booking))
WHEN: Vehicle.set_status
UNLESS: —
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Operational, Financial
PRIORITY: P0
SEVERITY: BLOCKER
DECISION: Validated
ENFORCEMENT: DOCUMENTED
OWNER: Fleet Manager
SOURCE: Internal Decision
```

| Implementation | Missing — status edits can contradict a booking window |
|---|---|
| Tests | Missing |

**Chain:** P15 → *new invariant (2B.1)* → Vehicle → SetVehicleStatus → — →
2D → Missing → —

---

# P16 — An expired document blocks rental

```rule
ID: P16
STATEMENT: An expired document blocks rental
PREDICATE: VehicleDocument.is_expired == true => NOT Booking.create
WHEN: Booking.create
UNLESS: decision pending — may not apply to all doc types (e.g. vignette)
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Legal, Operational, Customer Experience
PRIORITY: P1
SEVERITY: WARNING
DECISION: Proposed
ENFORCEMENT: PLANNED
OWNER: Fleet Manager
SOURCE: Engineering Proposal
```

| Implementation | Missing |
|---|---|
| Tests | Missing |

**Chain:** P16 → *new invariant (2B.1)* → VehicleDocument → CreateBooking →
— → 2D → Missing → —

---

# P17 — License plates and CINs are unique

```rule
ID: P17
STATEMENT: License plates and CINs are unique
PREDICATE: unique(Vehicle.plate) AND unique(Driver.cin)
WHEN: Vehicle.create, Driver.create
UNLESS: —
REQUIRES: —
EVIDENCE: model-unique-tests
RISKS: Legal, Operational
PRIORITY: P1
SEVERITY: ERROR
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Fleet Manager
SOURCE: Internal Decision
```

| Implementation | Present — `unique=True` |
|---|---|
| Tests | Present — model tests |

**Chain:** P17 → F6 → Vehicle/Driver → CreateVehicle/CreateDriver → — → model
tests → suite

---

# P18 — Plates/CINs unique per company

```rule
ID: P18
STATEMENT: License plates and CINs are unique per company
PREDICATE: unique(Vehicle.plate, Company) AND unique(Driver.cin, Company)
WHEN: Vehicle.create, Driver.create
UNLESS: decision pending — global uniqueness is safer; needs multi-tenant expansion decision
REQUIRES: —
EVIDENCE: — (missing)
RISKS: Operational
PRIORITY: P3
SEVERITY: INFO
DECISION: Proposed
ENFORCEMENT: PLANNED
OWNER: Fleet Manager
SOURCE: Engineering Proposal
```

| Implementation | Missing |
|---|---|
| Tests | Missing |

**Chain:** P18 → *new invariant (2B.1)* → Vehicle/Driver → — → — → 2D → Missing → —

---

# P19 — Violations auto-link to the active booking driver

```rule
ID: P19
STATEMENT: Violations auto-link to the active booking driver
PREDICATE: Violation.driver == active_booking(Violation.vehicle).driver
WHEN: Violation.create
UNLESS: —
REQUIRES: —
EVIDENCE: auto-link-test
RISKS: Legal, Operational
PRIORITY: P2
SEVERITY: ERROR
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Operations
SOURCE: Internal Decision
```

| Implementation | Present — view logic |
|---|---|
| Tests | Present |

**Chain:** P19 → *view behavior* → Violation/Booking/Driver → CreateViolation →
ViolationRecorded → auto-link test → suite

---

# P20 — Two non-cancelled bookings of one vehicle never overlap

```rule
ID: P20
STATEMENT: Two non-cancelled bookings of one vehicle never overlap
PREDICATE: NOT exists(Booking b2: b2.vehicle == v AND b2.status IN (confirmed, rented) AND overlaps(b2, new_booking))
WHEN: Booking.create
UNLESS: —
REQUIRES: —
EVIDENCE: k6.sameVehicleBooking, B1-tests
RISKS: Operational, Financial, Customer Experience
PRIORITY: P0
SEVERITY: BLOCKER
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Fleet Manager
SOURCE: Operational Practice (double booking)
```

| Implementation | Present — check-then-insert + retry (ADR 0005) |
|---|---|
| Tests | Present — k6 `sameVehicleBooking`; adjacent-window unit test needed (2D) |

**Chain:** P20 → B1 → Booking → CreateBooking → BookingCreated → k6 + view test
→ RC1 evidence

---

# P21 — Derived states are computed, never stored

```rule
ID: P21
STATEMENT: Derived states are computed, never stored
PREDICATE: NOT exists(stored derived field) AND transitions via service layer only
WHEN: ALL
UNLESS: —
REQUIRES: —
EVIDENCE: derivation-tests
RISKS: Operational
PRIORITY: P0
SEVERITY: ERROR
DECISION: Enforced
ENFORCEMENT: TESTED
OWNER: Platform
SOURCE: Internal Decision
```

| Implementation | Present — `is_late`, `is_due`, `is_overdue`, `is_expired` |
|---|---|
| Tests | Present (derivations covered; per-entity tests in 2D) |

**Chain:** P21 → B5 + derived-state invariants → Booking/Maintenance/Violation/
VehicleDocument → state commands → — → derivation tests → suite

---

## Register summary

| Dimension | Count | Distribution |
|---|---|---|
| DECISION | Enforced 8 · Validated 10 · Proposed 3 | Enforced: P9, P11, P12, P13, P17, P19, P20, P21 |
| ENFORCEMENT | TESTED 8 · IMPLEMENTED 5 · DOCUMENTED 5 · PLANNED 3 | TESTED: P9, P11, P12, P13, P17, P19, P20, P21 |
| SEVERITY | BLOCKER 7 · ERROR 8 · WARNING 4 · INFO 2 | BLOCKER: P1, P4, P11, P12, P13, P15, P20 |

## Release posture
- **BLOCKER + below TESTED** (release blockers): P1, P4, P15 — each is the
  Phase 2A/2B implementation workload. The Business Completeness Gate fails a
  release while any BLOCKER is below `TESTED` or `DECISION != Enforced`.
- **ERROR + Validated**: P2, P3, P6, P7 — must be enforced and tested within the
  current milestone.
- **Proposed**: P8, P16, P18 — decisions go through the Decision Engine
  (`execution/pipelines/decision-pipeline.md`).

## Phase 2A acceptance
Every policy has owner, source, decision, enforcement, severity, priority, and a
validated v2 rule block — verified by the validator script and the Business
Completeness Gate. Validated-but-missing policies (P1, P2, P4, P6, P15) then
move through Approve → Implement → Test → Evidence. Proposed policies (P8, P16,
P18) get a domain decision via the Decision Engine.
