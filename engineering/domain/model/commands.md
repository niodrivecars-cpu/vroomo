# Commands

The canonical catalog of allowed actions. Each command has: who can run it, its
guard, and where it lands today. A command with no guard is a policy gap.

Legend: ✅ implemented · ⚠️ implemented, guard unverified · 🔲 aspirational.

## Rental

| Command | Actor | Guard | Status |
|---|---|---|---|
| CreateBooking | staff | B1 exclusivity, B2 tenant, B3 window, B4 money | ✅ (B3–B4 tests needed) |
| CancelBooking | staff | before rental starts | ⚠️ |
| StartRental (pickup) | staff | confirmed booking; sets pickup_km | ⚠️ |
| ReturnVehicle | staff | rented booking; sets actual_return + return_km | ⚠️ |
| AssignDriverToBooking | staff | same company (B2) | ✅ |

## Fleet

| Command | Actor | Guard | Status |
|---|---|---|---|
| CreateVehicle | staff | unique plate (F6); company scope | ✅ |
| SetVehicleStatus | staff | cannot contradict active booking (P15) | ⚠️ |
| CreateMaintenanceRecord | staff | vehicle exists; sets is_due inputs | ✅ |
| UploadDocument | staff | tenant scope; file validators | ✅ |
| RevokeDownloadLinks | staff/owner | document ownership | ✅ |
| CreateViolation | staff | vehicle company scope; auto-link to active booking driver | ✅ |

## Admin / platform

| Command | Actor | Guard | Status |
|---|---|---|---|
| CreateCompany | platform | unique name | ✅ |
| DeactivateCompany | platform | deactivation semantics (Phase 2A) | 🔲 |
| ManageRateLimits | platform | — | ⚠️ (config) |

## Not yet available

| Command | Needed by | Status |
|---|---|---|
| MarkViolationPaid | violation lifecycle | 🔲 (no payment flow) |
| DisputeViolation | violation lifecycle | 🔲 |
| CreateInvoice / RecordPayment | invoicing (not modeled) | 🔲 |
| RegisterCustomer | customer entity (not modeled) | 🔲 |

## Rules
1. Commands mutate state **only** through the service layer
   (`patterns/django-service-layer/`), never raw status edits.
2. Every command's guard maps to an invariant (B1…, F1…) or a policy (P1…).
3. Aspirational commands are added here **before** their views/URLs are built.
