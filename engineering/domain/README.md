# Domain

Business rules per bounded context. This is the product's brain — the part that
makes a fleet/rental system more than a generic Django app. Each domain carries
`business-rules.md`, `invariants.md`, `state-machine.md`, `edge-cases.md`,
`test-matrix.md`.

## Domains (Vroom)

| Domain | Scope | Source |
|---|---|---|
| `booking/` | Vehicle reservation windows, exclusivity, lifecycle | `fleet/models.py` (Booking) |
| `fleet/` | Vehicles, documents, maintenance, violations | `fleet/models.py` |
| `pricing/` | Amounts, deposits, fines (thin today) | Booking.total_amount, Violation.fine_amount |
| `vehicle/` | Vehicle lifecycle and status | `fleet/models.py` (Vehicle) |
| `driver/` | Driver identity and licensing | `fleet/models.py` (Driver) |
| `customer/` | Customer data attached to bookings | Booking.customer_* |

## Discipline

Every rule here is protected by a reference test (see `test-matrix.md` and the
Business Rules Review phase). A rule that exists only in prose is a debt.
