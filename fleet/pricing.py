"""Domain-level pricing for Vroom bookings.

Single source of truth for the server-authoritative booking total.

Rule (engineering/domain/pricing/business-rules.md, F3):
    rental_days = ceil(elapsed_time / 24 hours)      # >= 1 for any valid rental
    total_amount = vehicle.daily_rate * rental_days

The client-submitted `total_amount` is NEVER trusted; it is always
recomputed here from the vehicle's authoritative `daily_rate` and the
rental window. This module intentionally contains no discounts, seasonal
pricing, extras, taxes, currency conversion, deposit calculation, or manual
overrides.
"""

from __future__ import annotations

import math
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

# A rental of zero or negative duration is invalid (enforced by form
# validation, B3), but guard the math so a bad call can never yield a
# non-positive day count.
_MIN_RENTAL_DAYS = 1


def _as_aware(value):
    """Ensure a datetime is timezone-aware in the active zone.

    Django stores naive-in-DB as UTC and re-interprets via USE_TZ; both
    pickup and expected_return come from the same active timezone, so the
    elapsed delta is correct regardless of which zone that is.
    """
    if timezone.is_naive(value):
        return timezone.make_aware(value, timezone.get_current_timezone())
    return value


def rental_days(pickup, expected_return):
    """Return ceil(elapsed rental duration / 24h), minimum 1.

    Elapsed duration (not calendar-date subtraction) is the authoritative
    measure. Both timestamps are interpreted in the resolved local timezone.
    """
    start = _as_aware(pickup)
    end = _as_aware(expected_return)
    elapsed = end - start
    if elapsed <= timedelta(0):
        # Invalid window; caller must have validated. Return the floor of 1
        # rather than raising, so the form/validation layer owns the error.
        return _MIN_RENTAL_DAYS
    total_seconds = elapsed.total_seconds()
    days = math.ceil(total_seconds / (24 * 3600))
    days = max(days, _MIN_RENTAL_DAYS)
    return days


def calculate_booking_total(vehicle, pickup, expected_return):
    """Server-authoritative total: daily_rate * rental_days.

    `vehicle.daily_rate` is the only authoritative pricing input. Any
    client-supplied total_amount is ignored by the caller.
    """
    rate = vehicle.daily_rate or Decimal(0)
    days = rental_days(pickup, expected_return)
    return (rate * Decimal(days)).quantize(Decimal("0.01"))
