"""F8 — BookingAdmin.save_model must recompute total_amount.

Verifies the Django admin edit path applies the same server-authoritative
pricing as BookingForm (F3): editing dates/vehicle recomputes total_amount
and any admin-submitted total_amount is ignored. deposit is untouched.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from ..admin import BookingAdmin
from ..models import Booking, Company, Driver, Vehicle


class BookingAdminSaveModelTest(TestCase):
    """Direct save_model override test (no full admin form juggling)."""

    def setUp(self):
        self.company = Company.objects.create(name='Admin Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='A-1', make='M', model='X', year=2020,
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
            pickup_date=start, expected_return=start + timedelta(hours=24 * 3),
            total_amount=Decimal('900.00'), company=self.company,
        )
        self.admin = BookingAdmin(Booking, admin.site)
        self.request = RequestFactory().post('/')

    def test_save_model_recomputes_on_date_change(self):
        # Edit to a 5-day window; stale total 900 must not survive.
        new_start = timezone.now() + timedelta(days=5)
        self.booking.pickup_date = new_start
        self.booking.expected_return = new_start + timedelta(hours=24 * 5)
        self.booking.total_amount = Decimal(0)  # attacker/ stale value
        self.admin.save_model(self.request, self.booking, form=None, change=True)
        self.booking.refresh_from_db()
        # 300 * 5 days = 1500, never the stale 900 or submitted 0.
        self.assertEqual(self.booking.total_amount, Decimal('1500.00'))

    def test_save_model_recomputes_on_vehicle_rate_change(self):
        # Switch to a cheaper vehicle; total reflects new rate.
        cheap = Vehicle.objects.create(
            license_plate='A-2', make='M', model='X', year=2020,
            daily_rate=Decimal('100.00'), status='available',
            company=self.company,
        )
        self.booking.vehicle = cheap
        self.booking.total_amount = Decimal('999999.99')  # ignored
        self.admin.save_model(self.request, self.booking, form=None, change=True)
        self.booking.refresh_from_db()
        # 100 * 3 days = 300
        self.assertEqual(self.booking.total_amount, Decimal('300.00'))

    def test_save_model_preserves_deposit(self):
        self.booking.deposit = Decimal('250.00')
        self.booking.total_amount = Decimal(0)
        new_start = timezone.now() + timedelta(days=7)
        self.booking.pickup_date = new_start
        self.booking.expected_return = new_start + timedelta(hours=24 * 2)
        self.admin.save_model(self.request, self.booking, form=None, change=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.deposit, Decimal('250.00'))  # untouched
        self.assertEqual(self.booking.total_amount, Decimal('600.00'))  # 300 * 2


class BookingAdminChangeViewTest(TestCase):
    """End-to-end: real admin change POST must recompute total_amount."""

    def setUp(self):
        self.company = Company.objects.create(name='AdminView Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='V-1', make='M', model='X', year=2020,
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
            pickup_date=start, expected_return=start + timedelta(hours=24 * 3),
            total_amount=Decimal('900.00'), deposit=Decimal('50.00'),
            company=self.company,
        )
        self.superuser = self._create_superuser()
        self.client.login(username='su', password='su1234')

    def _create_superuser(self):
        from django.contrib.auth import get_user_model
        U = get_user_model()
        return U.objects.create_superuser('su', 'su@example.com', 'su1234')

    def test_admin_change_recomputes_total_and_ignores_submitted_value(self):
        new_start = timezone.now() + timedelta(days=9)
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'K',
            'customer_phone': '063',
            'pickup_date_0': new_start.strftime('%Y-%m-%d'),
            'pickup_date_1': new_start.strftime('%H:%M:%S'),
            'expected_return_0': (new_start + timedelta(hours=24 * 5)).strftime('%Y-%m-%d'),
            'expected_return_1': (new_start + timedelta(hours=24 * 5)).strftime('%H:%M:%S'),
            'pickup_km': '0',
            'total_amount': '0',       # attacker tries to force 0
            'deposit': '50.00',
            'notes': '',
            'status': 'confirmed',
        }
        url = reverse('admin:fleet_booking_change', args=[self.booking.pk])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302, response.content[:500])
        self.booking.refresh_from_db()
        # 300 * 5 days = 1500, not the stale 900 nor submitted 0.
        self.assertEqual(self.booking.total_amount, Decimal('1500.00'))
        self.assertEqual(self.booking.deposit, Decimal('50.00'))
