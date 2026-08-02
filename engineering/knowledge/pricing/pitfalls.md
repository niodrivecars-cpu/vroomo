# Pricing Knowledge — Pitfalls

- **Floating-point money.** Amounts must be stored as decimal, not float.
- **Currency mixing without explicit handling.** A multi-currency product needs a
  currency field and a conversion policy.
- **Rounding at the wrong layer.** Round once at display/persistence boundary,
  not mid-computation.
- **Discounts applied after rounding** or compounded incorrectly.
