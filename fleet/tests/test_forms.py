from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from ..forms import (
    BookingForm,
    DriverForm,
    MaintenanceForm,
    VehicleDocumentForm,
    VehicleForm,
    ViolationForm,
)
from ..models import Company, Driver, Vehicle


class VehicleFormTest(TestCase):
    def test_valid_vehicle_form(self):
        data = {
            'license_plate': '9999-ج-9',
            'make': 'Test',
            'model': 'Car',
            'year': 2023,
            'status': 'available',
            'current_km': 0,
            'daily_rate': '350.00',
            'notes': '',
        }
        form = VehicleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_vehicle_form_missing_required(self):
        form = VehicleForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('license_plate', form.errors)
        self.assertIn('make', form.errors)
        self.assertIn('daily_rate', form.errors)


class DriverFormTest(TestCase):
    def test_valid_driver_form(self):
        data = {
            'first_name': 'سعيد',
            'last_name': 'المغربي',
            'cin': 'CD789012',
            'phone': '0622222222',
            'license_number': 'L-002',
            'license_expiry': '2027-12-31',
            'is_active': True,
        }
        form = DriverForm(data=data)
        self.assertTrue(form.is_valid())

    def test_driver_form_missing_cin(self):
        data = {
            'first_name': 'سعيد',
            'last_name': 'المغربي',
            'phone': '0622222222',
            'license_number': 'L-002',
            'license_expiry': '2027-12-31',
        }
        form = DriverForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cin', form.errors)


class BookingFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Booking Form Co')
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

    def test_valid_booking_form(self):
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'خالد',
            'customer_phone': '0633333333',
            'pickup_date': timezone.now() + timedelta(days=1),
            'expected_return': timezone.now() + timedelta(days=4),
            'total_amount': '900.00',
            'deposit': '300.00',
            'notes': '',
        }
        form = BookingForm(data=data)
        self.assertTrue(form.is_valid())

    def test_booking_form_pickup_after_return(self):
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'خالد',
            'customer_phone': '0633333333',
            'pickup_date': timezone.now() + timedelta(days=5),
            'expected_return': timezone.now() + timedelta(days=2),
            'total_amount': '900.00',
            'deposit': '300.00',
        }
        form = BookingForm(data=data)
        self.assertTrue(form.is_valid())


class MaintenanceFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Maint Form Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_valid_maintenance_form(self):
        data = {
            'date': '2026-06-01',
            'km_at_service': 50000,
            'type': 'vidange',
            'cost': '500.00',
            'next_service_km': 60000,
            'next_service_date': '2026-12-01',
            'notes': '',
        }
        form = MaintenanceForm(data=data)
        self.assertTrue(form.is_valid())


class ViolationFormTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Violation Form Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, daily_rate=Decimal('300.00'),
            company=self.company,
        )

    def test_valid_violation_form(self):
        data = {
            'vehicle': self.vehicle.pk,
            'violation_date': '2026-06-01T14:30:00',
            'violation_type': 'speeding',
            'fine_amount': '500.00',
            'majoration_amount': '0.00',
            'points_deducted': 0,
            'status': 'new',
        }
        form = ViolationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_violation_form_requires_vehicle(self):
        data = {
            'violation_date': '2026-06-01 14:30',
            'violation_type': 'speeding',
            'fine_amount': '500.00',
        }
        form = ViolationForm(data=data)
        self.assertFalse(form.is_valid())


class VehicleDocumentFormTest(TestCase):
    def test_valid_document_form(self):
        data = {
            'doc_type': 'insurance',
            'doc_number': 'INS-002',
            'expiry_date': '2027-06-01',
        }
        form = VehicleDocumentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_document_form_requires_expiry(self):
        data = {
            'doc_type': 'insurance',
            'doc_number': 'INS-002',
        }
        form = VehicleDocumentForm(data=data)
        self.assertFalse(form.is_valid())
