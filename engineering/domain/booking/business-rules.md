# Booking — Business Rules

Source: `fleet/models.py` (Booking).

## Entities & roles
- **Booking** belongs to a company (tenant-scoped), references a `vehicle`
  (PROTECT), a `driver` (PROTECT), and carries `customer_name`/`customer_phone`.
- Window: `pickup_date` → `expected_return` (both DateTime). Actuals:
  `actual_return`, `pickup_km`, `return_km`.

## Core rules
1. **Exclusivity:** a vehicle cannot be booked for a window that overlaps an
   existing (non-cancelled) booking of the same vehicle. Enforced
   check-then-insert; proven under load (`same_vehicle_booking_success == 1`).
2. **Tenant scope:** a booking can only reference vehicles and drivers of the
   same company. Cross-company references are invalid (isolation invariant).
3. **Money:** `total_amount` and `deposit` are Decimal (max_digits=10,
   decimal_places=2), non-negative by validation.
4. **Window validity:** `expected_return` must be after `pickup_date`.
5. **Status lifecycle:** confirmed → rented → returned; cancelled is terminal;
   `late` is derived (see `state-machine.md`).

## Derived values
- `is_late`: status == 'rented' and now > expected_return.
- `days_late`: whole days past expected_return while rented.

## Load-test model note
Day bands are per-VU (`40 + __VU * ITERATIONS + __ITER`) in smoke tests to keep
conflict space distinct; the `sameVehicleBooking` scenario deliberately forces
contention to prove rule 1.
