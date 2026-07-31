from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _

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
    list_display = ('created_at', 'action', 'username', 'content_type', 'object_repr', 'change_summary', 'ip_address', 'session_key')
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
