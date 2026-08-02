# Pricing Knowledge

What we know about pricing in Vroom. (Currently a thin area — bookings carry an
amount field; full pricing rules are a Business Rules Review item.)

## Current shape
- Booking has an `amount` field (e.g. `120.00` in load tests).
- No discount/rate-card engine yet; pricing is captured per booking.

## Direction
Pricing patterns (rate cards, currency, discounts, rounding) live in
`knowledge/business/pricing-patterns.md`. A full pricing domain model with
reference tests is expected during the Business Rules Review phase
(`domain/pricing/`).
