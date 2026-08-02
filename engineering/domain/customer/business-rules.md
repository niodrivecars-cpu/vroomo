# Customer — Business Rules

Source: `fleet/models.py` (Booking.customer_name, Booking.customer_phone).

## Current shape
Customer data is embedded on the booking (name + phone) — there is no separate
Customer entity yet.

## Rules
1. Booking requires `customer_name`; `customer_phone` captured for contact.
2. Customer data is tenant-scoped via its booking (F2).

## Open questions (Business Rules Review)
- Should customers become a first-class tenant-scoped entity (loyalty, history,
  repeat detection)?
- Phone format validation per locale?
- Is customer data PII requiring GDPR-style handling? (privacy review needed
  before pilot.)

## Test matrix
| Case | Status |
|---|---|
| Booking stores customer name/phone | exists (form validation) |
| Customer entity + dedupe | n/a (not modeled) |
