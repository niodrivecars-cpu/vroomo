import logging
import time
from datetime import timedelta
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.translation import gettext as _

from fleet.models import Booking, Driver, Maintenance, VehicleDocument

logger = logging.getLogger(__name__)


def send_mail_with_retry(subject, body, from_email, recipient_list, max_retries=3):
    for attempt in range(max_retries):
        try:
            send_mail(subject, body, from_email, recipient_list, fail_silently=False)
            return True
        except (SMTPException, OSError, ConnectionError) as e:
            logger.warning(_('Failed to send email (attempt %(attempt)d/%(max_retries)d): %(err)s'), {'attempt': attempt + 1, 'max_retries': max_retries, 'err': e})
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    logger.error(_('Failed to send email after %(count)d attempts'), {'count': max_retries})
    return False


class Command(BaseCommand):
    help = _('Send daily alert report')

    def handle(self, *args, **options):
        today = timezone.now().date()
        lines = []

        expired = VehicleDocument.objects.filter(expiry_date__lt=today).select_related('vehicle')
        for d in expired:
            lines.append(_('🔴 [Expired] %(plate)s - %(doc_type)s expired on %(date)s') % {'plate': d.vehicle.license_plate, 'doc_type': d.get_doc_type_display(), 'date': d.expiry_date})

        expiring = VehicleDocument.objects.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30)).select_related('vehicle')
        for d in expiring:
            lines.append(_('⚠️ [Upcoming] %(plate)s - %(doc_type)s expires on %(date)s (%(days)d days)') % {'plate': d.vehicle.license_plate, 'doc_type': d.get_doc_type_display(), 'date': d.expiry_date, 'days': d.days_until_expiry})

        late = Booking.objects.filter(status='rented', expected_return__lt=timezone.now()).select_related('vehicle', 'driver')
        for b in late:
            lines.append(_('🔴 [Late] %(plate)s - Customer %(name)s (%(phone)s) is %(days)d days late') % {'plate': b.vehicle.license_plate, 'name': b.customer_name, 'phone': b.customer_phone, 'days': b.days_late})

        for m in Maintenance.objects.select_related('vehicle').all():
            if m.is_due:
                lines.append(_('🔧 [Maintenance] %(plate)s - %(type)s due') % {'plate': m.vehicle.license_plate, 'type': m.type})

        expiring_licenses = Driver.objects.filter(license_expiry__gte=today, license_expiry__lte=today + timedelta(days=30), is_active=True)
        for dr in expiring_licenses:
            lines.append(_('🪪 [License] %(first)s %(last)s - license expires on %(date)s') % {'first': dr.first_name, 'last': dr.last_name, 'date': dr.license_expiry})

        if lines:
            subject = _('Vroom daily report - %(date)s (%(count)d alert(s))') % {'date': today, 'count': len(lines)}
            body = _('Vroom alerts:\n\n') + '\n'.join(lines) + _('\n\n-- Vroom system')
            success = send_mail_with_retry(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
            if not success:
                raise CommandError(_('Failed to send email after repeated attempts'))
            self.stdout.write(self.style.SUCCESS(_('Sent %(count)d alert(s) to %(email)s') % {'count': len(lines), 'email': settings.ADMIN_EMAIL}))
        else:
            self.stdout.write(self.style.SUCCESS(_('No alerts today')))
