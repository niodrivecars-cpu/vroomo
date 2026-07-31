from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from ..forms import VehicleDocumentForm
from ..middleware import _build_csp_string
from ..models import AuditLog, Company, UserProfile, Vehicle, VehicleDocument
from ..validators import (
    MAX_UPLOAD_SIZE,
    DocumentUploadTo,
    validate_file_extension,
    validate_file_size,
    validate_mime_type,
)


class ValidatorsTest(TestCase):
    def test_valid_extension_pdf(self):
        f = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content')
        validate_file_extension(f)

    def test_valid_extension_png(self):
        f = SimpleUploadedFile('test.png', b'fake png')
        validate_file_extension(f)

    def test_valid_extension_jpg(self):
        f = SimpleUploadedFile('test.jpg', b'fake jpg')
        validate_file_extension(f)

    def test_valid_extension_jpeg(self):
        f = SimpleUploadedFile('test.jpeg', b'fake jpeg')
        validate_file_extension(f)

    def test_invalid_extension_exe(self):
        f = SimpleUploadedFile('malware.exe', b'fake exe')
        with self.assertRaises(ValidationError):
            validate_file_extension(f)

    def test_invalid_extension_js(self):
        f = SimpleUploadedFile('script.js', b'alert(1)')
        with self.assertRaises(ValidationError):
            validate_file_extension(f)

    def test_valid_size_under_limit(self):
        f = SimpleUploadedFile('test.pdf', b'a' * (MAX_UPLOAD_SIZE - 1))
        validate_file_size(f)

    def test_invalid_size_over_limit(self):
        f = SimpleUploadedFile('test.pdf', b'a' * (MAX_UPLOAD_SIZE + 1))
        with self.assertRaises(ValidationError):
            validate_file_size(f)

    def test_invalid_size_exact_limit(self):
        f = SimpleUploadedFile('test.pdf', b'a' * MAX_UPLOAD_SIZE)
        validate_file_size(f)

    def test_mime_type_pdf(self):
        f = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        validate_mime_type(f)

    @patch('magic.from_buffer', return_value='image/png')
    def test_mime_type_png(self, mock_magic):
        png_header = b'\x89PNG\r\n\x1a\n'
        f = SimpleUploadedFile('test.png', png_header, content_type='image/png')
        validate_mime_type(f)

    def test_mime_type_jpeg(self):
        jpeg_header = b'\xff\xd8\xff\xe0'
        f = SimpleUploadedFile('test.jpg', jpeg_header, content_type='image/jpeg')
        validate_mime_type(f)

    def test_invalid_mime_type_text(self):
        f = SimpleUploadedFile('test.txt', b'plain text', content_type='text/plain')
        with self.assertRaises(ValidationError):
            validate_mime_type(f)

    def test_invalid_mime_type_html(self):
        f = SimpleUploadedFile('test.html', b'<html></html>', content_type='text/html')
        with self.assertRaises(ValidationError):
            validate_mime_type(f)

    def test_document_upload_to_generates_uuid_filename(self):
        upload_to = DocumentUploadTo()
        path = upload_to(None, 'original_name.pdf')
        self.assertTrue(path.startswith('documents/'))
        self.assertTrue(path.endswith('.pdf'))
        self.assertNotIn('original_name', path)

    def test_document_upload_to_preserves_extension_case(self):
        upload_to = DocumentUploadTo()
        path = upload_to(None, 'Scan.PNG')
        self.assertTrue(path.endswith('.png'))


class VehicleDocumentFileValidationTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Sec Test Co')
        self.vehicle = Vehicle.objects.create(
            license_plate='TEST-1', make='Test', model='Car',
            year=2023, daily_rate=Decimal('100.00'),
            company=self.company,
        )

    def test_valid_pdf_upload(self):
        pdf_file = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        form = VehicleDocumentForm(data={
            'doc_type': 'insurance', 'doc_number': 'INS-001',
            'expiry_date': '2028-01-01',
        }, files={'file': pdf_file})
        self.assertTrue(form.is_valid(), msg=str(form.errors))

    def test_rejects_exe_upload(self):
        exe_file = SimpleUploadedFile('virus.exe', b'MZ fake exe', content_type='application/x-msdownload')
        form = VehicleDocumentForm(data={
            'doc_type': 'insurance', 'doc_number': 'INS-001',
            'expiry_date': '2028-01-01',
        }, files={'file': exe_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_rejects_oversized_file(self):
        big_file = SimpleUploadedFile('big.pdf', b'%PDF-1.4' + b'a' * (MAX_UPLOAD_SIZE + 1), content_type='application/pdf')
        form = VehicleDocumentForm(data={
            'doc_type': 'insurance', 'doc_number': 'INS-001',
            'expiry_date': '2028-01-01',
        }, files={'file': big_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_no_file_is_optional(self):
        form = VehicleDocumentForm(data={
            'doc_type': 'insurance', 'doc_number': 'INS-001',
            'expiry_date': '2028-01-01',
        })
        self.assertTrue(form.is_valid())

    def test_rejects_non_pdf_content_disguised_as_pdf(self):
        fake_pdf = SimpleUploadedFile('test.pdf', b'<html>malicious</html>', content_type='application/pdf')
        form = VehicleDocumentForm(data={
            'doc_type': 'insurance', 'doc_number': 'INS-001',
            'expiry_date': '2028-01-01',
        }, files={'file': fake_pdf})
        self.assertFalse(form.is_valid())


class AuditLogModelTest(TestCase):
    def _create_vehicle(self):
        company = Company.objects.create(name='Audit Vehicle Co')
        return Vehicle.objects.create(
            license_plate='AUDIT-1', make='Test', model='X',
            year=2023, daily_rate=Decimal('200.00'), company=company,
        )

    def test_audit_log_creation(self):
        user = User.objects.create_user(username='tester', password='pass')
        log = AuditLog.objects.create(
            user=user, username='tester', ip_address='192.168.1.1',
            user_agent='TestAgent/1.0', action='LOGIN',
            change_summary='تم تسجيل الدخول',
        )
        self.assertEqual(log.action, 'LOGIN')
        self.assertEqual(log.username, 'tester')
        self.assertEqual(str(log.ip_address), '192.168.1.1')

    def test_audit_log_str(self):
        log = AuditLog.objects.create(
            username='admin', action='LOGIN',
            change_summary='login test',
        )
        self.assertIn('Login', str(log))
        self.assertIn('admin', str(log))

    def test_audit_log_default_ordering(self):
        AuditLog.objects.create(username='a', action='LOGIN', change_summary='first')
        AuditLog.objects.create(username='b', action='LOGOUT', change_summary='second')
        logs = AuditLog.objects.all()
        self.assertEqual(logs[0].username, 'b')
        self.assertEqual(logs[1].username, 'a')

    def test_audit_log_without_user(self):
        log = AuditLog.objects.create(
            username='anonymous', action='LOGIN_FAILED',
            ip_address='10.0.0.1',
            change_summary='فشل تسجيل دخول',
        )
        self.assertIsNone(log.user)

    def test_audit_log_counts(self):
        AuditLog.objects.create(username='a', action='LOGIN', change_summary='x')
        AuditLog.objects.create(username='b', action='LOGOUT', change_summary='y')
        self.assertEqual(AuditLog.objects.count(), 2)

    def test_audit_log_with_obj_ref(self):
        vehicle = self._create_vehicle()
        log = AuditLog.objects.create(
            username='admin', action='CREATE',
            content_type=vehicle._meta.label,
            object_id=str(vehicle.pk),
            object_repr=str(vehicle),
            change_summary='إضافة مركبة',
        )
        self.assertEqual(log.content_type, 'fleet.Vehicle')
        self.assertEqual(log.object_id, str(vehicle.pk))


class AuditLogLoginSignalsTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Signal Test Co')
        self.user = User.objects.create_user(username='signaluser', password='pass1234')
        UserProfile.objects.create(user=self.user, company=self.company)

    def test_login_creates_audit_log(self):
        self.client.login(username='signaluser', password='pass1234')
        self.assertTrue(AuditLog.objects.filter(action='LOGIN', username='signaluser').exists())

    def test_logout_creates_audit_log(self):
        self.client.login(username='signaluser', password='pass1234')
        self.client.logout()
        self.assertTrue(AuditLog.objects.filter(action='LOGOUT', username='signaluser').exists())

    def test_failed_login_creates_audit_log(self):
        self.client.login(username='signaluser', password='wrongpassword')
        self.assertTrue(AuditLog.objects.filter(action='LOGIN_FAILED').exists())


class PaginationViewTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Pagination Test Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client.login(username='admin', password='pass1234')

    def test_vehicle_list_pagination_context(self):
        from django.urls import reverse
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertIn('page_obj', response.context)

    def test_violation_list_pagination_context(self):
        from django.urls import reverse
        response = self.client.get(reverse('fleet:violation_list'))
        self.assertIn('page_obj', response.context)

    def test_violation_list_total_fines(self):
        from django.urls import reverse
        v = Vehicle.objects.create(
            license_plate='TOTAL-1', make='Test', model='X',
            year=2023, daily_rate=Decimal('100.00'),
            company=self.company,
        )
        from ..models import Violation
        Violation.objects.create(vehicle=v, violation_date='2026-01-01T12:00:00Z',
                                  violation_type='speeding', fine_amount=Decimal('500.00'),
                                  company=self.company)
        Violation.objects.create(vehicle=v, violation_date='2026-01-02T12:00:00Z',
                                  violation_type='parking', fine_amount=Decimal('300.00'),
                                  majoration_amount=Decimal('50.00'),
                                  company=self.company)
        response = self.client.get(reverse('fleet:violation_list'))
        self.assertEqual(response.context['total_fines'], Decimal('850.00'))


class AuditLogViewIntegrationTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Audit Integ Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='AUDIT-1', make='Test', model='X',
            year=2023, daily_rate=Decimal('100.00'),
            company=self.company,
        )

    def test_vehicle_create_logs_audit(self):
        from django.urls import reverse
        self.client.post(reverse('fleet:vehicle_create'), {
            'license_plate': 'AUDIT-NEW', 'make': 'Test', 'model': 'Y',
            'year': 2024, 'status': 'available', 'current_km': 0,
            'daily_rate': '150.00', 'notes': '',
        })
        self.assertTrue(AuditLog.objects.filter(action='CREATE', content_type='fleet.Vehicle').exists())

    def test_vehicle_change_status_logs_audit(self):
        from django.urls import reverse
        self.client.post(reverse('fleet:vehicle_change_status', args=[self.vehicle.pk]), {'status': 'maintenance'})
        self.assertTrue(AuditLog.objects.filter(action='CHANGE_STATUS').exists())

    def test_vehicle_delete_through_document_logs_audit(self):
        from django.urls import reverse
        doc = VehicleDocument.objects.create(
            vehicle=self.vehicle, doc_type='insurance',
            doc_number='DEL-001', expiry_date='2028-01-01',
            company=self.company,
        )
        self.client.post(reverse('fleet:document_delete', args=[doc.pk]))
        self.assertTrue(AuditLog.objects.filter(action='DELETE').exists())


class SecurityHeadersTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', is_staff=True)
        self.company = Company.objects.create(name='Header Test Co')
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client.force_login(self.user)
        from django.urls import reverse
        self.url = reverse('fleet:dashboard')

    def test_all_required_headers_present(self):
        response = self.client.get(self.url)
        required = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Referrer-Policy',
            'Cross-Origin-Opener-Policy',
            'Cross-Origin-Resource-Policy',
            'Permissions-Policy',
        ]
        for header in required:
            with self.subTest(header=header):
                self.assertIn(header, response)

    def test_csp_header_present_when_configured(self):
        response = self.client.get(self.url)
        self.assertIn('Content-Security-Policy-Report-Only', response)
        csp = response['Content-Security-Policy-Report-Only']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self'", csp)
        self.assertIn('cdn.jsdelivr.net', csp)
        self.assertIn("frame-ancestors 'none'", csp)

    def test_csp_header_absent_when_unconfigured(self):
        with override_settings(SECURITY_CSP=None):
            # rebuild middleware by getting fresh response
            response = self.client.get(self.url)
            self.assertNotIn('Content-Security-Policy-Report-Only', response)

    def test_x_content_type_options_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_x_frame_options_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response['X-Frame-Options'], 'DENY')

    def test_referrer_policy_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')

    def test_cross_origin_opener_policy_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response['Cross-Origin-Opener-Policy'], 'same-origin')

    def test_cross_origin_resource_policy_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response['Cross-Origin-Resource-Policy'], 'same-origin')

    def test_csp_header_on_error_page(self):
        """CSP is still applied even on error responses."""
        response = self.client.get('/nonexistent/')
        self.assertIn(response.status_code, [302, 404])
        if response.status_code == 404:
            self.assertIn('Content-Security-Policy-Report-Only', response)

    def test_headers_dont_override_cache_headers(self):
        """Security headers coexist with existing response headers."""
        response = self.client.get(self.url)
        self.assertIn('Content-Type', response)
        self.assertIn('X-Content-Type-Options', response)


class CspBuildStringTest(TestCase):
    def test_build_csp_string_single_sources(self):
        policy = {'default-src': "'self'"}
        result = _build_csp_string(policy)
        self.assertEqual(result, "default-src 'self'")

    def test_build_csp_string_multi_sources(self):
        policy = {
            'script-src': ["'self'", 'https://cdn.example.com'],
            'style-src': ["'self'", "'unsafe-inline'"],
        }
        result = _build_csp_string(policy)
        self.assertIn("script-src 'self' https://cdn.example.com", result)
        self.assertIn("style-src 'self' 'unsafe-inline'", result)

    def test_build_csp_string_multiple_directives(self):
        policy = {
            'default-src': "'self'",
            'img-src': ["'self'", 'data:'],
            'frame-ancestors': "'none'",
        }
        result = _build_csp_string(policy)
        self.assertIn("default-src 'self'", result)
        self.assertIn("img-src 'self' data:", result)
        self.assertIn("frame-ancestors 'none'", result)
        self.assertEqual(result.count(';'), 2)
