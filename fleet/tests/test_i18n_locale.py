from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Booking, Company, Driver, UserProfile, Vehicle


class LocaleTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Locale Test Co')
        self.user = User.objects.create_user(username='admin', password='pass1234', is_staff=True)
        UserProfile.objects.create(user=self.user, company=self.company)
        self.client = Client()
        self.client.login(username='admin', password='pass1234')
        self.vehicle = Vehicle.objects.create(
            license_plate='1234-أ-1', make='Renault', model='Clio',
            year=2020, current_km=50000, daily_rate=Decimal('300.00'),
            status='available', company=self.company,
        )
        self.driver = Driver.objects.create(
            first_name='Test', last_name='Driver',
            cin='LOC123456', phone='0500000000',
            license_number='LIC-LOC-1',
            license_expiry='2028-01-01', company=self.company,
        )

    def set_language(self, code, next_url=None):
        data = {'language': code}
        if next_url:
            data['next'] = next_url
        return self.client.post(reverse('set_language'), data)

    def language_cookie(self):
        return self.client.cookies.get(settings.LANGUAGE_COOKIE_NAME).value

    def booking_post(self):
        pickup = timezone.now() + timedelta(days=1)
        ret = pickup - timedelta(days=3)
        return {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'customer_name': 'Test Client',
            'customer_phone': '0600000000',
            'pickup_date': pickup.strftime('%Y-%m-%d %H:%M'),
            'expected_return': ret.strftime('%Y-%m-%d %H:%M'),
            'total_amount': '300.00',
            'deposit': '0.00',
            'notes': '',
        }


class SetLanguageTests(LocaleTestCase):
    def test_switch_to_french_persists_and_renders(self):
        self.set_language('fr')
        self.assertEqual(self.language_cookie(), 'fr')
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertContains(response, 'lang="fr"')
        self.assertContains(response, 'dir="ltr"')
        self.assertContains(response, 'Véhicules')
        self.assertContains(response, 'Tableau de bord')

    def test_switch_to_arabic_sets_rtl(self):
        self.set_language('ar')
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertContains(response, 'lang="ar"')
        self.assertContains(response, 'dir="rtl"')
        self.assertContains(response, 'bootstrap.rtl.min.css')
        self.assertContains(response, 'المركبات')
        self.assertContains(response, 'لوحة القيادة')

    def test_switch_back_to_english_resets_ltr(self):
        self.set_language('ar')
        self.set_language('en')
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertContains(response, 'lang="en"')
        self.assertContains(response, 'dir="ltr"')
        self.assertContains(response, 'bootstrap.min.css')
        self.assertContains(response, 'Vehicles')
        self.assertEqual(self.language_cookie(), 'en')

    def test_redirects_to_next_url(self):
        target = reverse('fleet:vehicle_list')
        response = self.set_language('fr', next_url=target)
        self.assertRedirects(response, target)

    def test_default_language_is_english(self):
        response = self.client.get(reverse('fleet:vehicle_list'))
        self.assertContains(response, 'lang="en"')
        self.assertContains(response, 'Vehicles')


class LogoutLabelTests(LocaleTestCase):
    def test_logout_label_french_includes_username(self):
        self.set_language('fr')
        response = self.client.get(reverse('fleet:dashboard'))
        self.assertContains(response, 'Déconnexion (admin)')

    def test_logout_label_arabic_includes_username(self):
        self.set_language('ar')
        response = self.client.get(reverse('fleet:dashboard'))
        self.assertContains(response, 'تسجيل الخروج (admin)')

    def test_logout_label_english_includes_username(self):
        response = self.client.get(reverse('fleet:dashboard'))
        self.assertContains(response, 'Logout (admin)')


class LocalizedValidationTests(LocaleTestCase):
    def test_booking_validation_error_in_french(self):
        self.set_language('fr')
        response = self.client.post(reverse('fleet:booking_create'), self.booking_post())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'La date de retour doit être après la date de prise en charge',
        )
        self.assertEqual(Booking.objects.count(), 0)

    def test_booking_validation_error_in_arabic(self):
        self.set_language('ar')
        response = self.client.post(reverse('fleet:booking_create'), self.booking_post())
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'تاريخ الرجوع يجب أن يكون بعد تاريخ الاستلام',
        )
        self.assertEqual(Booking.objects.count(), 0)
