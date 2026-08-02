# Fleet — State Machines

Canonical source: `domain/model/state-machines.md`. This file holds the
fleet-specific guards and notes; states are not redefined here.

Two lifecycle state machines exist in the fleet domain.

## Vehicle status
`available` → `rented` → `available` (via return)
`available` → `maintenance` → `available`
`*` → `out_of_service` (terminal until manually restored)

Derived, not stored: whether a vehicle is actually rented follows from active
bookings (`rented`/`late`), so vehicle.status and bookings must stay consistent —
an area for reference tests (Business Rules Review).

## Violation status
`new` → `driver_designated` → `paid`
`new`/`driver_designated` → `disputed`
`*` → `overdue` (derived: past payment_deadline and not paid)

`overdue` is computed (`is_overdue`), never stored. `paid` is terminal.
`majoration_amount` (surcharge) is meaningful once overdue — currently just data.

## Rules
- Derived states (vehicle in-use, violation overdue) are computed from data and
  must never be stored, so they can't drift.
- Transitions go through the service layer; raw status edits are disallowed.
