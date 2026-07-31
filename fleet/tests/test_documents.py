from datetime import timedelta

from django.contrib.auth.models import User
from django.core import signing
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from fleet.models import AuditLog, Company, UserProfile, Vehicle, VehicleDocument

FILE_BYTES = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n'


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage',
)
class DocumentTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Alpha')
        self.other_company = Company.objects.create(name='Beta')
        self.user = User.objects.create_user(
            username='admin', password='pass1234', is_staff=True,
        )
        UserProfile.objects.create(user=self.user, company=self.company)
        self.vehicle = Vehicle.objects.create(
            company=self.company, license_plate='ABC123', make='Toyota',
            model='Corolla', year=2020, daily_rate='50.00',
        )
        self.other_vehicle = Vehicle.objects.create(
            company=self.other_company, license_plate='XYZ999', make='Ford',
            model='Focus', year=2019, daily_rate='40.00',
        )
        self.doc = self._make_doc(self.vehicle, name='registration.pdf')
        self.other_doc = self._make_doc(self.other_vehicle, name='insurance.pdf')

    def _make_doc(self, vehicle, name='reg.pdf'):
        return VehicleDocument.objects.create(
            vehicle=vehicle,
            company=vehicle.company,
            doc_type='carte_grise',
            expiry_date=timezone.now().date() + timedelta(days=90),
            file=ContentFile(FILE_BYTES, name=name),
            original_filename=name,
        )

    def _download_url(self, pk):
        return reverse('fleet:document_download', kwargs={'pk': pk})


class VehicleDocumentModelTests(DocumentTestCase):
    def test_get_signed_download_url_points_to_signed_route(self):
        url = self.doc.get_signed_download_url()
        self.assertIn(reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk}), url)
        self.assertIn('token=', url)

    def test_signed_url_token_encodes_expected_payload(self):
        url = self.doc.get_signed_download_url(ttl=3600)
        token = url.split('token=', 1)[1]
        data = signing.loads(token)
        self.assertEqual(1, data['v'])
        self.assertEqual(self.doc.pk, data['doc'])
        self.assertEqual(self.company.pk, data['company'])
        self.assertEqual('vehicle_document_download', data['purpose'])
        self.assertEqual(self.doc.download_token_version, data['version'])
        self.assertAlmostEqual(timezone.now().timestamp() + 3600, float(data['exp']), delta=10)

    def test_revoke_download_links_increments_token_version(self):
        self.doc.revoke_download_links()
        self.assertEqual(2, self.doc.download_token_version)
        self.doc.refresh_from_db()
        self.assertEqual(2, self.doc.download_token_version)

    def test_save_replaces_old_physical_file(self):
        original_name = self.doc.file.name
        self.doc.file = ContentFile(b'second version', name='replacement.pdf')
        self.doc.save()
        storage = self.doc.file.storage
        self.assertFalse(storage.exists(original_name), 'superseded file must be deleted')
        self.assertTrue(storage.exists(self.doc.file.name))

    def test_delete_removes_physical_file(self):
        name = self.doc.file.name
        storage = self.doc.file.storage
        self.doc.delete()
        self.assertFalse(storage.exists(name), 'physical file must be deleted')


class DocumentDownloadViewTests(DocumentTestCase):
    def test_download_requires_login(self):
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 302)

    def test_download_requires_staff(self):
        self.client.force_login(
            User.objects.create_user(username='regular', password='pass1234'),
        )
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 403)

    def test_staff_downloads_document(self):
        self.client.force_login(self.user)
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FILE_BYTES, b''.join(response.streaming_content))
        disposition = response['Content-Disposition']
        self.assertIn('attachment', disposition)
        self.assertIn('registration.pdf', disposition)
        self.assertEqual('application/pdf', response['Content-Type'])
        self.assertEqual('nosniff', response['X-Content-Type-Options'])
        self.assertEqual('private, no-store', response['Cache-Control'])
        self.assertEqual('0', response['Expires'])

    def test_download_uses_original_filename_for_non_ascii(self):
        self.client.force_login(self.user)
        self.doc.original_filename = 'document à télécharger.pdf'
        self.doc.save()
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertIn('filename*=UTF-8', response['Content-Disposition'])

    def test_download_audits_success_row(self):
        self.client.force_login(self.user)
        self.client.get(self._download_url(self.doc.pk))
        row = AuditLog.objects.filter(action='DOWNLOAD').latest('id')
        self.assertEqual(self.company.pk, row.company_id)
        self.assertIn('Document downloaded', row.change_summary)

    def test_download_hides_cross_tenant_document(self):
        self.client.force_login(self.user)
        response = self.client.get(self._download_url(self.other_doc.pk))
        self.assertEqual(response.status_code, 404)

    def test_superuser_downloads_any_company(self):
        superuser = User.objects.create_superuser(
            username='root', password='pass1234', email='root@example.com',
        )
        self.client.force_login(superuser)
        response = self.client.get(self._download_url(self.other_doc.pk))
        self.assertEqual(response.status_code, 200)

    def test_download_missing_file_returns_404(self):
        self.client.force_login(self.user)
        name = self.doc.file.name
        self.doc.file.storage.delete(name)
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 404)

    def test_download_non_whitelisted_extension_returns_404(self):
        self.client.force_login(self.user)
        self.doc.file = ContentFile(b'not allowed', name='evil.exe')
        self.doc.save()
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 404)


class DocumentDownloadSignedTests(DocumentTestCase):
    def _signed_token(self, doc, **overrides):
        payload = {
            'v': 1,
            'doc': doc.pk,
            'company': doc.vehicle.company_id,
            'purpose': 'vehicle_document_download',
            'version': doc.download_token_version,
            'exp': timezone.now().timestamp() + 3600,
        }
        payload.update(overrides)
        return signing.dumps(payload)

    def _signed_url(self, doc, **overrides):
        url = reverse('fleet:document_download_signed', kwargs={'pk': doc.pk})
        return f'{url}?token={self._signed_token(doc, **overrides)}'

    def test_signed_download_works_without_login(self):
        response = self.client.get(self._signed_url(self.doc))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FILE_BYTES, b''.join(response.streaming_content))

    def test_signed_download_rejects_expired_token(self):
        url = self._signed_url(self.doc, exp=timezone.now().timestamp() - 10)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_revoked_token(self):
        url = self._signed_url(self.doc)
        self.doc.revoke_download_links()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_company(self):
        url = self._signed_url(self.doc, company=self.other_company.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_document(self):
        url = self._signed_url(self.doc)
        wrong = reverse('fleet:document_download_signed', kwargs={'pk': self.other_doc.pk})
        response = self.client.get(f'{wrong}?token={url.split("token=", 1)[1]}')
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_tampered_token(self):
        token = self._signed_token(self.doc)
        tampered = (token[:-4] + ('A' if token[-4] != 'A' else 'B') + token[-3:])
        url = reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk})
        response = self.client.get(f'{url}?token={tampered}')
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_missing_token(self):
        url = reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_purpose(self):
        url = self._signed_url(self.doc, purpose='other')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_version(self):
        url = self._signed_url(self.doc, version=999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_audits_success_and_denial(self):
        url = self._signed_url(self.doc)
        self.client.get(url)
        self.assertEqual(1, AuditLog.objects.filter(action='DOWNLOAD').count())
        self.client.get(self._signed_url(self.doc, exp=timezone.now().timestamp() - 10))
        self.assertEqual(2, AuditLog.objects.filter(action='DOWNLOAD').count())
