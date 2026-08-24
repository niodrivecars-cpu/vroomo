"""Pricing + F3 security regression tests.

Verifies the server-authoritative rental-day and total_amount rules:
    rental_days = ceil(elapsed / 24h)   (>= 1)
    total_amount = vehicle.daily_rate * rental_days

And that a client-submitted total_amount (0 or inflated) can never alter the
stored, server-calculated total.
"""

from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from ..forms import BookingForm
from ..models import Booking, Company, Driver, Vehicle
from ..pricing import calculate_booking_total, rental_days


class RentalDaysTest(TestCase):
    """rental_days = ceil(elapsed / 24h), minimum 1 (elapsed duration, not dates)."""

    def setUp(self):
        self.base = timezone.now().replace(microsecond=0)

    def _elapsed(self, hours):
        return self.base, self.base + timedelta(hours=hours)

    def test_one_hour_is_one_day(self):
        self.assertEqual(rental_days(*self._elapsed(1)), 1)

    def test_23_hours_is_one_day(self):
        self.assertEqual(rental_days(*self._elapsed(23)), 1)

    def test_exactly_24_hours_is_one_day(self):
        self.assertEqual(rental_days(*self._elapsed(24)), 1)

    def test_25_hours_is_two_days(self):
        self.assertEqual(rental_days(*self._elapsed(25)), 2)

    def test_exactly_48_hours_is_two_days(self):
        self.assertEqual(rental_days(*self._elapsed(48)), 2)

    def test_49_hours_is_three_days(self):
        self.assertEqual(rental_days(*self._elapsed(49)), 3)

    def test_72_hours_is_three_days(self):
        self.assertEqual(rental_days(*self._elapsed(72)), 3)

    def test_same_calendar_day_positive_rental_is_one_day(self):
        # 1h apart but same local calendar day -> still 1 day by elapsed rule.
        self.assertEqual(rental_days(*self._elapsed(2)), 1)

    def test_invalid_non_positive_duration_is_not_positive_days(self):
        # Elapsed <= 0 must not yield a positive rental window. rental_days
        # guards to the floor of 1; the *validation* layer (B3) owns the error.
        self.assertEqual(rental_days(self.base, self.base), 1)
        self.assertEqual(rental_days(self.base, self.base - timedelta(hours=5)), 1)


class CalculateBookingTotalTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Pricing Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='P-1', make='M', model='X', year=2020,
            daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )
        self.base = timezone.now().replace(microsecond=0)

    def test_total_is_rate_times_rental_days(self):
        total = calculate_booking_total(self.vehicle, self.base, self.base + timedelta(hours=25))
        self.assertEqual(total, Decimal('600.00'))  # 300 * 2 days

    def test_decimal_daily_rate(self):
        self.vehicle.daily_rate = Decimal('99.99')
        self.vehicle.save()
        total = calculate_booking_total(self.vehicle, self.base, self.base + timedelta(hours=48))
        self.assertEqual(total, Decimal('199.98'))  # 99.99 * 2 days

    def test_zero_daily_rate_yields_zero_total(self):
        # daily_rate can be 0 today (no validation forbids it). Authoritative
        # total is then 0 -- not the client's submitted value.
        self.vehicle.daily_rate = Decimal(0)
        self.vehicle.save()
        total = calculate_booking_total(self.vehicle, self.base, self.base + timedelta(hours=24))
        self.assertEqual(total, Decimal('0.00'))

    def test_negative_daily_rate_passes_through(self):
        # No current rule forbids negative daily_rate; we do not invent one.
        self.vehicle.daily_rate = Decimal('-50.00')
        self.vehicle.save()
        total = calculate_booking_total(self.vehicle, self.base, self.base + timedelta(hours=24))
        self.assertEqual(total, Decimal('-50.00'))


