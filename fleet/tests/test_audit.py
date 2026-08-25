from datetime import timedelta

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from ..audit import log_audit
from ..models import (
    AuditLog,
    Booking,
    Company,
    Driver,
    Maintenance,
    UserProfile,
    Vehicle,
    VehicleDocument,
    Violation,
)


class AuditCompanyIdTest(TestCase):
    """Regression: every tenant-scoped action must record its owning company.

    OBS-1 — log_audit previously derived company_id only from obj.vehicle,
    so Vehicle/Driver/Maintenance/Violation audit entries had company_id=None
    and could not be filtered per tenant.
    """

    def setUp(self):
        self.company = Company.objects.create(name='Audit Co')
        self.staff = User.objects.create_user(
            username='staff', password='pass1234', is_staff=True,
        )
        UserProfile.objects.create(user=self.staff, company=self.company)
        self.vehicle = Vehicle.objects.create(
            license_plate='AUD-1', make='M', model='X', year=2023,
            daily_rate='100.00', company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='A', last_name='B', cin='AUD123', phone='0500000000',
            license_number='L-AUD', license_expiry='2028-01-01', company=self.company,
        )
        self.booking = Booking.objects.create(
            vehicle=self.vehicle, driver=self.driver, customer_name='C',
            customer_phone='0500000000', pickup_date=timezone.now(),
            expected_return=timezone.now() + timedelta(days=3),
            total_amount='300.00', company=self.company,
        )
        self.doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance', doc_number='AUD-D',
            expiry_date='2028-01-01', company=self.company,
        )
        self.maintenance = Maintenance.objects.create(
            vehicle=self.vehicle, type='Oil', date=timezone.now(),
            km_at_service=10, cost='50.00', company=self.company,
        )
        self.violation = Violation.objects.create(
            vehicle=self.vehicle, violation_date=timezone.now(),
            violation_type='speeding', fine_amount='100.00', company=self.company,
        )

    def _request(self):
        factory = RequestFactory()
        request = factory.post('/')
        request.user = self.staff
        request.session = type('S', (), {'session_key': 'key'})()
        request.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'test'}
        return request

    def _assert_company_recorded(self, obj):
        before = AuditLog.objects.count()
        log_audit(self._request(), 'CREATE', obj)
        self.assertEqual(AuditLog.objects.count(), before + 1)
        entry = AuditLog.objects.latest('created_at')
        self.assertEqual(entry.company_id, self.company.pk)

    def test_vehicle_audit_records_company(self):
        self._assert_company_recorded(self.vehicle)

    def test_driver_audit_records_company(self):
        self._assert_company_recorded(self.driver)

    def test_maintenance_audit_records_company(self):
        self._assert_company_recorded(self.maintenance)

    def test_violation_audit_records_company(self):
        self._assert_company_recorded(self.violation)

    def test_booking_audit_records_company(self):
        self._assert_company_recorded(self.booking)

    def test_vehicle_document_audit_records_company(self):
        self._assert_company_recorded(self.doc)

    def test_vehicle_create_view_audit_records_company(self):
        self.client.login(username='staff', password='pass1234')
        self.client.post(reverse('fleet:vehicle_create'), {
            'license_plate': 'AUD-2', 'make': 'M', 'model': 'X',
            'year': 2024, 'daily_rate': '150', 'current_km': '0',
            'status': 'available',
        })
        entry = AuditLog.objects.filter(action='CREATE').latest('created_at')
        self.assertEqual(entry.company_id, self.company.pk)
