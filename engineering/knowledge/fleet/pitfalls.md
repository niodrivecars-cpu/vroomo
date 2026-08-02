# Fleet Knowledge — Pitfalls

- **Forgetting the company filter on a query.** The classic IDOR vector: a
  vehicle/driver/booking lookup that doesn't scope by company leaks across
  tenants.
- **Treating vehicle/driver as global.** Everything in this domain is
  company-owned; global uniqueness assumptions are wrong.
- **Document files treated as static assets.** They are private, signed,
  expiring (ADR 0002).
- **Booking exclusivity assumed safe without a concurrency test.**
- **Violations without a linked driver/booking** — the flow auto-links a driver
  from the active booking; ignoring that path drops audit context.
