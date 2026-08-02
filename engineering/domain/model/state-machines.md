# State Machines

The canonical state machines. Per-context files in `domain/<ctx>/` link here;
they do not redefine states. **Forbidden transitions are as important as legal
ones** — each is tested in Phase 2D.

Legend: `→` legal transition · `✗` forbidden transition · `(derived)` computed
from data, never stored.

---

## Vehicle — physical status

`fleet/models.py` (`Vehicle.STATUS_CHOICES`): `available`, `rented`,
`maintenance`, `out_of_service`.

```text
available ──→ rented ──→ available      (return)
available ──→ maintenance ──→ available (service complete)
     │            │
     ▼            ▼
out_of_service    out_of_service        (any → out_of_service; manual restore)
```

**Legal:**
| From | To | Guard |
|---|---|---|
| available | rented | rental starts (pickup of a confirmed booking) |
| rented | available | vehicle returned, no active booking |
| available | maintenance | maintenance record created |
| maintenance | available | service complete |
| * | out_of_service | manual decision |
| out_of_service | available | manual restore |

**Forbidden (✗):**
- `rented` → `maintenance` while a rental is active.
- `available` → `rented` with no confirmed booking (renting is driven by a
  booking, never a raw status flip).
- Any transition that **contradicts an active booking window** (status must stay
  consistent with bookings — see policy P15).

**Important:** there is **no `reserved` status**. A vehicle is *effectively*
reserved while a `confirmed` booking exists. Reserved is derived, never stored.

---

## Booking — lifecycle

`fleet/models.py` (`Booking.STATUS_CHOICES`): `confirmed`, `rented`, `returned`,
`cancelled`, `late` (derived).

```text
confirmed ──→ rented ──→ returned        (terminal)
confirmed ──→ cancelled                  (terminal)
rented ──(time passes)→ late (derived, not stored)
```

**Legal:**
| From | To | Guard |
|---|---|---|
| confirmed | rented | pickup performed (pickup_km set) |
| confirmed | cancelled | before rental starts |
| rented | returned | actual_return + return_km set |
| rented | late | now > expected_return (derived) |
| returned | — | terminal |
| cancelled | — | terminal |

**Forbidden (✗):**
- `cancelled` → anything (terminal).
- `returned` → anything (terminal).
- `confirmed` → `returned` (skips rented).
- `rented` → `confirmed` (backwards).
- `returned` → `late`.
- Raw status edits outside the service layer.

**Derived:** `late` = `rented` AND now > `expected_return`; `days_late` from the
same condition.

**Open (Phase 2A):** cancel-after-start policy (implied no today).

---

## Violation — lifecycle

`fleet/models.py` (`Violation.STATUS_CHOICES`): `new`, `driver_designated`,
`paid`, `disputed`, `overdue` (derived).

```text
new ──→ driver_designated ──→ paid          (terminal)
new / driver_designated ──→ disputed
* ──(past deadline, unpaid)→ overdue (derived, not stored)
```

**Legal:**
| From | To | Guard |
|---|---|---|
| new | driver_designated | driver assigned |
| driver_designated | paid | payment recorded |
| new | disputed | dispute opened |
| driver_designated | disputed | dispute opened |
| any (not paid) | overdue | now > payment_deadline (derived) |

**Forbidden (✗):**
- `paid` → anything (terminal).
- `disputed` → `paid` (must resolve dispute first — current model doesn't
  special-case this; Phase 2A question).
- `overdue` is never stored as a status.

**Derived:** `total_due = fine_amount + majoration_amount`; `is_overdue` when
past deadline and not `paid`.

---

## VehicleDocument — expiry lifecycle

Derived only (`days_until_expiry`, `is_expired`, `is_expiring_soon`). No status
field.

```text
valid ──(t→t+30d)→ expiring_soon ──(t→expiry)→ expired    (all derived)
```

**Rules:** states are computed from `expiry_date`, never stored. Revoking
downloads (`revoke_download_links`) bumps `download_token_version` — a version
event, not a state.

**Open (Phase 2A):** does an `expired` document block rental? (policy P16).

---

## Company / Driver / Maintenance

- **Company:** `active` / `inactive` via `is_active` flag. No transition machine
  yet; Phase 2A decision on deactivation semantics (block rentals?).
- **Driver:** `active` / `inactive` flag; license-validity is a policy (P4), not
  a state.
- **Maintenance:** no status; `is_due` is derived. Whether a due vehicle is
  blocked from booking is policy P1.

## Cross-cutting rule
Derived states are **computed, never stored**, so they cannot drift. Transitions
go through the service layer; raw status edits are disallowed
(`patterns/django-service-layer/`).
