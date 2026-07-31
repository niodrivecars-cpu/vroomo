from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
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


class TenantIsolationBase(TestCase):
    """Two companies with separate data. User A belongs to Company A."""

    def setUp(self):
        # Company A
        self.company_a = Company.objects.create(name='Company A')
        self.user_a = User.objects.create_user(username='staff_a', password='pass', is_staff=True)
        UserProfile.objects.create(user=self.user_a, company=self.company_a)
        self.vehicle_a = Vehicle.objects.create(
            license_plate='A-001', make='Alpha', model='X',
            year=2023, daily_rate=Decimal(100), company=self.company_a,
        )
        self.driver_a = Driver.objects.create(
            first_name='Ali', last_name='A', cin='AAA111', phone='0500000001',
            license_number='L-A', license_expiry='2028-01-01', company=self.company_a,
        )
        self.booking_a = Booking.objects.create(
            vehicle=self.vehicle_a, driver=self.driver_a,
            customer_name='Cust A', customer_phone='0500000010',
            pickup_date=timezone.now(), expected_return=timezone.now() + timedelta(days=2),
            total_amount=Decimal(200), company=self.company_a,
        )
        self.doc_a = VehicleDocument.objects.create(
            vehicle=self.vehicle_a, doc_type='insurance',
            doc_number='DOC-A', expiry_date='2028-01-01', company=self.company_a,
        )
        self.maintenance_a = Maintenance.objects.create(
            vehicle=self.vehicle_a, type='repair', date=timezone.now(),
            km_at_service=10000, cost=Decimal(150), company=self.company_a,
        )
        self.violation_a = Violation.objects.create(
            vehicle=self.vehicle_a, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal(300), company=self.company_a,
        )

        # Company B (user_a must NOT access this data)
        self.company_b = Company.objects.create(name='Company B')
        self.vehicle_b = Vehicle.objects.create(
            license_plate='B-001', make='Beta', model='Y',
            year=2024, daily_rate=Decimal(200), company=self.company_b,
        )
        self.driver_b = Driver.objects.create(
            first_name='Bob', last_name='B', cin='BBB222', phone='0500000002',
            license_number='L-B', license_expiry='2029-01-01', company=self.company_b,
        )
        self.booking_b = Booking.objects.create(
            vehicle=self.vehicle_b, driver=self.driver_b,
            customer_name='Cust B', customer_phone='0500000020',
            pickup_date=timezone.now(), expected_return=timezone.now() + timedelta(days=3),
            total_amount=Decimal(600), company=self.company_b,
        )
        self.doc_b = VehicleDocument.objects.create(
            vehicle=self.vehicle_b, doc_type='carte_grise',
            doc_number='DOC-B', expiry_date='2029-01-01', company=self.company_b,
        )
        self.maintenance_b = Maintenance.objects.create(
            vehicle=self.vehicle_b, type='oil', date=timezone.now(),
            km_at_service=5000, cost=Decimal(80), company=self.company_b,
        )
        self.violation_b = Violation.objects.create(
            vehicle=self.vehicle_b, violation_date=timezone.now(),
            violation_type='parking', fine_amount=Decimal(100), company=self.company_b,
        )

        self.client = Client()
        self.client.login(username='staff_a', password='pass')


class TenantIsolationReadTests(TenantIsolationBase):
    """User A must not see Company B's objects."""

    def test_vehicle_list_excludes_other_company(self):
        r = self.client.get(reverse('fleet:vehicle_list'))
        self.assertContains(r, 'A-001')
        self.assertNotContains(r, 'B-001')

    def test_vehicle_detail_not_found_for_other_company(self):
        r = self.client.get(reverse('fleet:vehicle_detail', args=[self.vehicle_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_driver_list_excludes_other_company(self):
        r = self.client.get(reverse('fleet:driver_list'))
        self.assertContains(r, 'Ali')
        self.assertNotContains(r, 'Bob')

    def test_driver_detail_not_found_for_other_company(self):
        r = self.client.get(reverse('fleet:driver_detail', args=[self.driver_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_booking_list_excludes_other_company(self):
        r = self.client.get(reverse('fleet:booking_list'))
        self.assertContains(r, 'Cust A')
        self.assertNotContains(r, 'Cust B')

    def test_booking_detail_not_found_for_other_company(self):
        r = self.client.get(reverse('fleet:booking_detail', args=[self.booking_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_maintenance_list_excludes_other_company(self):
        r = self.client.get(reverse('fleet:maintenance_list'))
        self.assertContains(r, 'repair')
        self.assertNotContains(r, 'oil')

    def test_violation_list_excludes_other_company(self):
        r = self.client.get(reverse('fleet:violation_list'))
        self.assertContains(r, 'A-001')
        self.assertNotContains(r, 'B-001')


class TenantIsolationWriteTests(TenantIsolationBase):
    """User A must not be able to edit Company B's objects."""

    def test_vehicle_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:vehicle_edit', args=[self.vehicle_b.pk]), {
            'license_plate': 'B-001', 'make': 'Beta', 'model': 'Z',
            'year': 2024, 'daily_rate': '200', 'status': 'available',
        })
        self.assertEqual(r.status_code, 404)

    def test_driver_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:driver_edit', args=[self.driver_b.pk]), {
            'first_name': 'Bob', 'last_name': 'B', 'cin': 'BBB222',
            'phone': '0500000002', 'license_number': 'L-B', 'license_expiry': '2029-01-01',
        })
        self.assertEqual(r.status_code, 404)

    def test_booking_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:booking_edit', args=[self.booking_b.pk]), {
            'vehicle': self.vehicle_b.pk, 'driver': self.driver_b.pk,
            'customer_name': 'Cust B', 'customer_phone': '0500000020',
            'pickup_date': timezone.now() + timedelta(days=1),
            'expected_return': timezone.now() + timedelta(days=4),
            'total_amount': '600',
        })
        self.assertEqual(r.status_code, 404)

    def test_booking_pickup_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:booking_pickup', args=[self.booking_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_booking_return_not_found_for_other_company(self):
        self.booking_b.status = 'rented'
        self.booking_b.save()
        r = self.client.post(reverse('fleet:booking_return', args=[self.booking_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_vehicle_change_status_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:vehicle_change_status', args=[self.vehicle_b.pk]), {'status': 'maintenance'})
        self.assertEqual(r.status_code, 404)

    def test_document_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:document_edit', args=[self.doc_b.pk]), {
            'doc_type': 'insurance', 'doc_number': 'DOC-B', 'expiry_date': '2029-01-01',
        })
        self.assertEqual(r.status_code, 404)

    def test_document_delete_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:document_delete', args=[self.doc_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_maintenance_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:maintenance_edit', args=[self.maintenance_b.pk]), {
            'date': '2026-01-01', 'km_at_service': 5000,
            'type': 'oil', 'cost': '80',
        })
        self.assertEqual(r.status_code, 404)

    def test_maintenance_delete_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:maintenance_delete', args=[self.maintenance_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_violation_edit_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:violation_edit', args=[self.violation_b.pk]), {
            'vehicle': self.vehicle_b.pk, 'violation_date': '2026-01-01T12:00',
            'violation_type': 'parking', 'fine_amount': '100',
        })
        self.assertEqual(r.status_code, 404)

    def test_violation_delete_not_found_for_other_company(self):
        r = self.client.post(reverse('fleet:violation_delete', args=[self.violation_b.pk]))
        self.assertEqual(r.status_code, 404)


