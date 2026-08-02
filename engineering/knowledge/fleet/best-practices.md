# Fleet Knowledge — Best Practices

- **Scope every query by company** — use the shared tenant-scoping helper, not
  ad-hoc filters.
- **Enforce booking exclusivity at the view/service layer and prove it under
  load** (`same_vehicle_booking_success == 1`).
- **Keep documents private and signed**; never expose them from static.
- **Audit security-relevant fleet actions** (downloads, admin ops) with company
  and session context.
- **Link violations to their context** (active booking/driver) for a complete
  audit trail.
