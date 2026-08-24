import logging

from django.conf import settings
from django.core import signing
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

from .validators import (
    DocumentUploadTo,
    validate_file_extension,
    validate_file_size,
    validate_mime_type,
)


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_("Company name"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name=_("User"))
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name=_("Company"))

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")


class TenantScopedManager(models.Manager):
    def for_company(self, company):
        return self.filter(company=company)


class TenantScopedModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, editable=False, verbose_name=_("Company"))
    objects = TenantScopedManager()

    class Meta:
        abstract = True


class Vehicle(TenantScopedModel):
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('rented', _('Rented')),
        ('maintenance', _('Maintenance')),
        ('out_of_service', _('Out of service')),
    ]

    license_plate = models.CharField(max_length=20, unique=True, verbose_name=_("License plate"))
    make = models.CharField(max_length=50, verbose_name=_("Make"))
    model = models.CharField(max_length=50, verbose_name=_("Model"))
    year = models.IntegerField(verbose_name=_("Year"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_("Status"))
    current_km = models.IntegerField(default=0, verbose_name=_("Current km"))
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Daily rate"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.make} {self.model} - {self.license_plate}"

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")


class VehicleDocument(TenantScopedModel):
    DOC_TYPE_CHOICES = [
        ('carte_grise', _('Registration card')),
        ('insurance', _('Insurance')),
        ('visite_technique', _('Technical inspection')),
        ('vignette', _('Vignette')),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents', verbose_name=_("Vehicle"))
    doc_type = models.CharField(max_length=30, choices=DOC_TYPE_CHOICES, verbose_name=_("Document type"))
    doc_number = models.CharField(max_length=50, blank=True, verbose_name=_("Document number"))
    expiry_date = models.DateField(verbose_name=_("Expiry date"))
    file = models.FileField(
        upload_to=DocumentUploadTo(), blank=True, verbose_name=_("File"),
        validators=[validate_file_extension, validate_file_size, validate_mime_type],
    )
    original_filename = models.CharField(
        max_length=255, blank=True, default='', verbose_name=_('Original filename'),
    )
    download_token_version = models.PositiveIntegerField(
        default=1, verbose_name=_('Download token version'),
    )

    def save(self, *args, **kwargs):
        # Best-effort removal of the superseded physical file on replacement.
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).only('file').first()
            if old is not None and old.file and old.file.name and old.file != self.file:
                old_name = old.file.name
                if old.file.storage.exists(old_name):
                    try:
                        old.file.storage.delete(old_name)
                    except OSError:
                        logger.warning('Could not delete superseded document file %s', old_name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Best-effort removal of the physical file; never aborts the DB delete.
        storage = self.file.storage
        name = self.file.name
        result = super().delete(*args, **kwargs)
        if name and storage.exists(name):
            try:
                storage.delete(name)
            except OSError:
                logger.warning('Could not delete document file %s', name)
        return result

    def get_signed_download_url(self, ttl=None):
        ttl = ttl if ttl is not None else settings.DOCUMENT_SIGNED_URL_TTL
        payload = {
            'v': 1,
            'doc': self.pk,
            'company': self.vehicle.company_id,
            'purpose': 'vehicle_document_download',
            'version': self.download_token_version,
            'exp': timezone.now().timestamp() + ttl,
        }
        url = reverse('fleet:document_download_signed', kwargs={'pk': self.pk})
        return f'{url}?token={signing.dumps(payload)}'

    def revoke_download_links(self):
        type(self).objects.filter(pk=self.pk).update(
            download_token_version=F('download_token_version') + 1,
        )
        self.refresh_from_db(fields=['download_token_version'])

    @property
    def days_until_expiry(self):
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    @property
    def is_expired(self):
        return self.days_until_expiry < 0

    @property
    def is_expiring_soon(self):
        return 0 <= self.days_until_expiry <= 30

    def __str__(self):
        return f"{self.vehicle} - {self.get_doc_type_display()}"

    class Meta:
        verbose_name = _("Vehicle document")
        verbose_name_plural = _("Vehicle documents")


class Driver(TenantScopedModel):
    first_name = models.CharField(max_length=100, verbose_name=_("First name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last name"))
    cin = models.CharField(max_length=20, unique=True, verbose_name=_("CIN number"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    license_number = models.CharField(max_length=30, verbose_name=_("License number"))
    license_expiry = models.DateField(verbose_name=_("License expiry"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")


class Booking(TenantScopedModel):
    STATUS_CHOICES = [
        ('confirmed', _('Confirmed')),
        ('rented', _('Rented')),
        ('returned', _('Returned')),
        ('late', _('Late')),
        ('cancelled', _('Cancelled')),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Vehicle"))
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='bookings', verbose_name=_("Driver"))
    customer_name = models.CharField(max_length=200, verbose_name=_("Customer name"))
    customer_phone = models.CharField(max_length=20, verbose_name=_("Customer phone"))
    pickup_date = models.DateTimeField(verbose_name=_("Pickup date"))
    expected_return = models.DateTimeField(verbose_name=_("Expected return"))
    actual_return = models.DateTimeField(null=True, blank=True, verbose_name=_("Actual return"))
    pickup_km = models.IntegerField(default=0, verbose_name=_("Pickup km"))
    return_km = models.IntegerField(null=True, blank=True, verbose_name=_("Return km"))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Deposit"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', verbose_name=_("Status"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_late(self):
        return self.status == 'rented' and timezone.now() > self.expected_return

    @property
    def days_late(self):
        if not self.is_late:
            return 0
        delta = timezone.now() - self.expected_return
        return delta.days

    def __str__(self):
        return f"{self.customer_name} - {self.vehicle} ({self.pickup_date})"

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")


class Maintenance(TenantScopedModel):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenances', verbose_name=_("Vehicle"))
    date = models.DateField(verbose_name=_("Date"))
    km_at_service = models.IntegerField(verbose_name=_("Km at service"))
    type = models.CharField(max_length=100, verbose_name=_("Type"))
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Cost"))
    next_service_km = models.IntegerField(null=True, blank=True, verbose_name=_("Next service at (km)"))
    next_service_date = models.DateField(null=True, blank=True, verbose_name=_("Next service (date)"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    @property
    def is_due(self):
        return (
            self.next_service_km is not None
            and self.vehicle.current_km >= self.next_service_km
        ) or (
            self.next_service_date is not None
            and timezone.now().date() >= self.next_service_date
        )

    def __str__(self):
        return f"{self.vehicle} - {self.type} ({self.date})"

    class Meta:
        verbose_name = _("Maintenance")
        verbose_name_plural = _("Maintenance records")


class Violation(TenantScopedModel):
    STATUS_CHOICES = [
        ('new', _('New')),
        ('driver_designated', _('Driver designated')),
        ('paid', _('Paid')),
        ('disputed', _('Disputed')),
        ('overdue', _('Overdue')),
    ]
    TYPE_CHOICES = [
        ('speeding', _('Speeding')),
        ('red_light', _('Red light')),
        ('seatbelt', _('Seatbelt')),
        ('phone', _('Phone use')),
        ('parking', _('Parking')),
        ('other', _('Other')),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='violations', verbose_name=_("Vehicle"))
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='violations', verbose_name=_("Driver"))
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='violations', verbose_name=_("Booking"))
    violation_date = models.DateTimeField(verbose_name=_("Violation date"))
    violation_location = models.CharField(max_length=300, blank=True, verbose_name=_("Location"))
    violation_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='other', verbose_name=_("Violation type"))
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Fine amount"))
    majoration_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Surcharge"))
    notification_date = models.DateField(null=True, blank=True, verbose_name=_("Notification date"))
    payment_deadline = models.DateField(null=True, blank=True, verbose_name=_("Payment deadline"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_("Status"))
    paid_by = models.CharField(max_length=20, blank=True, verbose_name=_("Paid by"))
    points_deducted = models.IntegerField(default=0, verbose_name=_("Points deducted"))
    pv_number = models.CharField(max_length=50, blank=True, verbose_name=_("PV number"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_due(self):
        return self.fine_amount + self.majoration_amount

    @property
    def is_overdue(self):
        if self.payment_deadline and self.status not in ('paid',):
            return timezone.now().date() > self.payment_deadline
        return False

    class Meta:
        verbose_name = _("Violation")
        verbose_name_plural = _("Violations")

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.get_violation_type_display()} ({self.violation_date})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', _('Login')),
        ('LOGOUT', _('Logout')),
        ('LOGIN_FAILED', _('Failed login')),
        ('CREATE', _('Create')),
        ('UPDATE', _('Update')),
        ('DELETE', _('Delete')),
        ('CHANGE_STATUS', _('Status change')),
        ('PICKUP', _('Pickup')),
        ('RETURN', _('Return')),
        ('DOWNLOAD', _('Download')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=_("User"))
    username = models.CharField(max_length=150, blank=True, verbose_name=_("Username"))
    ip_address = models.GenericIPAddressField(null=True, verbose_name=_("IP address"))
    user_agent = models.CharField(max_length=500, blank=True, verbose_name=_("User agent"))
    session_key = models.CharField(max_length=40, blank=True, verbose_name=_("Session key"))
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_("Action"))
    content_type = models.CharField(max_length=100, blank=True, verbose_name=_("Content type"))
    object_id = models.CharField(max_length=50, blank=True, verbose_name=_("Object ID"))
    object_repr = models.CharField(max_length=200, blank=True, verbose_name=_("Object representation"))
    change_summary = models.CharField(max_length=500, blank=True, verbose_name=_("Change summary"))
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        verbose_name=_('Company'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = _('Audit log')
        verbose_name_plural = _('Audit logs')

    def __str__(self):
        return f"{self.get_action_display()} - {self.username} ({self.created_at})"
