# Relationships

Canonical relationship map (from `fleet/models.py`). Notation: `1—N`, `N—1`,
`1—1`; deletion rule in parentheses.

## Ownership (Company is the tenant)

```
Company 1—N  UserProfile     (CASCADE)
Company 1—N  Vehicle         (CASCADE)
Company 1—N  Driver          (CASCADE)
Company 1—N  Booking         (CASCADE)
Company 1—N  Maintenance     (CASCADE)
Company 1—N  Violation       (CASCADE)
Company 1—N  VehicleDocument (via vehicle → CASCADE)
Company N—1  AuditLog        (SET_NULL)
```

Every tenant-scoped entity carries `company`; isolation is enforced at the query
layer (F1/F2).

## Rental graph

```
Vehicle 1—N  VehicleDocument  (CASCADE)   docs belong to the vehicle
Vehicle 1—N  Booking          (PROTECT)   cannot delete a booked vehicle
Vehicle 1—N  Maintenance      (CASCADE)   service history dies with the vehicle
Vehicle 1—N  Violation        (PROTECT)   cannot delete a vehicle with violations
Driver  1—N  Booking          (PROTECT)   cannot delete a booked driver
Driver  1—N  Violation        (SET_NULL)  violation outlives driver
Booking 1—N  Violation        (SET_NULL)  violation outlives booking
```

## Deletion semantics (why PROTECT matters)

- **PROTECT** on Vehicle→Booking and Driver→Booking (B6): an entity referenced by
  an active booking cannot be deleted — enforced by the DB, proven by tests.
- **CASCADE** on maintenance/documents: history is owned by the vehicle.
- **SET_NULL** on violation→driver/booking: a violation stays even if the
  driver/booking link is gone (compliance requirement).

## Invariants this map guarantees

| Relationship | Invariant |
|---|---|
| Booking→Vehicle/Driver PROTECT | B6 |
| All tenant-scoped → Company | F1 (structural) |
| Booking→Vehicle same company | B2 |
| Violation→Vehicle PROTECT | (compliance: no orphan violations via delete) |

## Open questions (Phase 2A)
- Should violations be PROTECT on vehicle forever, or archived on
  decommissioning?
- Booking→Customer: when Customer becomes an entity, is it PROTECT or snapshot?
