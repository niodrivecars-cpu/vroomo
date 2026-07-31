from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import (
    Booking,
    Company,
    Driver,
    Maintenance,
    UserProfile,
    Vehicle,
    VehicleDocument,
    Violation,
)


class AuthorizationBase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Auth Test Co')
        self.staff_user = User.objects.create_user(
            username='staff', password='pass1234', is_staff=True,
        )
        UserProfile.objects.create(user=self.staff_user, company=self.company)
        self.regular_user = User.objects.create_user(
            username='user', password='pass1234', is_staff=False,
        )
        UserProfile.objects.create(user=self.regular_user, company=self.company)
        self.vehicle = Vehicle.objects.create(
            license_plate='AUTH-1', make='Test', model='X',
            year=2023, daily_rate=Decimal('100.00'), company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='Auth', last_name='Driver',
            cin='AUTH123456', phone='0500000000',
            license_number='LIC-AUTH-1',
            license_expiry='2028-01-01', company=self.company,
        )
        self.booking = Booking.objects.create(
            vehicle=self.vehicle, driver=self.driver,
            customer_name='Auth Customer', customer_phone='0500000000',
            pickup_date=timezone.now(),
            expected_return=timezone.now() + timezone.timedelta(days=3),
            total_amount=Decimal('300.00'), company=self.company,
        )
        self.doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='AUTH-DOC', expiry_date='2028-01-01', company=self.company,
        )
        self.maintenance = Maintenance.objects.create(
            vehicle=self.vehicle, type='Oil change',
            date=timezone.now(), km_at_service=50000,
            cost=Decimal('100.00'), company=self.company,
        )
        self.violation = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'), company=self.company,
        )

    def post(self, url, data=None):
        return self.client.post(url, data or {}, follow=False)

    def get(self, url):
        return self.client.get(url, follow=False)


class StaffRequiredOnWriteViewsTest(AuthorizationBase):

    def test_vehicle_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:vehicle_create')
        r = self.post(url, {'license_plate': 'SEC-1', 'make': 'X', 'model': 'Y', 'year': 2024, 'daily_rate': '100', 'status': 'available'})
        self.assertEqual(r.status_code, 403)

    def test_vehicle_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:vehicle_edit', args=[self.vehicle.pk])
        r = self.post(url, {'license_plate': 'SEC-2', 'make': 'X', 'model': 'Y', 'year': 2024, 'daily_rate': '100', 'status': 'available'})
        self.assertEqual(r.status_code, 403)

    def test_vehicle_change_status_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:vehicle_change_status', args=[self.vehicle.pk])
        r = self.post(url, {'status': 'maintenance'})
        self.assertEqual(r.status_code, 403)

    def test_booking_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:booking_create')
        r = self.post(url, {
            'vehicle': self.vehicle.pk, 'driver': self.driver.pk,
            'customer_name': 'Test', 'customer_phone': '0500000000',
            'pickup_date': '2026-01-01T10:00', 'expected_return': '2026-01-03T10:00',
            'total_amount': '200',
        })
        self.assertEqual(r.status_code, 403)

    def test_booking_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:booking_edit', args=[self.booking.pk])
        r = self.post(url, {
            'vehicle': self.vehicle.pk, 'driver': self.driver.pk,
            'customer_name': 'Test', 'customer_phone': '0500000000',
            'pickup_date': '2026-01-01T10:00', 'expected_return': '2026-01-03T10:00',
            'total_amount': '200',
        })
        self.assertEqual(r.status_code, 403)

    def test_booking_pickup_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:booking_pickup', args=[self.booking.pk])
        r = self.post(url)
        self.assertEqual(r.status_code, 403)

    def test_booking_return_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:booking_return', args=[self.booking.pk])
        r = self.post(url)
        self.assertEqual(r.status_code, 403)

    def test_driver_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:driver_create')
        r = self.post(url, {
            'first_name': 'Bad', 'last_name': 'Driver',
            'cin': 'BAD123', 'phone': '0500000000',
            'license_number': 'B', 'license_expiry': '2028-01-01',
        })
        self.assertEqual(r.status_code, 403)

    def test_driver_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:driver_edit', args=[self.driver.pk])
        r = self.post(url, {
            'first_name': 'Bad', 'last_name': 'Driver',
            'cin': 'BAD123', 'phone': '0500000000',
            'license_number': 'B', 'license_expiry': '2028-01-01',
        })
        self.assertEqual(r.status_code, 403)

    def test_document_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:document_create', args=[self.vehicle.pk])
        r = self.post(url, {'doc_type': 'insurance', 'doc_number': 'X', 'expiry_date': '2028-01-01'})
        self.assertEqual(r.status_code, 403)

    def test_document_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:document_edit', args=[self.doc.pk])
        r = self.post(url, {'vehicle': self.vehicle.pk, 'doc_type': 'insurance', 'doc_number': 'Y', 'expiry_date': '2028-01-01'})
        self.assertEqual(r.status_code, 403)

    def test_document_delete_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:document_delete', args=[self.doc.pk])
        r = self.post(url)
        self.assertEqual(r.status_code, 403)

    def test_maintenance_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:maintenance_create', args=[self.vehicle.pk])
        r = self.post(url, {'type': 'X', 'date': '2026-01-01', 'km_at_service': 50000, 'cost': '50'})
        self.assertEqual(r.status_code, 403)

    def test_maintenance_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:maintenance_edit', args=[self.maintenance.pk])
        r = self.post(url, {'type': 'X', 'date': '2026-01-01', 'km_at_service': 50000, 'cost': '50'})
        self.assertEqual(r.status_code, 403)

    def test_maintenance_delete_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:maintenance_delete', args=[self.maintenance.pk])
        r = self.post(url)
        self.assertEqual(r.status_code, 403)

    def test_violation_create_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:violation_create')
        r = self.post(url, {'vehicle': self.vehicle.pk, 'violation_date': '2026-01-01T12:00', 'violation_type': 'speeding', 'fine_amount': '100'})
        self.assertEqual(r.status_code, 403)

    def test_violation_edit_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:violation_edit', args=[self.violation.pk])
        r = self.post(url, {'vehicle': self.vehicle.pk, 'violation_date': '2026-01-01T12:00', 'violation_type': 'parking', 'fine_amount': '50'})
        self.assertEqual(r.status_code, 403)

    def test_violation_delete_requires_staff(self):
        self.client.login(username='user', password='pass1234')
        url = reverse('fleet:violation_delete', args=[self.violation.pk])
        r = self.post(url)
        self.assertEqual(r.status_code, 403)


