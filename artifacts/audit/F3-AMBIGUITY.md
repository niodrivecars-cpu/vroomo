# F3 — Blocked: rental-day billing semantics are undefined

## Status: STOPPED / AMBIGUOUS (per F3 implementation gate)

The F3 fix cannot proceed because the **rental-day counting rule is not defined
anywhere in the repository**. Implementing `total_amount = vehicle.daily_rate ×
rental_days` requires a precise definition of `rental_days`, and inventing one
would violate the explicit instruction: *"Do not invent a billing policy."*

## What I verified (locate + inspect existing rules)

### 1. Every path that creates/updates Booking
- `fleet/views.py` L192-235 `booking_create` (POST → `form.save(commit=False)`)
- `fleet/views.py` L238-273 `booking_edit` (POST → `form.save()`)
- Admin `VehicleDocument` is unrelated; Booking has no admin add/change path.
- `total_amount` is set from `form.cleaned_data` in both. No server recompute.

### 2. Every path that reads/uses total_amount
- Display only: `booking_list.html` L57, `booking_detail.html` L78 (rendered via
  `|currency`). Stored value is trusted and shown. No downstream billing yet
  (Invoice/Payment/Customer are Phase-2, not implemented).

### 3. Repo-wide search (total_amount / deposit / daily_rate)
- `total_amount`: model L208, form L28, views create/edit, templates (display),
  admin list_display, ~30 test references. No arithmetic anywhere.
- `deposit`: model L209, form L28, templates (display), tests. No arithmetic.
- `daily_rate`: model L73 (Vehicle), admin, templates (display), tests. The ONLY
  authoritative pricing input. Never multiplied by any duration anywhere.

### 4. Existing pricing/domain-service boundary
- **None exists.** No `fleet/pricing.py`, no `services.py`, no `rate` module,
  no function that multiplies `daily_rate × duration`. The pricing
  business-rules doc (`engineering/domain/pricing/business-rules.md` L14, L28)
  states: "No rate-card engine, no discounts, no currency handling yet" and
  "Rate computation from daily_rate → open (not modeled)".
- `engineering/verification/traceability/vroom-rc1.md` L39: "Rate computation
  from `daily_rate` × duration — 🔲 not modeled". L60: "G11 rate computation
  from daily_rate → pricing → Phase 2A".

### 5/6. Smallest reusable pricing boundary / no speculative engine
- Cannot create one yet: the core unit (`rental_days`) is undefined.

## The ambiguity (must be resolved before code)

The instruction lists cases to investigate: same-day, 1h, 23h, 24h, 25h, 48h,
multi-day, timezone. **None of these are defined in the spec.** Concrete
examples of the gap:

| Pickup → Return | Wall-clock Δ | Possible `rental_days` interpretations |
|---|---|---|
| 2026-08-22 10:00 → 2026-08-22 10:00 | 0h | invalid (B3: return must be after pickup) |
| 2026-08-22 10:00 → 2026-08-22 11:00 | 1h | (a) 0 days, (b) 1 day (any partial = 1) |
| 2026-08-22 10:00 → 2026-08-23 09:00 | 23h | (a) 0 days, (b) 1 day |
| 2026-08-22 10:00 → 2026-08-23 10:00 | 24h (1 day) | 1 day (agreed) |
| 2026-08-22 10:00 → 2026-08-23 11:00 | 25h | (a) 1 day, (b) 2 days (ceil) |
| 2026-08-22 10:00 → 2026-08-24 10:00 | 48h (2 days) | 2 days (agreed) |

The two standard conventions diverge materially:
- **Whole-calendar-day / ceil**: any partial day counts as a full day. 25h → 2 days.
- **Elapsed-24h-blocks**: `Δ // 24h` with truncation. 25h → 1 day.

These produce **different financial totals** (e.g. daily_rate=300 → 600 vs 900).
Choosing either without a product decision is inventing a billing policy.

### Timezone behavior
`pickup_date`/`expected_return` are naive `DateTimeField` (no `USE_TZ`-aware
tzinfo in the model). `timezone.now()` is used in tests. Whether rentals are
local-time or UTC, and DST handling, are also undefined.

## Why this is the correct stop, not a "fix"

The F3 instruction was explicit:
> "If the existing specification does not define the rule, STOP before
> implementing the calculation and report the ambiguity. Do not invent a
> billing policy."

The repository does not define `rental_days`. Therefore the authoritative
server calculation **cannot be implemented correctly yet**. Implementing
`daily_rate * (expected_return - pickup).days` (naive integer-day truncation)
would silently pick one unstated convention and bake a financial rule into
code with no product sign-off — exactly what the instruction forbids.

## Required decision (from product / domain owner)

Define `rental_days` for the matrix above. Recommended default if none given:
**ceil(elapsed hours / 24)** (car-rental industry norm: any partial day is a
full day), computed on **local calendar days** (or explicitly UTC). Once the
rule is fixed in `engineering/domain/pricing/business-rules.md`, implementation
resumes:

1. Create `fleet/pricing.py` with `rental_days(pickup, expected_return)` +
   `calculate_booking_total(vehicle, pickup, expected_return)` (smallest
   boundary — no engine).
2. In `BookingForm.save(commit=False)` / `clean_total_amount`: compute and
   assign `total_amount` from the vehicle's `daily_rate`; **ignore** client
   value. Keep the field as the stored authoritative snapshot.
3. Add regression/security tests: submitted `total_amount=0` and inflated value
   must NOT equal stored total; stored = server calc. Plus matrix cases
   (decimal rate, same-day invalid already covered by B3, min valid period,
   invalid datetime, vehicle w/o valid daily_rate, create + edit).
4. Run targeted tests → full 278 suite → security re-check → update F3 to
   RESOLVED.

## F7 — deposit exposure parity (separate, not folded into F3)

`deposit` is client-editable by the **same** `@staff_required` author as
`total_amount` (it is in `BookingForm.Meta.fields` and rendered by
`{% bootstrap_form %}` in `form.html`). There is no lower-privilege / untrusted
actor path for `deposit` beyond what already exists for `total_amount`. Per the
instruction, this is **not** an "untrusted actor" exposure distinct from F3, so
it is recorded as a separate observation, not silently merged into F3. No
deposit calc change is in scope (instruction: "Do NOT change the
meaning/calculation of deposit yet").
