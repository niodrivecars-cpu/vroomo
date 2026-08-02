from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase, override_settings
from django.utils.module_loading import import_string
from django_ratelimit.core import is_ratelimited

from fleet.audit import log_audit
from fleet.models import AuditLog
from fleet.security import get_client_ip

TRUSTED = ['127.0.0.1']


class ClientIPResolverTests(TestCase):
    """get_client_ip resolves the real client address through trusted proxies."""

    def setUp(self):
        self.factory = RequestFactory()

    def _req(self, remote_addr, xff=None):
        headers = {'REMOTE_ADDR': remote_addr}
        if xff is not None:
            headers['HTTP_X_FORWARDED_FOR'] = xff
        return self.factory.get('/', **headers)

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=[])
    def test_no_trusted_proxy_ignores_xff(self):
        self.assertEqual(get_client_ip(self._req('203.0.113.9', '6.6.6.6')), '203.0.113.9')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_direct_connection_uses_remote_addr(self):
        self.assertEqual(get_client_ip(self._req('203.0.113.9')), '203.0.113.9')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_trusted_proxy_single_hop(self):
        self.assertEqual(get_client_ip(self._req('127.0.0.1', '203.0.113.5')), '203.0.113.5')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_spoofed_xff_from_untrusted_peer_ignored(self):
        self.assertEqual(get_client_ip(self._req('203.0.113.99', '6.6.6.6')), '203.0.113.99')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=['127.0.0.1', '10.0.0.2'])
    def test_multihop_rightmost_untrusted_wins(self):
        # Client spoofs a value, then middle proxy (10.0.0.2) and nginx (127.0.0.1)
        # append real hops with $proxy_add_x_forwarded_for.
        xff = '6.6.6.6, 203.0.113.5, 10.0.0.2'
        self.assertEqual(get_client_ip(self._req('127.0.0.1', xff)), '203.0.113.5')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_missing_xff_from_trusted_proxy_falls_back(self):
        self.assertEqual(get_client_ip(self._req('127.0.0.1')), '127.0.0.1')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=['127.0.0.1', '10.0.0.2'])
    def test_all_hops_trusted_falls_back_to_peer(self):
        self.assertEqual(get_client_ip(self._req('127.0.0.1', '10.0.0.2')), '127.0.0.1')


@override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
class RateLimitClientIPIntegrationTests(TestCase):
    """Rate limiting keys off the resolved client IP, not REMOTE_ADDR."""

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def _make(self, remote_addr, xff=None):
        headers = {'REMOTE_ADDR': remote_addr}
        if xff is not None:
            headers['HTTP_X_FORWARDED_FOR'] = xff
        return self.factory.get('/', **headers)

    def test_ip_key_buckets_by_resolved_client_ip(self):
        req_a = self._make('127.0.0.1', xff='203.0.113.5')
        req_b = self._make('127.0.0.1', xff='203.0.113.6')
        self.assertFalse(is_ratelimited(req_a, group='ip-bucket', key='ip', rate='2/m', increment=True))
        self.assertFalse(is_ratelimited(req_a, group='ip-bucket', key='ip', rate='2/m', increment=True))
        # Different resolved IP -> fresh bucket.
        self.assertFalse(is_ratelimited(req_b, group='ip-bucket', key='ip', rate='2/m', increment=True))
        self.assertTrue(is_ratelimited(req_a, group='ip-bucket', key='ip', rate='2/m', increment=True))

    def test_xff_ignored_when_no_trusted_proxy(self):
        with override_settings(X_FORWARDED_TRUSTED_PROXIES=[]):
            req_a = self._make('127.0.0.1', xff='203.0.113.5')
            req_b = self._make('127.0.0.1', xff='203.0.113.6')
            # Both map to 127.0.0.1, so they share one bucket.
            self.assertFalse(is_ratelimited(req_a, group='ip-ctl', key='ip', rate='2/m', increment=True))
            self.assertFalse(is_ratelimited(req_b, group='ip-ctl', key='ip', rate='2/m', increment=True))
            self.assertTrue(is_ratelimited(req_a, group='ip-ctl', key='ip', rate='2/m', increment=True))


class LoginRateLimitProxyTests(TestCase):
    """End-to-end: the login IP throttle is per resolved client IP."""

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.url = '/accounts/login/'

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_login_ip_limit_is_per_resolved_client_ip(self):
        # django-ratelimit uses fixed windows, so a burst can straddle a window
        # boundary. Post distinct usernames until the IP throttle trips instead
        # of asserting on an exact post count.
        blocked = None
        for i in range(20):
            response = self.client.post(
                self.url,
                {'username': f'user{i}', 'password': 'wrong'},
                HTTP_X_FORWARDED_FOR='203.0.113.5',
            )
            if response.status_code == 429:
                blocked = response
                break
        self.assertIsNotNone(blocked, 'login IP throttle never tripped')
        # Same resolved client IP stays blocked.
        response = self.client.post(
            self.url,
            {'username': 'again', 'password': 'wrong'},
            HTTP_X_FORWARDED_FOR='203.0.113.5',
        )
        self.assertEqual(response.status_code, 429)
        # Different resolved client IP is not blocked.
        response = self.client.post(
            self.url,
            {'username': 'fresh', 'password': 'wrong'},
            HTTP_X_FORWARDED_FOR='203.0.113.6',
        )
        self.assertNotEqual(response.status_code, 429)


class AuditLogClientIPTests(TestCase):
    """Audit entries record the resolved client IP."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='audituser', password='pw')

    def _request(self, remote_addr, xff=None):
        headers = {'REMOTE_ADDR': remote_addr}
        if xff is not None:
            headers['HTTP_X_FORWARDED_FOR'] = xff
        request = self.factory.get('/', **headers)
        request.user = self.user
        request.session = type('SessionStub', (), {'session_key': ''})()
        return request

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_log_audit_records_resolved_client_ip(self):
        log_audit(self._request('127.0.0.1', xff='203.0.113.7'), 'TEST_ACTION')
        log = AuditLog.objects.get(action='TEST_ACTION')
        self.assertEqual(log.ip_address, '203.0.113.7')

    @override_settings(X_FORWARDED_TRUSTED_PROXIES=TRUSTED)
    def test_log_audit_ignores_spoofed_header_from_untrusted_peer(self):
        log_audit(self._request('10.1.1.1', xff='6.6.6.6'), 'TEST_SPOOF')
        log = AuditLog.objects.get(action='TEST_SPOOF')
        self.assertEqual(log.ip_address, '10.1.1.1')


class ClientIPConfigTests(TestCase):
    def test_ratelimit_ip_meta_key_points_to_central_resolver(self):
        self.assertEqual(settings.RATELIMIT_IP_META_KEY, 'fleet.security.get_client_ip')
        self.assertIs(import_string(settings.RATELIMIT_IP_META_KEY), get_client_ip)
