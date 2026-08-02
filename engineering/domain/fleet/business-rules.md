# Fleet — Business Rules

Source: `fleet/models.py` (Company, Vehicle, Driver, VehicleDocument, Maintenance,
Violation, AuditLog).

## Entities
- **Company** — the tenant; owns everything below it.
- **Vehicle** — license plate (unique), make/model/year, status, current_km,
  daily_rate. Documents, maintenances, bookings, violations attached.
- **VehicleDocument** — doc type, doc number, expiry date, private `file`,
  `original_filename`, `download_token_version` (for revoking signed links).
- **Driver** — CIN (unique), phone, license number/expiry, active flag.
- **Maintenance** — service record: km_at_service, type, cost, next-service
  km/date.
- **Violation** — type, fine + surcharge, deadlines, status, points, PV number.
- **AuditLog** — tenant-scoped action trail.

## Core rules
1. **Tenant ownership (isolation):** every entity carries `company`; access and
   queries are tenant-scoped (structural, see `patterns/multi-tenant/`).
2. **Documents are private + expiring:** served only via signed URLs with expiry;
   `revoke_download_links()` invalidates previously issued links (version bump).
3. **Physical file hygiene:** replacing/deleting a document deletes the
   superseded file best-effort without aborting the DB write.
4. **Maintenance due** is derived: `is_due` when `current_km >= next_service_km`
   OR today >= next_service_date.
5. **Violation total:** `total_due = fine_amount + majoration_amount`;
   `is_overdue` when past deadline and not paid.

## Uniqueness (business + integrity)
- License plate unique; CIN unique. Both global (not per-company) in the current
  schema — a Business Rules Review question: should they be per-company?
