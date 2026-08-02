# State Machines

Modeling entity lifecycles explicitly instead of free-form status fields.

## When to use
Any entity whose transitions are meaningful and constrained: bookings,
violations, orders, invoices. A status string with no transition rules invites
invalid states.

## Pattern
1. Enumerate states in `domain/*/state-machine.md`.
2. Enumerate legal transitions (from → to → guard).
3. Enforce in the service layer; test every transition (valid + invalid).
4. Log transitions where audit matters (see `patterns/audit/`).

## Anti-patterns
- Free-form status fields editable anywhere.
- Transitions defined implicitly by "who happens to call what".
- Multiple sources of truth for current state.

## Vroom status
A booking state machine is being formalized in `domain/booking/state-machine.md`
(Business Rules Review). Until then, status changes go through the service layer.
