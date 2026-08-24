from django import forms
from django.contrib import admin
from django.db import models
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .audit import log_audit
from .models import (
    AuditLog,
    Booking,
    Company,
    Driver,
    Maintenance,
    Vehicle,
    VehicleDocument,
    Violation,
)
from .pricing import calculate_booking_total


class VehicleDocumentAdminForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = '__all__'

    def save(self, commit=True):
        doc = super().save(commit=False)
        uploaded = self.files.get('file')
        if uploaded is not None:
            doc.original_filename = uploaded.name
        if commit:
            doc.save()
        return doc


class AdminDocumentFileWidget(forms.ClearableFileInput):
    """File widget whose 'current file' link is the authenticated download URL."""
    template_name = 'admin/fleet/widgets/document_file.html'

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        download_url = None
        instance = getattr(value, 'instance', None)
        if value and instance is not None and getattr(instance, 'pk', None):
            download_url = reverse('fleet:document_download', kwargs={'pk': instance.pk})
        ctx['widget']['download_url'] = download_url
        return ctx


class TenantAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'profile'):
            return qs.filter(company=request.user.profile.company)
        return qs.none()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)


@admin.register(Vehicle)
class VehicleAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'model', 'year', 'status', 'current_km', 'daily_rate')
    list_filter = ('status', 'make', 'year')
    search_fields = ('license_plate', 'make', 'model')
    list_editable = ('status',)


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('vehicle', 'doc_type', 'doc_number', 'expiry_date', 'days_until_expiry', 'is_expired')
    list_filter = ('doc_type', 'vehicle')
    search_fields = ('vehicle__license_plate', 'doc_number')
    form = VehicleDocumentAdminForm
    formfield_overrides = {
        models.FileField: {'widget': AdminDocumentFileWidget},
    }
    change_form_template = 'admin/fleet/vehicledocument/change_form.html'
    readonly_fields = ('download_token_version', 'original_filename')

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<path:object_id>/generate-download-link/',
                self.admin_site.admin_view(self.generate_download_link_view),
                name='fleet_vehicledocument_generate_link',
            ),
        ]
        return custom + urls

    def generate_download_link_view(self, request, object_id):
        doc = self.get_queryset(request).filter(pk=object_id).first()
        if doc is None:
            raise Http404
        if request.method == 'POST':
            ttl_seconds = {'15m': 15 * 60, '1h': 60 * 60, '24h': 24 * 60 * 60}
            seconds = ttl_seconds.get(request.POST.get('ttl', '1h'), 60 * 60)
            url = request.build_absolute_uri(doc.get_signed_download_url(ttl=seconds))
            return render(
                request,
                'admin/fleet/vehicledocument/download_link.html',
                {'doc': doc, 'download_url': url, 'opts': self.opts},
            )
        return render(
            request,
            'admin/fleet/vehicledocument/generate_link.html',
            {'doc': doc, 'opts': self.opts},
        )

    def response_change(self, request, obj):
        if '_generate_link' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:fleet_vehicledocument_generate_link', args=[obj.pk]),
            )
        if '_revoke_links' in request.POST:
            obj.revoke_download_links()
            log_audit(request, 'DOWNLOAD', obj=obj, summary=_('Temporary links revoked'))
            self.message_user(request, _('Temporary links revoked'))
            return HttpResponseRedirect(
                reverse('admin:fleet_vehicledocument_change', args=[obj.pk]),
            )
        return super().response_change(request, obj)

    def get_days_remaining(self, obj):
        days = obj.days_until_expiry
        if days < 0:
            return format_html('<span style="color:red;">{} ({})</span>', _('Expired'), days)
        if days <= 30:
            return format_html('<span style="color:orange;">{} {}</span>', days, _('day(s)'))
        return f'{days} {_("day(s)")}'

    get_days_remaining.short_description = _('Days remaining')


@admin.register(Driver)
class DriverAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'cin', 'phone', 'license_number', 'license_expiry', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('first_name', 'last_name', 'cin', 'license_number')
    list_editable = ('is_active',)


@admin.register(Booking)
class BookingAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('customer_name', 'vehicle', 'driver', 'pickup_date', 'expected_return', 'status', 'total_amount', 'get_is_late')
    list_filter = ('status', 'vehicle', 'driver')
    search_fields = ('customer_name', 'customer_phone', 'vehicle__license_plate')
    list_editable = ('status',)
    date_hierarchy = 'pickup_date'

    def save_model(self, request, obj, form, change):
        # Server-authoritative total_amount (F3/F8): recompute from the
        # vehicle's daily_rate and the rental window, ignoring any admin-
        # submitted value. Mirrors BookingForm.save(). deposit is unchanged.
        obj.total_amount = calculate_booking_total(
            obj.vehicle, obj.pickup_date, obj.expected_return
        )
        super().save_model(request, obj, form, change)

    def get_is_late(self, obj):
        if obj.is_late:
            return format_html('<span style="color:red;">⚠️ {}</span>', _('Late'))
        return '✓'

    get_is_late.short_description = _('Late status')


@admin.register(Maintenance)
class MaintenanceAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('vehicle', 'type', 'date', 'km_at_service', 'cost', 'next_service_km', 'is_due')
    list_filter = ('type', 'vehicle')
    search_fields = ('vehicle__license_plate', 'type')
    date_hierarchy = 'date'


@admin.register(Violation)
class ViolationAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'violation_type', 'violation_date', 'fine_amount', 'status', 'is_overdue')
    list_filter = ('status', 'violation_type', 'vehicle')
    search_fields = ('vehicle__license_plate', 'pv_number')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'username', 'content_type', 'object_repr', 'change_summary', 'ip_address', 'session_key', 'company')
    list_filter = ('action', 'created_at')
    search_fields = ('username', 'content_type', 'change_summary')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
