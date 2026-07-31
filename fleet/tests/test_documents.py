from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone

from fleet.models import Company, UserProfile, Vehicle, VehicleDocument

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
