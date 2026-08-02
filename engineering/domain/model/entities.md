# Entities

Canonical entity definitions. Status per `README.md`: ✅ represented /
🔲 planned but not represented.

## Company ✅

The tenant. Everything below it belongs to a company.

- **Responsibility:** ownership boundary and isolation unit.
- **Owner:** platform/operations.
- **Lifecycle:** created → active; `is_active` flag. No delete (cascade to all
  owned data is destructive — see relationships).
- **Constraints:** `name` unique; structural tenant boundary.
- **Relationships:** 1—N UserProfile, Vehicle, Driver, Booking, Maintenance,
  Violation, AuditLog.
- **Source:** `fleet/models.py` (Company).

## UserProfile ✅

- **Responsibility:** binds an auth user to one company (employment).
- **Owner:** platform/auth.
- **Lifecycle:** user → profile → company. CASCADE on company delete.
- **Constraints:** one profile per user (OneToOne); one company per profile.
- **Relationships:** N—1 Company; 1—1 User.

## Vehicle ✅

- **Responsibility:** the rentable asset; carries status, mileage, rate.
- **Owner:** fleet operations.
- **Lifecycle:** see `state-machines.md` (available → rented/maintenance/
  out_of_service). Derived "reserved" while a `confirmed` booking exists.
- **Constraints:** `license_plate` unique (global — per-company question open);
  `current_km` integer; `daily_rate` Decimal(10,2).
- **Relationships:** 1—N VehicleDocument (CASCADE), Booking (PROTECT),
  Maintenance (CASCADE), Violation (PROTECT); N—1 Company.
- **Source:** Vehicle in `fleet/models.py`.

## Booking ✅

- **Responsibility:** a reservation/rental window for one vehicle by one driver,
  with customer + money captured at booking time.
- **Owner:** rental operations.
- **Lifecycle:** see `state-machines.md` (confirmed → rented → returned;
  cancelled terminal; late derived).
- **Constraints:** B1 exclusivity; B2 tenant scope; B3 window validity; B4
  money non-negative; vehicle/driver PROTECT (B6).
- **Relationships:** N—1 Vehicle (PROTECT), Driver (PROTECT), Company; 1—N
  Violation (SET_NULL).
- **Source:** Booking in `fleet/models.py`.

## Customer 🧾 (not an entity today)

- **Status:** represented as embedded data on Booking (`customer_name`,
  `customer_phone`), not a model.
- **Phase 2A decision:** promote to an entity (contact, company-scope, history)
  or keep as a value object. Until decided, no separate lifecycle/constraints.

## Driver ✅

- **Responsibility:** a licensed person who can rent and be assigned violations.
- **Owner:** fleet operations.
- **Lifecycle:** created → active/inactive (`is_active`); no strong lifecycle.
- **Constraints:** `cin` unique (global — per-company question open);
  `license_expiry` stored (license-valid policy not enforced — see policies.md).
- **Relationships:** 1—N Booking (PROTECT), Violation (SET_NULL); N—1 Company.
- **Source:** Driver in `fleet/models.py`.

## Maintenance ✅

- **Responsibility:** a service record on a vehicle, with next-service forecast.
- **Owner:** fleet operations.
- **Lifecycle:** created per service; no status (derived `is_due`).
- **Constraints:** `cost` Decimal(10,2); `is_due` derived from km OR date.
- **Relationships:** N—1 Vehicle (CASCADE), Company.
- **Source:** Maintenance in `fleet/models.py`.

## Violation ✅

- **Responsibility:** a traffic violation tied to a vehicle (and usually a
  driver/booking), with fine, surcharge, deadlines.
- **Owner:** fleet operations / finance.
- **Lifecycle:** see `state-machines.md` (new → driver_designated → paid;
  disputed; overdue derived).
- **Constraints:** money Decimal(10,2); `total_due = fine + majoration`;
  `is_overdue` derived.
- **Relationships:** N—1 Vehicle (PROTECT), Driver (SET_NULL), Booking
  (SET_NULL), Company.
- **Source:** Violation in `fleet/models.py`.

## VehicleDocument ✅

- **Responsibility:** a vehicle's proof file (registration, insurance,
  inspection, vignette) with expiry and private, revocable download.
- **Owner:** fleet operations / compliance.
- **Lifecycle:** uploaded → (expiring soon → expired) derived from `expiry_date`;
  revoked links via `download_token_version` bump.
- **Constraints:** DOC_TYPE enum; expiry required; file private with
  extension/size/mime validation; download only via signed URLs.
- **Relationships:** N—1 Vehicle (CASCADE), Company.
- **Source:** VehicleDocument in `fleet/models.py`.

## AuditLog ✅

- **Responsibility:** append-only trace of security-relevant and status actions.
- **Owner:** platform/security.
- **Lifecycle:** created; never edited or deleted.
- **Constraints:** ACTION enum; company/session context recorded.
- **Relationships:** N—1 Company (SET_NULL), user (SET_NULL).
- **Source:** AuditLog in `fleet/models.py`.

## Invoice 🔲 (planned — not modeled)

- **Responsibility:** billing document for a booking/violation.
- **Status:** **zero representation.** Zero model, view, or test.
- **Phase 2A decision:** is invoicing in scope for v1? If yes, design here
  before any code.

## Payment 🔲 (planned — not modeled)

- **Responsibility:** a payment against an invoice/violation deposit.
- **Status:** **zero representation.** Deposit is a field on Booking; no payment
  ledger exists.
- **Phase 2A decision:** in scope? Ledger, refunds, currency?

## Policy decisions waiting (summarized)
Per-company uniqueness (plates/CIN), customer as entity, invoicing/payments in
scope, expired-doc blocks rental. Each is a Phase 2A item, tracked in
`platform/ROADMAP.md`.
