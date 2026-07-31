from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from ..models import (
    Booking,
    Company,
    Driver,
    Maintenance,
    Vehicle,
    VehicleDocument,
    Violation,
)


class VehicleModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Vehicle Model Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1',
            make='Renault',
            model='Clio',
            year=2020,
            status='available',
            current_km=50000,
            daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_vehicle_str(self):
        self.assertEqual(str(self.vehicle), 'Renault Clio - 1234-أ-1')

    def test_vehicle_default_status(self):
        v = Vehicle.objects.create(
            license_plate='5678-ب-2',
            make='Dacia',
            model='Logan',
            year=2021,
            daily_rate=Decimal('250.00'),
            company=self.company,
        )
        self.assertEqual(v.status, 'available')


class VehicleDocumentModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Doc Model Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_is_expired(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() - timedelta(days=1),
            company=self.company,
        )
        self.assertTrue(doc.is_expired)

    def test_is_not_expired(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() + timedelta(days=1),
            company=self.company,
        )
        self.assertFalse(doc.is_expired)

    def test_is_expiring_soon(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() + timedelta(days=15),
            company=self.company,
        )
        self.assertTrue(doc.is_expiring_soon)

    def test_not_expiring_soon(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() + timedelta(days=60),
            company=self.company,
        )
        self.assertFalse(doc.is_expiring_soon)

    def test_days_until_expiry_future(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() + timedelta(days=10),
            company=self.company,
        )
        self.assertEqual(doc.days_until_expiry, 10)

    def test_days_until_expiry_past(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='INS-001', expiry_date=timezone.now().date() - timedelta(days=5),
            company=self.company,
        )
        self.assertEqual(doc.days_until_expiry, -5)

    def test_doc_str(self):
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='carte_grise',
            doc_number='CG-001', expiry_date=timezone.now().date(),
            company=self.company,
        )
        self.assertIn('Registration card', str(doc))


class DriverModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Driver Model Co')
        self.driver = Driver.objects.create(
            first_name='أحمد', last_name='العربي',
            cin='AB123456', phone='0612345678',
            license_number='L-001',
            license_expiry=timezone.now().date() + timedelta(days=365),
            company=self.company,
        )

    def test_driver_str(self):
        self.assertEqual(str(self.driver), 'أحمد العربي')

    def test_driver_active_by_default(self):
        self.assertTrue(self.driver.is_active)


class BookingModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Booking Model Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
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
            pickup_date=timezone.now(), expected_return=timezone.now() + timedelta(days=3),
            total_amount=Decimal('900.00'), deposit=Decimal('300.00'),
            company=self.company,
        )

    def test_booking_default_status(self):
        self.assertEqual(self.booking.status, 'confirmed')

    def test_booking_str(self):
        self.assertIn('محمد', str(self.booking))

    def test_is_late_when_rented_and_past_due(self):
        self.booking.status = 'rented'
        self.booking.expected_return = timezone.now() - timedelta(hours=1)
        self.booking.save()
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.is_late)

    def test_is_not_late_when_returned(self):
        self.booking.status = 'returned'
        self.booking.actual_return = timezone.now()
        self.booking.save()
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.is_late)

    def test_days_late_zero_when_not_late(self):
        self.assertEqual(self.booking.days_late, 0)

    def test_days_late_positive_when_late(self):
        self.booking.status = 'rented'
        self.booking.expected_return = timezone.now() - timedelta(days=2)
        self.booking.save()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.days_late, 2)


class MaintenanceModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Maint Model Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, current_km=60000, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_is_due_by_km(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date=timezone.now().date(),
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            next_service_km=55000,
            company=self.company,
        )
        self.assertTrue(maint.is_due)

    def test_is_not_due_by_km(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date=timezone.now().date(),
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            next_service_km=65000,
            company=self.company,
        )
        self.assertFalse(maint.is_due)

    def test_is_due_by_date(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date=timezone.now().date(),
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            next_service_date=timezone.now().date() - timedelta(days=1),
            company=self.company,
        )
        self.assertTrue(maint.is_due)

    def test_is_not_due_by_date(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date=timezone.now().date(),
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            next_service_date=timezone.now().date() + timedelta(days=30),
            company=self.company,
        )
        self.assertFalse(maint.is_due)

    def test_maintenance_str(self):
        maint = Maintenance.objects.create(
            vehicle=self.vehicle, date=timezone.now().date(),
            km_at_service=50000, type='vidange', cost=Decimal('500.00'),
            company=self.company,
        )
        self.assertIn('vidange', str(maint))


class ViolationModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Violation Model Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_total_due_sum(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            majoration_amount=Decimal('100.00'),
            company=self.company,
        )
        self.assertEqual(v.total_due, Decimal('600.00'))

    def test_total_due_no_majoration(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='parking', fine_amount=Decimal('300.00'),
            company=self.company,
        )
        self.assertEqual(v.total_due, Decimal('300.00'))

    def test_is_overdue_when_past_deadline(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            payment_deadline=timezone.now().date() - timedelta(days=1),
            status='new',
            company=self.company,
        )
        self.assertTrue(v.is_overdue)

    def test_is_not_overdue_when_paid(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            payment_deadline=timezone.now().date() - timedelta(days=1),
            status='paid',
            company=self.company,
        )
        self.assertFalse(v.is_overdue)

    def test_is_not_overdue_future_deadline(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            payment_deadline=timezone.now().date() + timedelta(days=30),
            status='new',
            company=self.company,
        )
        self.assertFalse(v.is_overdue)

    def test_violation_str(self):
        v = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount=Decimal('500.00'),
            company=self.company,
        )
        self.assertIn('1234-أ-1', str(v))