class TenantIsolationCreateTests(TenantIsolationBase):
    """New objects created by User A must be owned by Company A."""

    def test_vehicle_created_with_user_company(self):
        self.client.post(reverse('fleet:vehicle_create'), {
            'license_plate': 'NEW-A', 'make': 'Test', 'model': 'T',
            'year': 2024, 'status': 'available', 'current_km': 0,
            'daily_rate': '100', 'notes': '',
        })
        vehicle = Vehicle.objects.get(license_plate='NEW-A')
        self.assertEqual(vehicle.company, self.company_a)

    def test_driver_created_with_user_company(self):
        self.client.post(reverse('fleet:driver_create'), {
            'first_name': 'New', 'last_name': 'Driver',
            'cin': 'NEW123', 'phone': '0500000099',
            'license_number': 'L-NEW', 'license_expiry': '2028-01-01',
        })
        driver = Driver.objects.get(cin='NEW123')
        self.assertEqual(driver.company, self.company_a)

    def test_booking_created_with_user_company(self):
        self.client.post(reverse('fleet:booking_create'), {
            'vehicle': self.vehicle_a.pk, 'driver': self.driver_a.pk,
            'customer_name': 'New Cust', 'customer_phone': '0500000098',
            'pickup_date': timezone.now() + timedelta(days=10),
            'expected_return': timezone.now() + timedelta(days=13),
            'total_amount': '300', 'deposit': '100', 'notes': '',
        })
        booking = Booking.objects.get(customer_name='New Cust')
        self.assertEqual(booking.company, self.company_a)

    def test_violation_created_with_user_company(self):
        now_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        self.client.post(reverse('fleet:violation_create'), {
            'vehicle': self.vehicle_a.pk,
            'violation_date': now_str,
            'violation_type': 'speeding', 'fine_amount': '200',
        })
        violation = Violation.objects.filter(vehicle=self.vehicle_a).order_by('-id').first()
        self.assertIsNotNone(violation)
        self.assertEqual(violation.company, self.company_a)


class TenantIsolationFormTests(TenantIsolationBase):
    """Forms must only show objects from the user's company."""

    def test_booking_form_only_shows_own_company_vehicles(self):
        r = self.client.get(reverse('fleet:booking_create'))
        self.assertContains(r, 'A-001')
        self.assertNotContains(r, 'B-001')

    def test_violation_form_only_shows_own_company_vehicles(self):
        r = self.client.get(reverse('fleet:violation_create'))
        self.assertContains(r, 'A-001')
        self.assertNotContains(r, 'B-001')

    def test_maintenance_form_only_shows_own_company_vehicles(self):
        r = self.client.get(reverse('fleet:maintenance_create', args=[self.vehicle_a.pk]))
        self.assertEqual(r.status_code, 200)

    def test_maintenance_form_not_found_for_other_company_vehicle(self):
        r = self.client.get(reverse('fleet:maintenance_create', args=[self.vehicle_b.pk]))
        self.assertEqual(r.status_code, 404)

    def test_document_form_only_shows_own_company_vehicles(self):
        r = self.client.get(reverse('fleet:document_create', args=[self.vehicle_a.pk]))
        self.assertEqual(r.status_code, 200)

    def test_document_form_not_found_for_other_company_vehicle(self):
        r = self.client.get(reverse('fleet:document_create', args=[self.vehicle_b.pk]))
        self.assertEqual(r.status_code, 404)
