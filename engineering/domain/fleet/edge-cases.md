# Fleet — Edge Cases

## Documents
- **Expired document upload/retention** — documents have `expiry_date`;
  `is_expiring_soon` (<=30 days) and `is_expired` are derived. Business question:
  must an expired document block vehicle rental? (open)
- **Replacing a document file** — old file deleted best-effort; if deletion fails
  (OSError), DB write still succeeds and a warning is logged (non-fatal).
- **Revoke links then re-issue** — after `revoke_download_links()`, old tokens
  fail; new links must be re-signed (version mismatch).
- **Tampered signature / wrong doc pk / wrong company in token** → 403/404.

## Maintenance
- **next_service_km AND next_service_date both set** → due when either triggers.
- **current_km > next_service_km at service time** → is_due already true; plan
  next interval from actuals.
- **km_at_service vs vehicle.current_km drift** → which wins for "due" calc?

## Violations
- **Violation without a driver** → driver is SET_NULL; auto-link to active
  booking's driver when booking exists (`test_violation_create_auto_links_driver`).
- **Overdue with surcharge** → total_due grows; is_overdue derived from deadline.
- **Paid after deadline** → is_overdue false once paid (status check).

## Tenant
- **Global uniqueness vs per-company** — plate/CIN unique globally today; two
  companies with the same plate is impossible — confirm that's desired.
- **AuditLog company null** (anonymous/system actions) → company may be null;
  queries must handle it.
