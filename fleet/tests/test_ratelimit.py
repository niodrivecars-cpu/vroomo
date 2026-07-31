import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from fleet.middleware import RateLimitLogMiddleware
from fleet.models import AuditLog, Company, UserProfile, Vehicle


class RateLimitMiddlewareTests(TestCase):
    def test_log_rate_limit_creates_audit(self):
        """RateLimitLogMiddleware._log_rate_limit creates audit entry."""
        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_USER_AGENT': 'test'}
        request.user = User()
        request.company = None
        from django.contrib.sessions.backends.db import SessionStore
        request.session = SessionStore()
        request.session.create()
        request.method = 'GET'
        request.path = '/test/'
        mw = RateLimitLogMiddleware(lambda r: HttpResponse('ok'))
        mw._log_rate_limit(request)
        logs = AuditLog.objects.filter(action='RATE_LIMITED')
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs[0].ip_address, '127.0.0.1')

    def test_log_rate_limit_anonymous(self):
        """Midleware handles anonymous requests without error."""
        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '10.0.0.1'}
        request.user = type('AnonUser', (), {'is_authenticated': False, 'username': ''})()
        request.company = None
        from django.contrib.sessions.backends.db import SessionStore
        request.session = SessionStore()
        request.session.create()
        request.method = 'POST'
        request.path = '/accounts/login/'
        mw = RateLimitLogMiddleware(lambda r: HttpResponse('ok'))
        mw._log_rate_limit(request)
        logs = AuditLog.objects.filter(action='RATE_LIMITED')
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs[0].username, 'ANONYMOUS')


class LoginRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.company = Company.objects.create(name='Test Co')
        UserProfile.objects.create(user=self.user, company=self.company)
        self.url = '/accounts/login/'

    def test_login_works_within_limit(self):
        """Login POST succeeds within rate limit window."""
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')

    def test_failed_login_attempts_within_limit(self):
        """Failed login attempts work without triggering rate limit within bound."""
        for i in range(5):
            data = {'username': f'nonexistent{i}', 'password': 'wrongpass'}
            response = self.client.post(self.url, data)
            self.assertNotEqual(response.status_code, 429)

    def test_login_rate_limit_triggers_429(self):
        """Exceeding IP-based login limit blocks request."""
        for i in range(5):
            self.client.post(self.url, {'username': f'user{i}', 'password': 'wrong'})
        response = self.client.post(self.url, {'username': 'another', 'password': 'wrong'})
        self.assertEqual(response.status_code, 429)

    def test_failed_login_rate_limit_creates_audit(self):
        """Rate-limited login creates RATE_LIMITED audit log entry."""
        for i in range(7):
            try:
                self.client.post(self.url, {'username': 'nogood', 'password': 'wrong'})
            except Exception:  # noqa: S110, BLE001
                pass
        logs = AuditLog.objects.filter(action='RATE_LIMITED')
        self.assertGreaterEqual(logs.count(), 1)


class UploadRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='staffuser', password='testpass123', is_staff=True)
        self.company = Company.objects.create(name='Test Co')
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client.force_login(self.user)
        self.vehicle = Vehicle.objects.create(
            company=self.company,
            license_plate='TEST123',
            make='Toyota',
            model='Corolla',
            year=2020,
            status='active',
            daily_rate=100.00,
        )
        self.url = reverse('fleet:document_create', args=[self.vehicle.pk])

    def test_upload_get_succeeds(self):
        """GET request to upload view is not rate-limited."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_upload_post_exceeds_limit(self):
        """Rate limit for upload blocks after POST threshold."""
        status = None
        for i in range(12):
            response = self.client.post(self.url, {'doc_type': 'registration', 'file': ''})
            status = response.status_code
            if status == 429:
                break
        self.assertEqual(status, 429)


class SecurityRateLimitConfigTests(TestCase):
    def test_rate_limit_config_has_required_keys(self):
        """All expected rate limit keys are defined in settings."""
        rl = settings.SECURITY_RATE_LIMITS
        required = ['login_ip', 'login_user', 'password_reset', 'upload_per_user', 'upload_per_hour', 'api']
        for key in required:
            self.assertIn(key, rl)

    def test_rate_limit_config_values_are_valid(self):
        """Rate limit values match expected pattern (number/unit)."""
        for key, value in settings.SECURITY_RATE_LIMITS.items():
            with self.subTest(key=key):
                self.assertIsNotNone(re.match(r'^\d+/(s|m|h|d)$', value))
