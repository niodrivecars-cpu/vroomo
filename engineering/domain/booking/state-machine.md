# Booking — State Machine

Canonical source: `domain/model/state-machines.md`. This file holds the
booking-specific guards and open questions; states are not redefined here.

Source: `fleet/models.py` (Booking.STATUS_CHOICES).

## States
`confirmed` → `rented` → `returned` (normal flow)
`cancelled` (terminal)
`late` (derived state, not stored: `status == 'rented'` and now > expected_return)

## Legal transitions

| From | To | Guard |
|---|---|---|
| confirmed | rented | pickup performed (pickup_km set) |
| confirmed | cancelled | before rental starts |
| rented | returned | actual_return + return_km set |
| rented | late (derived) | time passes expected_return |
| returned | — | terminal |
| cancelled | — | terminal |

## Rules
- `cancelled` and `returned` are terminal — no further transition.
- `late` is computed, never stored; it must remain consistent with
  `status == 'rented'`.
- Transitions happen through the service/view layer (see
  `patterns/django-service-layer/`), not by raw status edits.

## To formalize (Business Rules Review)
- Is "cancel after rental started" allowed? (currently implied no).
- Are partial/extension windows a state? (no — keep as data, not state).
