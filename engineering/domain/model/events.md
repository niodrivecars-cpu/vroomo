# Events

The canonical business event catalog. Status per README:
- **Real** — observable today (status transitions, audit actions).
- **Derived** — computed from data, not emitted.
- **Aspirational** — the business wants them; **no emission code exists** (Phase 2A
  decides whether to emit).

## Real (observable)

| Event | Trigger | Evidence |
|---|---|---|
| BookingCreated | booking created | AuditLog `CREATE` (booking) |
| BookingCancelled | confirmed → cancelled | AuditLog `CHANGE_STATUS` |
| BookingPickedUp | confirmed → rented | AuditLog `PICKUP` |
| BookingReturned | rented → returned | AuditLog `RETURN` |
| VehicleStatusChanged | vehicle status change | AuditLog `CHANGE_STATUS` |
| DocumentUploaded | VehicleDocument created | AuditLog `CREATE` |
| DocumentDownloaded | signed URL served | AuditLog `DOWNLOAD` |
| DocumentLinksRevoked | `revoke_download_links()` | `download_token_version` bump |
| ViolationRecorded | violation created | AuditLog `CREATE` (violation) |
| Login / Logout / LoginFailed | auth events | AuditLog `LOGIN`/`LOGOUT`/`LOGIN_FAILED` |

## Derived (computed, never stored, never emitted)

| Event | Rule | Where |
|---|---|---|
| BookingLate | `rented` and now > expected_return | `Booking.is_late` |
| VehicleMaintenanceDue | km ≥ next_service_km OR date ≥ next_service_date | `Maintenance.is_due` |
| DocumentExpired / DocumentExpiringSoon | from `expiry_date` | `VehicleDocument.is_expired` / `is_expiring_soon` |
| ViolationOverdue | past deadline and not paid | `Violation.is_overdue` |

## Aspirational (no emission code yet)

| Event | Needed by | Status |
|---|---|---|
| MaintenanceStarted / MaintenanceCompleted | maintenance tracking | 🔲 |
| InvoiceIssued | invoicing (not modeled) | 🔲 |
| PaymentRecorded | payments (not modeled) | 🔲 |
| VehicleReserved | UX/availability views | 🔲 — today "reserved" is a query over confirmed bookings |

## Rules
1. Events are named in the past tense, from the business, not the table
   (`BookingPickedUp`, not `booking_pickup_1`).
2. Derived events are never persisted — they are queries.
3. When an event becomes a real emit (e.g. Notification), it moves from
   Aspirational to Real here **first**, then in code.
