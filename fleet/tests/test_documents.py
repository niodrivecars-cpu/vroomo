from datetime import timedelta

from django.contrib.auth.models import User
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
