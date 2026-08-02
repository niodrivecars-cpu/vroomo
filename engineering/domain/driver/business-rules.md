# Driver — Business Rules

Source: `fleet/models.py` (Driver).

## Rules
1. **Tenant-owned** — `company` structural (F2).
2. **CIN unique** (global today — per-company question open, see fleet docs).
3. **License validity:** `license_expiry` is data; `is_active` is the business
   flag. An expired license does not auto-deactivate today — open rule.
4. **Bookings:** a driver can have many bookings (PROTECT on delete while
   booked).
5. **Violations:** can be auto-linked from the active booking
   (`test_violation_create_auto_links_driver...`).

## Invariants
- D1: company owned.
- D2: unique CIN.
- D3: driver referenced by a booking cannot be deleted (PROTECT).

## Edge cases
- **Inactive driver booked** — currently allowed; open question.
- **Expired license** — derived warning candidate; no rule yet.
- **Driver deleted with violations** — Violation.driver is SET_NULL (history
  preserved).

## Test matrix
| Case | Status |
|---|---|
| Tenant scoping | exists |
| Unique CIN enforced | exists |
| PROTECT under active booking | needed (Phase 2) |
| Violation keeps driver history on delete | needed |
