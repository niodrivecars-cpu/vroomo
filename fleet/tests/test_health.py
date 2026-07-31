import json
from unittest.mock import patch

from django.db.utils import OperationalError
from django.test import Client, TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('health')

    def test_health_ok_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['checks']['database'], 'ok')
        self.assertEqual(data['checks']['cache'], 'ok')

    def test_health_response_is_not_cached(self):
        response = self.client.get(self.url)
        self.assertEqual(response['Cache-Control'], 'no-store')

    def test_health_database_failure_returns_503(self):
        with patch('fleet.views.connection.ensure_connection', side_effect=OperationalError('db down')):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['checks']['database'], 'error')

    def test_health_cache_failure_returns_503(self):
        with patch('fleet.views.cache.set', side_effect=RuntimeError('cache down')):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['checks']['cache'], 'error')
