# Pricing Patterns

General rules for pricing logic (applies to any product with money).

## Principles
- **Decimal everywhere** — money is Decimal, never float.
- **One pricing engine** per domain; no arithmetic scattered in views.
- **Round once** at a defined boundary.
- **Currency is explicit** — a `currency` field and a conversion policy when
  multi-currency.
- **Discounts** — apply to the pre-tax amount; never compound rounding.

## Turning rules into tests
Every pricing rule becomes a reference test: "given this rate card + window →
this price". These live in `domain/<domain>/test-matrix.md` and the suite.

## Status
Vroom currently captures a per-booking `amount`; a full pricing engine
(rate cards, discounts) is a Business Rules Review item
(`knowledge/pricing/`, `domain/pricing/`).
