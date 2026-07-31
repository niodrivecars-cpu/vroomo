from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import cache
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


class AuthTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Auth Test Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('fleet:dashboard'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("fleet:dashboard")}')

    def test_vehicle_list_requires_login(self):
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertEqual(response.status_code, 302)

    def test_vehicle_create_requires_login(self):
        response = self.client.get(reverse('fleet:vehicle_create'))
        self.assertEqual(response.status_code, 302)

    def test_vehicle_change_status_requires_login(self):
        response = self.client.post(reverse('fleet:vehicle_change_status', args=[self.vehicle.pk]), {'status': 'maintenance'})
        self.assertEqual(response.status_code, 302)

    def test_dashboard_works_when_logged_in(self):
        self.client.login(username='admin', password='pass1234')
        response = self.client.get(reverse('fleet:dashboard'))
        self.assertEqual(response.status_code, 200)


class VehicleViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Vehicle View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, current_km=50000, daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )

    def test_vehicle_list(self):
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1234-أ-1')

    def test_vehicle_create(self):
        response = self.client.post(reverse('fleet:vehicle_create'), {
            'license_plate': '9999-ج-9',
            'make': 'Dacia',
            'model': 'Sandero',
            'year': 2023,
            'status': 'available',
            'current_km': 0,
            'daily_rate': '280.00',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_list'))
        self.assertEqual(Vehicle.objects.count(), 2)

    def test_vehicle_detail(self):
        response = self.client.get(reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Renault')

    def test_vehicle_edit(self):
        response = self.client.post(reverse('fleet:vehicle_edit', args=[self.vehicle.pk]), {
            'license_plate': '1234-أ-1',
            'make': 'Renault',
            'model': 'Megane',
            'year': 2021,
            'status': 'available',
            'current_km': 50000,
            'daily_rate': '350.00',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model, 'Megane')

    def test_vehicle_change_status(self):
        response = self.client.post(reverse('fleet:vehicle_change_status', args=[self.vehicle.pk]), {'status': 'maintenance'})
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'maintenance')

    def test_vehicle_change_status_rented_to_available_blocked(self):
        self.vehicle.status = 'rented'
        self.vehicle.save()
        self.client.post(reverse('fleet:vehicle_change_status', args=[self.vehicle.pk]), {'status': 'available'})
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'rented')


class BookingViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Booking View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, current_km=50000, daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='أحمد', last_name='العربي',
            cin='AB123456', phone='0612345678',
            license_number='L-001',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )
        self.booking = Booking.objects.create(
            vehicle=self.vehicle, driver=self.driver,
            customer_name='محمد', customer_phone='0611111111',
            pickup_date=timezone.now() + timedelta(days=1),
            expected_return=timezone.now() + timedelta(days=4),
            total_amount=Decimal('900.00'), deposit=Decimal('300.00'),
            status='confirmed', company=self.company,
        )

    def test_booking_list(self):
        response = self.client.get(reverse('fleet:booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'محمد')

    def test_booking_create(self):
        response = self.client.post(reverse('fleet:booking_create'), {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'خالد',
            'customer_phone': '0633333333',
            'pickup_date': timezone.now() + timedelta(days=10),
            'expected_return': timezone.now() + timedelta(days=13),
            'total_amount': '900.00',
            'deposit': '300.00',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:booking_list'))
        self.assertEqual(Booking.objects.count(), 2)

    def test_booking_create_pickup_after_return_rejected(self):
        response = self.client.post(reverse('fleet:booking_create'), {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'خالد',
            'customer_phone': '0633333333',
            'pickup_date': timezone.now() + timedelta(days=10),
            'expected_return': timezone.now() + timedelta(days=8),
            'total_amount': '900.00',
            'deposit': '300.00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Return date must be after pickup date')

    def test_booking_create_maintenance_vehicle_rejected(self):
        self.vehicle.status = 'maintenance'
        self.vehicle.save()
        response = self.client.post(reverse('fleet:booking_create'), {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'خالد',
            'customer_phone': '0633333333',
            'pickup_date': timezone.now() + timedelta(days=10),
            'expected_return': timezone.now() + timedelta(days=13),
            'total_amount': '900.00',
            'deposit': '300.00',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This vehicle is not available for booking (maintenance or out of service)')

    def test_booking_detail(self):
        response = self.client.get(reverse('fleet:booking_detail', args=[self.booking.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'محمد')

    def test_booking_edit(self):
        response = self.client.post(reverse('fleet:booking_edit', args=[self.booking.pk]), {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'محمد المغير',
            'customer_phone': '0611111111',
            'pickup_date': timezone.now() + timedelta(days=1),
            'expected_return': timezone.now() + timedelta(days=4),
            'total_amount': '900.00',
            'deposit': '300.00',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:booking_detail', args=[self.booking.pk]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.customer_name, 'محمد المغير')

    def test_booking_pickup(self):
        response = self.client.post(reverse('fleet:booking_pickup', args=[self.booking.pk]))
        self.assertRedirects(response, reverse('fleet:booking_detail', args=[self.booking.pk]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'rented')
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'rented')

    def test_booking_return(self):
        self.booking.status = 'rented'
        self.booking.pickup_km = 50000
        self.booking.save()
        self.vehicle.status = 'rented'
        self.vehicle.save()
        response = self.client.post(reverse('fleet:booking_return', args=[self.booking.pk]))
        self.assertRedirects(response, reverse('fleet:booking_detail', args=[self.booking.pk]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'returned')
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, 'available')

    def test_booking_pickup_rejected_wrong_status(self):
        self.booking.status = 'returned'
        self.booking.save()
        self.client.post(reverse('fleet:booking_pickup', args=[self.booking.pk]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'returned')


class DriverViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Driver View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')

    def test_driver_list_empty(self):
        response = self.client.get(reverse('fleet:driver_list'))
        self.assertEqual(response.status_code, 200)

    def test_driver_create(self):
        response = self.client.post(reverse('fleet:driver_create'), {
            'first_name': 'سعيد',
            'last_name': 'المغربي',
            'cin': 'CD789012',
            'phone': '0622222222',
            'license_number': 'L-002',
            'license_expiry': '2027-12-31',
            'is_active': True,
        })
        self.assertRedirects(response, reverse('fleet:driver_list'))
        self.assertEqual(Driver.objects.count(), 1)

    def test_driver_detail(self):
        driver = Driver.objects.create(
            first_name='سعيد', last_name='المغربي',
            cin='CD789012', phone='0622222222',
            license_number='L-002',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )
        response = self.client.get(reverse('fleet:driver_detail', args=[driver.pk]))
        self.assertEqual(response.status_code, 200)

    def test_driver_edit(self):
        driver = Driver.objects.create(
            first_name='سعيد', last_name='المغربي',
            cin='CD789012', phone='0622222222',
            license_number='L-002',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )
        response = self.client.post(reverse('fleet:driver_edit', args=[driver.pk]), {
            'first_name': 'سعيد المغير',
            'last_name': 'المغربي',
            'cin': 'CD789012',
            'phone': '0622222222',
            'license_number': 'L-002',
            'license_expiry': '2027-12-31',
            'is_active': True,
        })
        self.assertRedirects(response, reverse('fleet:driver_list'))
        driver.refresh_from_db()
        self.assertEqual(driver.first_name, 'سعيد المغير')


class DocumentViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.company = Company.objects.create(name='Doc View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_document_create(self):
        response = self.client.post(reverse('fleet:document_create', args=[self.vehicle.pk]), {
            'doc_type': 'insurance',
            'doc_number': 'INS-001',
            'expiry_date': '2027-06-01',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.assertEqual(VehicleDocument.objects.count(), 1)

    def test_document_edit(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date='2027-06-01',
            company=self.company,
        )
        response = self.client.post(reverse('fleet:document_edit', args=[doc.pk]), {
            'doc_type': 'carte_grise',
            'doc_number': 'CG-001',
            'expiry_date': '2028-01-01',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        doc.refresh_from_db()
        self.assertEqual(doc.doc_type, 'carte_grise')

    def test_document_delete(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date='2027-06-01',
            company=self.company,
        )
        response = self.client.post(reverse('fleet:document_delete', args=[doc.pk]))
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.assertEqual(VehicleDocument.objects.count(), 0)


class MaintenanceViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Maint View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, current_km=50000, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_maintenance_list(self):
        response = self.client.get(reverse('fleet:maintenance_list'))
        self.assertEqual(response.status_code, 200)

    def test_maintenance_create(self):
        response = self.client.post(reverse('fleet:maintenance_create', args=[self.vehicle.pk]), {
            'date': '2026-06-01',
            'km_at_service': 50000,
            'type': 'vidange',
            'cost': '500.00',
            'next_service_km': 60000,
            'next_service_date': '',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))

    def test_maintenance_edit(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date='2026-06-01',
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            company=self.company,
        )
        response = self.client.post(reverse('fleet:maintenance_edit', args=[maint.pk]), {
            'date': '2026-06-01',
            'km_at_service': 50000,
            'type': 'freinage',
            'cost': '800.00',
            'next_service_km': '',
            'next_service_date': '',
            'notes': '',
        })
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        maint.refresh_from_db()
        self.assertEqual(maint.type, 'freinage')

    def test_maintenance_delete(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date='2026-06-01',
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            company=self.company,
        )
        response = self.client.post(reverse('fleet:maintenance_delete', args=[maint.pk]))
        self.assertRedirects(response, reverse('fleet:vehicle_detail', args=[self.vehicle.pk]))
        self.assertEqual(Maintenance.objects.count(), 0)


class ViolationViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Violation View Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'), status='available',
            company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='أحمد', last_name='العربي',
            cin='AB123456', phone='0612345678',
            license_number='L-001',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )
        self.booking = Booking.objects.create(
            vehicle=self.vehicle, driver=self.driver,
            customer_name='محمد', customer_phone='0611111111',
            pickup_date=timezone.now() - timedelta(days=2),
            expected_return=timezone.now() + timedelta(days=2),
            total_amount=Decimal('900.00'), deposit=Decimal('300.00'),
            status='rented', company=self.company,
        )

    def test_violation_list(self):
        response = self.client.get(reverse('fleet:violation_list'))
        self.assertEqual(response.status_code, 200)

    def test_violation_create(self):
        now_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('fleet:violation_create'), {
            'vehicle': self.vehicle.pk,
            'violation_date': now_str,
            'violation_type': 'speeding',
            'fine_amount': '500.00',
            'majoration_amount': '0.00',
        })
        self.assertRedirects(response, reverse('fleet:violation_list'))
        self.assertEqual(Violation.objects.count(), 1)

    def test_violation_create_auto_links_driver_from_active_booking(self):
        now_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        self.client.post(reverse('fleet:violation_create'), {
            'vehicle': self.vehicle.pk,
            'violation_date': now_str,
            'violation_type': 'speeding',
            'fine_amount': '500.00',
            'majoration_amount': '0.00',
        })
        violation = Violation.objects.first()
        self.assertIsNotNone(violation)
        self.assertEqual(violation.driver, self.driver)
        self.assertEqual(violation.booking, self.booking)
        self.assertEqual(violation.status, 'driver_designated')

    def test_violation_create_without_driver_if_no_booking(self):
        self.booking.status = 'returned'
        self.booking.actual_return = timezone.now()
        self.booking.save()
        now_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        self.client.post(reverse('fleet:violation_create'), {
            'vehicle': self.vehicle.pk,
            'violation_date': now_str,
            'violation_type': 'speeding',
            'fine_amount': '500.00',
            'majoration_amount': '0.00',
        })
        violation = Violation.objects.first()
        self.assertIsNotNone(violation)
        self.assertIsNone(violation.driver)

    def test_violation_edit(self):
        violation = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            company=self.company,
        )
        now_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('fleet:violation_edit', args=[violation.pk]), {
            'vehicle': self.vehicle.pk,
            'violation_date': now_str,
            'violation_type': 'parking',
            'fine_amount': '300.00',
            'majoration_amount': '0.00',
        })
        self.assertRedirects(response, reverse('fleet:violation_list'))
        violation.refresh_from_db()
        self.assertEqual(violation.violation_type, 'parking')
        self.assertEqual(violation.fine_amount, Decimal('300.00'))

    def test_violation_delete(self):
        violation = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            company=self.company,
        )
        response = self.client.post(reverse('fleet:violation_delete', args=[violation.pk]))
        self.assertRedirects(response, reverse('fleet:violation_list'))
        self.assertEqual(Violation.objects.count(), 0)