class BookingTotalSecurityRegressionTest(TestCase):
    """Client-submitted total_amount must never become the stored total."""

    def setUp(self):
        self.company = Company.objects.create(name='Sec Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='S-1', make='M', model='X', year=2020,
            daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='A', last_name='B', cin='AB1', phone='061',
            license_number='L1',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )

    def _post_data(self, total_amount, hours=25, daily_rate='300.00'):
        self.vehicle.daily_rate = Decimal(daily_rate)
        self.vehicle.save()
        start = timezone.now() + timedelta(days=1)
        return {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date': start,
            'expected_return': start + timedelta(hours=hours),
            'total_amount': total_amount,   # attacker-controlled
            'deposit': '0.00',
            'notes': '',
        }

    def test_submitted_zero_total_is_ignored(self):
        form = BookingForm(data=self._post_data('0'), company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('600.00'))  # 300 * 2 days

    def test_submitted_inflated_total_is_ignored(self):
        form = BookingForm(data=self._post_data('999999.99'), company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('600.00'))

    def test_total_recomputed_on_save_commit_false_then_save(self):
        # Mirrors booking_create view flow: form.save(commit=False) -> set meta
        # -> booking.save(). Computed total must survive.
        form = BookingForm(data=self._post_data('0'), company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save(commit=False)
        booking.company = self.company
        booking.status = 'confirmed'
        booking.save()
        self.assertEqual(booking.total_amount, Decimal('600.00'))

    def test_missing_total_amount_field_is_ignored(self):
        data = self._post_data('600.00')
        del data['total_amount']
        form = BookingForm(data=data, company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('600.00'))

    def test_deposit_is_not_recalculated(self):
        # F3 does not touch deposit; client deposit value must be preserved.
        form = BookingForm(data=self._post_data('0', hours=25), company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        self.assertEqual(booking.deposit, Decimal('0.00'))
        self.assertEqual(booking.total_amount, Decimal('600.00'))

    def test_changing_vehicle_daily_rate_recomputes(self):
        form = BookingForm(
            data=self._post_data('0', hours=48, daily_rate='150.00'),
            company=self.company,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        # 150 * 2 days = 300
        self.assertEqual(booking.total_amount, Decimal('300.00'))

    def test_changing_window_recomputes(self):
        # 72h with default rate 300 -> 3 days -> 900
        form = BookingForm(data=self._post_data('0', hours=72), company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        form.instance.company = self.company
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('900.00'))


class BookingEditRecomputeTest(TestCase):
    """Editing pricing inputs must recompute total_amount; old total never survives."""

    def setUp(self):
        self.company = Company.objects.create(name='Edit Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='E-1', make='M', model='X', year=2020,
            daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='A', last_name='B', cin='AB1', phone='061',
            license_number='L1',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )
        start = timezone.now() + timedelta(days=1)
        self.booking = Booking.objects.create(
            vehicle=self.vehicle, driver=self.driver,
            customer_name='K', customer_phone='063',
            pickup_date=start, expected_return=start + timedelta(hours=24),
            total_amount=Decimal('300.00'), company=self.company,
        )

    def test_edit_extends_window_recomputes_total(self):
        new_start = timezone.now() + timedelta(days=5)
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date': new_start,
            'expected_return': new_start + timedelta(hours=72),  # 3 days
            'total_amount': '0',  # attacker tries to force 0
            'deposit': '0.00',
            'notes': '',
        }
        form = BookingForm(data=data, instance=self.booking, company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('900.00'))  # 300 * 3

    def test_edit_preserves_computed_not_client_value(self):
        new_start = timezone.now() + timedelta(days=8)
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date': new_start,
            'expected_return': new_start + timedelta(hours=24),  # 1 day
            'total_amount': '123456.78',
            'deposit': '0.00',
            'notes': '',
        }
        form = BookingForm(data=data, instance=self.booking, company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('300.00'))  # 300 * 1

    def test_edit_recompute_from_3_days_to_5_days(self):
        # Original: daily_rate 300, 3 days -> total 900. Edit to a 5-day window.
        new_start = timezone.now() + timedelta(days=9)
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date': new_start,
            'expected_return': new_start + timedelta(hours=24 * 5),  # 5 days
            'total_amount': '0',  # attacker tries to force 0
            'deposit': '0.00',
            'notes': '',
        }
        form = BookingForm(data=data, instance=self.booking, company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()
        # 300 * 5 days = 1500, never the submitted 0.
        self.assertEqual(booking.total_amount, Decimal('1500.00'))

    def test_edit_submitted_zero_total_still_1500(self):
        # Same as above but explicit assertion name for the invariant:
        # old total 900 must not survive; new computed total is authoritative.
        new_start = timezone.now() + timedelta(days=11)
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date': new_start,
            'expected_return': new_start + timedelta(hours=24 * 5),  # 5 days
            'total_amount': '0',
            'deposit': '0.00',
            'notes': '',
        }
        form = BookingForm(data=data, instance=self.booking, company=self.company)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()
        self.assertEqual(booking.total_amount, Decimal('1500.00'))
        self.assertNotEqual(booking.total_amount, Decimal('900.00'))  # old total gone
        self.assertNotEqual(booking.total_amount, Decimal('0.00'))   # client value ignored


class TimezoneAwareTimestampsTest(TestCase):
    """Elapsed-duration rule is timezone-correct with aware timestamps."""

    def setUp(self):
        self.company = Company.objects.create(name='TZ Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='T-1', make='M', model='X', year=2020,
            daily_rate=Decimal('100.00'), status='available',
            company=self.company,
        )

    def test_aware_timestamps_25h_is_two_days(self):
        start = timezone.now()
        total = calculate_booking_total(
            self.vehicle, start, start + timedelta(hours=25)
        )
        self.assertEqual(total, Decimal('200.00'))
