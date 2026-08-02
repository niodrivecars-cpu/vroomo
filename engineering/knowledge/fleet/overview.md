# Fleet Knowledge

What we know about the fleet domain in Vroom — vehicle fleet management with
tenant-isolated companies.

## Model shape
- **Company** — the tenant. Every user, vehicle, driver, booking, and document
  belongs to a company; isolation is structural.
- **Vehicle** — owned by a company, has documents (licenses/registration).
- **Driver** — belongs to a company, linked to bookings.
- **Booking** — a vehicle reserved for a time window by a driver.
- **Violation** — recorded against a driver/vehicle.
- **AuditLog** — records security-relevant actions with company + session key.

## Key invariants (detailed in `domain/`)
- One vehicle per overlapping booking window (exclusivity).
- Tenant scoping on every query.
- Private, expiring document downloads.

## Known quirks
- Booking day-bands are per-VU in load tests to keep conflict space distinct.
- Same-vehicle concurrency is load-tested: exactly one success per window.
