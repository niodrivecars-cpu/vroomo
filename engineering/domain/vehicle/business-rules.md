# Vehicle — Business Rules

Source: `fleet/models.py` (Vehicle).

## Rules
1. **Tenant-owned** — `company` is structural (isolation invariant F2).
2. **License plate unique** (global today — see `fleet/business-rules.md` for the
   open per-company question).
3. **Status** ∈ {available, rented, maintenance, out_of_service}; transitions per
   `fleet/state-machine.md`. `rented` is book-derived.
4. **Money:** `daily_rate` is Decimal (10,2), non-negative by validation.
5. **Documents:** zero or more `VehicleDocument`; all private/expiring (F3).
6. **Lifetime data:** `current_km` monotonic in practice (pickup/return km),
   maintained by bookings.

## Invariants
- V1: company owned (F1/F2).
- V2: unique plate (F6).
- V3: status always a valid enum value.

## Edge cases
- Vehicle deleted under active bookings → PROTECT (B6 applies via Booking FK).
- Deleting a vehicle deletes its documents (CASCADE) → physical files removed
  best-effort.
- Maintenance `is_due` while status == available → suggest taking it to
  maintenance (open rule).

## Test matrix
| Case | Status |
|---|---|
| Tenant scoping on list/detail | exists |
| Unique plate enforced | exists |
| Status transition guard | needed (Phase 2) |
| Document cascade + file cleanup | needed |
