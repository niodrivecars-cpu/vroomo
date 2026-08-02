# Pricing Knowledge — Best Practices

- **Use Decimal for money**, with explicit precision at the DB and model layers.
- **One canonical pricing engine** per domain, not scattered arithmetic in views.
- **Round once**, at a defined boundary.
- **Validate amounts at the form/model boundary** (negative, absurd values).
- **Test pricing rules as reference tests** (red/green), per the Business Rules
  Review phase.