class AnonymousRedirectedToLoginTest(AuthorizationBase):

    def test_vehicle_list_redirects_anonymous(self):
        r = self.get(reverse('fleet:vehicle_list'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:vehicle_list')}")

    def test_vehicle_create_redirects_anonymous(self):
        r = self.get(reverse('fleet:vehicle_create'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:vehicle_create')}")

    def test_booking_create_redirects_anonymous(self):
        r = self.get(reverse('fleet:booking_create'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:booking_create')}")

    def test_driver_list_redirects_anonymous(self):
        r = self.get(reverse('fleet:driver_list'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:driver_list')}")

    def test_maintenance_list_redirects_anonymous(self):
        r = self.get(reverse('fleet:maintenance_list'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:maintenance_list')}")

    def test_violation_list_redirects_anonymous(self):
        r = self.get(reverse('fleet:violation_list'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('fleet:violation_list')}")


class ReadOnlyAccessibleToRegularUserTest(AuthorizationBase):

    def test_dashboard_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_vehicle_list_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:vehicle_list'))
        self.assertEqual(r.status_code, 200)

    def test_vehicle_detail_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.assertEqual(r.status_code, 200)

    def test_booking_list_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:booking_list'))
        self.assertEqual(r.status_code, 200)

    def test_booking_detail_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:booking_detail', args=[self.booking.pk]))
        self.assertEqual(r.status_code, 200)

    def test_driver_list_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:driver_list'))
        self.assertEqual(r.status_code, 200)

    def test_driver_detail_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:driver_detail', args=[self.driver.pk]))
        self.assertEqual(r.status_code, 200)

    def test_maintenance_list_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:maintenance_list'))
        self.assertEqual(r.status_code, 200)

    def test_violation_list_accessible_to_regular_user(self):
        self.client.login(username='user', password='pass1234')
        r = self.get(reverse('fleet:violation_list'))
        self.assertEqual(r.status_code, 200)


class StaffWriteAccessWorksTest(AuthorizationBase):

    def test_vehicle_create_works_for_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.post(reverse('fleet:vehicle_create'), {
            'license_plate': 'STAFF-1', 'make': 'X', 'model': 'Y',
            'year': 2024, 'daily_rate': '150', 'current_km': '0',
            'status': 'available',
        })
        self.assertEqual(r.status_code, 302)

    def test_driver_create_works_for_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.post(reverse('fleet:driver_create'), {
            'first_name': 'Staff', 'last_name': 'Driver',
            'cin': 'STAFF789', 'phone': '0500000000',
            'license_number': 'L-STAFF', 'license_expiry': '2028-01-01',
        })
        self.assertEqual(r.status_code, 302)
