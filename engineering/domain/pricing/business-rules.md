# Pricing — Business Rules

Source: Booking.total_amount, Booking.deposit, Vehicle.daily_rate,
Violation.fine_amount, Violation.majoration_amount.

## Current shape (thin)
- `daily_rate` on Vehicle is the advertised rate.
- Booking carries `total_amount` + `deposit` captured at booking time.
- Violation carries `fine_amount` + `majoration_amount` (surcharge).

## Rules today
1. Money is Decimal(10,2), non-negative (B4).
2. Violation `total_due = fine_amount + majoration_amount`.
3. No rate-card engine, no discounts, no currency handling yet.

## Business Rules Review questions
- How is `total_amount` derived from `daily_rate` × duration? (Currently manual.)
- Deposit policy (percentage, per-vehicle)?
- Surcharge rules (majoration when overdue)?
- Currency and rounding policy?
- Multi-tenant pricing (per-company rate cards)?

## Test matrix
| Case | Status |
|---|---|
| Decimal money, non-negative | exists (form validation) |
| total_due = fine + surcharge | exists (property) |
| Rate computation from daily_rate | open (not modeled) |
| Deposit/rounding/currency rules | open (Phase 2) |

See `knowledge/business/pricing-patterns.md` for general pricing discipline.
