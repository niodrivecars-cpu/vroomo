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

## Approved rental-day & pricing rule (F3, 2026-08-22)

Rental days are calculated from elapsed rental **duration**:

```
rental_days = ceil(elapsed_time / 24 hours)
```

For any valid positive rental duration, `rental_days >= 1`.

| Elapsed | rental_days |
|---|---|
| 1h   | 1 |
| 23h  | 1 |
| 24h  | 1 |
| 25h  | 2 |
| 48h  | 2 |
| 49h  | 3 |
| 72h  | 3 |

Booking timestamps are interpreted using the booking's **resolved local
timezone** (`settings.TIME_ZONE`, e.g. `Africa/Casablanca`). This determines how
the timestamps are read — it does **not** mean rental_days is computed by
subtracting calendar dates. The authoritative calculation is elapsed duration
divided by 24 hours and **rounded UP** (`ceil`). No DST-specific exceptions are
introduced (none are required).

### Authoritative total

```
total_amount = vehicle.daily_rate × rental_days
```

`total_amount` is a **server-authoritative stored snapshot**. The client-submitted
`total_amount` is ignored. No discounts, seasonal pricing, extras, taxes,
currency conversion, deposit calculation, or manual pricing overrides are
applied. `deposit` is unchanged (see F7).

Implementation: `fleet/pricing.py` → `rental_days(pickup, expected_return)` and
`calculate_booking_total(vehicle, pickup, expected_return)`.


## Test matrix
| Case | Status |
|---|---|
| Decimal money, non-negative | exists (form validation) |
| total_due = fine + surcharge | exists (property) |
| Rate computation from daily_rate | open (not modeled) |
| Deposit/rounding/currency rules | open (Phase 2) |

See `knowledge/business/pricing-patterns.md` for general pricing discipline.
