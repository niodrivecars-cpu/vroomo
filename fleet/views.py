from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Sum
from django.db.utils import OperationalError
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from django_ratelimit.decorators import ratelimit

from .audit import log_audit
from .decorators import staff_required
from .downloads import (
    decode_token,
    get_document_or_none,
    is_download_rate_limited,
    serve_document,
)
from .forms import (
    BookingForm,
    DriverForm,
    MaintenanceForm,
    VehicleDocumentForm,
    VehicleForm,
    ViolationForm,
)
from .models import Booking, Driver, Maintenance, Vehicle, VehicleDocument, Violation


def tenant_objects(request, model):
    return model.objects.for_company(request.company)


def tenant_get_object_or_404(request, model, **kwargs):
    return get_object_or_404(model, company=request.company, **kwargs)


class CustomLoginView(LoginView):
    @method_decorator(ratelimit(key='ip', rate=settings.SECURITY_RATE_LIMITS['login_ip'], method='POST', block=True))
    @method_decorator(ratelimit(key='post:username', rate=settings.SECURITY_RATE_LIMITS['login_user'], method='POST', block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    @method_decorator(ratelimit(key='ip', rate=settings.SECURITY_RATE_LIMITS['password_reset'], method='POST', block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    @method_decorator(ratelimit(key='ip', rate=settings.SECURITY_RATE_LIMITS['password_reset'], method='POST', block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard(request):
    qs = tenant_objects(request, Vehicle)
    total_vehicles = qs.count()
    available = qs.filter(status='available').count()
    rented = qs.filter(status='rented').count()
    maintenance_count = qs.filter(status='maintenance').count()

    bqs = tenant_objects(request, Booking)
    active_bookings = bqs.filter(status='rented')
    late_bookings = bqs.filter(
        status='rented',
        expected_return__lt=timezone.now()
    )

    today = timezone.now().date()
    dqs = tenant_objects(request, VehicleDocument)
    expiring_docs = dqs.filter(
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gte=today
    )
    expired_docs = dqs.filter(expiry_date__lt=today)

    mqs = tenant_objects(request, Maintenance)
    due_maintenance = [
        m for m in mqs.select_related('vehicle').all()
        if m.is_due
    ]

    context = {
        'total_vehicles': total_vehicles,
        'available': available,
        'rented': rented,
        'maintenance_count': maintenance_count,
        'active_bookings': active_bookings,
        'late_bookings': late_bookings,
        'expiring_docs': expiring_docs,
        'expired_docs': expired_docs,
        'due_maintenance': due_maintenance,
    }
    return render(request, 'fleet/dashboard.html', context)


@login_required
def vehicle_list(request):
    vehicles = tenant_objects(request, Vehicle).order_by('license_plate')
    paginator = Paginator(vehicles, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'fleet/vehicle_list.html', {'page_obj': page_obj, 'vehicles': page_obj})


@staff_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.company = request.company
            vehicle.save()
            log_audit(request, 'CREATE', vehicle, _('Added vehicle: %(plate)s') % {'plate': vehicle.license_plate})
            messages.success(request, _('Vehicle added successfully'))
            return redirect('fleet:vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add vehicle')})


@staff_required
def vehicle_edit(request, pk):
    vehicle = tenant_get_object_or_404(request, Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            log_audit(request, 'UPDATE', vehicle, _('Edited vehicle: %(plate)s') % {'plate': vehicle.license_plate})
            messages.success(request, _('Vehicle updated successfully'))
            return redirect('fleet:vehicle_detail', pk=pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit vehicle')})


@login_required
def vehicle_detail(request, pk):
    vehicle = tenant_get_object_or_404(request, Vehicle, pk=pk)
    documents = vehicle.documents.all()
    maintenances = vehicle.maintenances.all().order_by('-date')
    bookings = Booking.objects.for_company(request.company).filter(vehicle=vehicle).select_related('driver').order_by('-pickup_date')[:10]
    return render(request, 'fleet/vehicle_detail.html', {
        'vehicle': vehicle,
        'documents': documents,
        'maintenances': maintenances,
        'bookings': bookings,
    })


@staff_required
@require_POST
def vehicle_change_status(request, pk):
    vehicle = tenant_get_object_or_404(request, Vehicle, pk=pk)
    new_status = request.POST.get('status')

    if vehicle.status == 'rented' and new_status == 'available':
        messages.error(request, _('Cannot change a rented vehicle to available. Return the booking first.'))
    else:
        old_status = vehicle.status
        vehicle.status = new_status
        vehicle.save()
        log_audit(request, 'CHANGE_STATUS', vehicle, _('Changed status %(plate)s: %(old)s \u2192 %(new)s') % {'plate': vehicle.license_plate, 'old': old_status, 'new': new_status})
        messages.success(request, _('Vehicle status updated'))

    return redirect('fleet:vehicle_detail', pk=vehicle.pk)


@login_required
def booking_list(request):
    bookings = tenant_objects(request, Booking).select_related('vehicle', 'driver').order_by('-pickup_date')
    paginator = Paginator(bookings, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'fleet/booking_list.html', {'page_obj': page_obj, 'bookings': page_obj})


@staff_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, company=request.company)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']
            pickup = form.cleaned_data['pickup_date']
            ret = form.cleaned_data['expected_return']

            if pickup >= ret:
                form.add_error('expected_return', _('Return date must be after pickup date'))
            elif vehicle.status in ('maintenance', 'out_of_service'):
                form.add_error('vehicle', _('This vehicle is not available for booking (maintenance or out of service)'))
            else:
                conflict = Booking.objects.for_company(request.company).filter(
                    vehicle=vehicle,
                    status__in=['confirmed', 'rented'],
                    pickup_date__lt=ret,
                    expected_return__gt=pickup,
                ).exists()
                if conflict:
                    form.add_error('expected_return', _('This vehicle is already booked for this period'))
                else:
                    booking = form.save(commit=False)
                    booking.company = request.company
                    booking.status = 'confirmed'
                    booking.save()
                    log_audit(request, 'CREATE', booking, _('New booking: %(name)s - %(plate)s') % {'name': booking.customer_name, 'plate': booking.vehicle.license_plate})
                    messages.success(request, _('Booking created successfully'))
                    return redirect('fleet:booking_list')
    else:
        form = BookingForm(company=request.company)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add booking')})


@staff_required
def booking_edit(request, pk):
    booking = tenant_get_object_or_404(request, Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking, company=request.company)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicle']
            pickup = form.cleaned_data['pickup_date']
            ret = form.cleaned_data['expected_return']

            if pickup >= ret:
                form.add_error('expected_return', _('Return date must be after pickup date'))
            elif vehicle.status in ('maintenance', 'out_of_service') and booking.status != 'rented':
                form.add_error('vehicle', _('This vehicle is not available for booking (maintenance or out of service)'))
            else:
                conflict = Booking.objects.for_company(request.company).filter(
                    vehicle=vehicle,
                    status__in=['confirmed', 'rented'],
                    pickup_date__lt=ret,
                    expected_return__gt=pickup,
                ).exclude(pk=booking.pk).exists()
                if conflict:
                    form.add_error('expected_return', _('This vehicle is already booked for this period'))
                else:
                    form.save()
                    log_audit(request, 'UPDATE', booking, _('Edited booking: %(name)s') % {'name': booking.customer_name})
                    messages.success(request, _('Booking updated successfully'))
                    return redirect('fleet:booking_detail', pk=pk)
    else:
        form = BookingForm(instance=booking, company=request.company)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit booking')})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.for_company(request.company).select_related('vehicle', 'driver'),
        pk=pk,
    )
    return render(request, 'fleet/booking_detail.html', {'booking': booking})


@staff_required
def booking_pickup(request, pk):
    if request.method != 'POST':
        return redirect('fleet:booking_detail', pk=pk)

    booking = tenant_get_object_or_404(request, Booking, pk=pk)

    if booking.status != 'confirmed':
        messages.error(request, _('Cannot pick up a booking that is not confirmed'))
    else:
        booking.status = 'rented'
        booking.pickup_km = booking.vehicle.current_km
        booking.save()
        booking.vehicle.status = 'rented'
        booking.vehicle.save()
        log_audit(request, 'PICKUP', booking, _('Picked up vehicle: %(plate)s - %(name)s') % {'plate': booking.vehicle.license_plate, 'name': booking.customer_name})
        messages.success(request, _('Vehicle pickup recorded'))

    return redirect('fleet:booking_detail', pk=pk)


@staff_required
def booking_return(request, pk):
    if request.method != 'POST':
        return redirect('fleet:booking_detail', pk=pk)

    booking = tenant_get_object_or_404(request, Booking, pk=pk)

    if booking.status != 'rented':
        messages.error(request, _('Cannot return a booking that is not rented'))
    else:
        booking.status = 'returned'
        booking.actual_return = timezone.now()
        booking.return_km = booking.vehicle.current_km
        booking.save()
        booking.vehicle.status = 'available'
        booking.vehicle.save()
        log_audit(request, 'RETURN', booking, _('Returned vehicle: %(plate)s - %(name)s') % {'plate': booking.vehicle.license_plate, 'name': booking.customer_name})
        messages.success(request, _('Vehicle return recorded'))

    return redirect('fleet:booking_detail', pk=pk)


@staff_required
def driver_edit(request, pk):
    driver = tenant_get_object_or_404(request, Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            log_audit(request, 'UPDATE', driver, _('Edited driver: %(first)s %(last)s') % {'first': driver.first_name, 'last': driver.last_name})
            messages.success(request, _('Driver updated successfully'))
            return redirect('fleet:driver_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit driver')})


@login_required
def driver_detail(request, pk):
    driver = tenant_get_object_or_404(request, Driver, pk=pk)
    bookings = Booking.objects.for_company(request.company).filter(driver=driver).select_related('vehicle').order_by('-pickup_date')[:10]
    violations = Violation.objects.for_company(request.company).filter(driver=driver).order_by('-violation_date')
    total_fines = sum(v.total_due for v in violations)
    return render(request, 'fleet/driver_detail.html', {
        'driver': driver, 'bookings': bookings, 'violations': violations, 'total_fines': total_fines,
        'today': timezone.now().date(),
    })


@login_required
def driver_list(request):
    drivers = tenant_objects(request, Driver).order_by('last_name')
    paginator = Paginator(drivers, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'fleet/driver_list.html', {'page_obj': page_obj, 'drivers': page_obj})


@staff_required
def driver_create(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.company = request.company
            driver.save()
            log_audit(request, 'CREATE', driver, _('Added driver: %(first)s %(last)s') % {'first': driver.first_name, 'last': driver.last_name})
            messages.success(request, _('Driver added successfully'))
            return redirect('fleet:driver_list')
    else:
        form = DriverForm()
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add driver')})


@ratelimit(key='user_or_ip', rate=settings.SECURITY_RATE_LIMITS['upload_per_user'], method='POST', block=True)
@ratelimit(key='user_or_ip', rate=settings.SECURITY_RATE_LIMITS['upload_per_hour'], method='POST', block=True)
@staff_required
def document_create(request, pk):
    vehicle = tenant_get_object_or_404(request, Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.vehicle = vehicle
            doc.company = request.company
            doc.save()
            log_audit(request, 'CREATE', doc, _('Added document: %(type)s - %(plate)s') % {'type': doc.get_doc_type_display(), 'plate': vehicle.license_plate})
            messages.success(request, _('Document added successfully'))
            return redirect('fleet:vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleDocumentForm()
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add document for %(plate)s') % {'plate': vehicle.license_plate}})


@ratelimit(key='user_or_ip', rate=settings.SECURITY_RATE_LIMITS['upload_per_user'], method='POST', block=True)
@ratelimit(key='user_or_ip', rate=settings.SECURITY_RATE_LIMITS['upload_per_hour'], method='POST', block=True)
@staff_required
def document_edit(request, pk):
    doc = tenant_get_object_or_404(request, VehicleDocument, pk=pk)
    if request.method == 'POST':
        form = VehicleDocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            log_audit(request, 'UPDATE', doc, _('Edited document: %(type)s - %(plate)s') % {'type': doc.get_doc_type_display(), 'plate': doc.vehicle.license_plate})
            messages.success(request, _('Document updated successfully'))
            return redirect('fleet:vehicle_detail', pk=doc.vehicle.pk)
    else:
        form = VehicleDocumentForm(instance=doc)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit document')})


@staff_required
@require_POST
def document_delete(request, pk):
    doc = tenant_get_object_or_404(request, VehicleDocument, pk=pk)
    vehicle_pk = doc.vehicle.pk
    log_audit(request, 'DELETE', doc, _('Deleted document: %(type)s - %(plate)s') % {'type': doc.get_doc_type_display(), 'plate': doc.vehicle.license_plate})
    doc.delete()
    messages.success(request, _('Document deleted successfully'))
    return redirect('fleet:vehicle_detail', pk=vehicle_pk)


@require_GET
@login_required
@staff_required
def document_download(request, pk):
    if request.user.is_superuser:
        doc = get_object_or_404(VehicleDocument, pk=pk)
    else:
        doc = tenant_get_object_or_404(request, VehicleDocument, pk=pk)
    if is_download_rate_limited(request):
        log_audit(request, 'DOWNLOAD', summary=_('Download denied: rate limit exceeded'))
        return HttpResponseForbidden(_('Download denied: rate limit exceeded'))
    log_audit(request, 'DOWNLOAD', obj=doc, summary=_('Document downloaded'))
    return serve_document(doc, request)


@require_GET
def document_download_signed(request, pk):
    data = decode_token(request.GET.get('token'))
    if data is None:
        log_audit(request, 'DOWNLOAD', summary=_('Download denied: invalid or expired token'))
        return HttpResponseForbidden(_('Download denied: invalid or expired token'))
    doc = get_document_or_none(data.get('doc'), company_id=data.get('company'))
    if doc is None or doc.pk != pk or doc.download_token_version != data.get('version'):
        log_audit(request, 'DOWNLOAD', summary=_('Download denied: token does not match document'))
        return HttpResponseForbidden(_('Download denied: token does not match document'))
    if is_download_rate_limited(request):
        log_audit(request, 'DOWNLOAD', summary=_('Download denied: rate limit exceeded'))
        return HttpResponseForbidden(_('Download denied: rate limit exceeded'))
    log_audit(request, 'DOWNLOAD', obj=doc, summary=_('Document downloaded via signed link'))
    return serve_document(doc, request)


@staff_required
def maintenance_create(request, pk):
    vehicle = tenant_get_object_or_404(request, Vehicle, pk=pk)
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maint = form.save(commit=False)
            maint.vehicle = vehicle
            maint.company = request.company
            maint.save()
            if maint.km_at_service > vehicle.current_km:
                vehicle.current_km = maint.km_at_service
                vehicle.save()
            log_audit(request, 'CREATE', maint, _('Added maintenance: %(type)s - %(plate)s') % {'type': maint.type, 'plate': vehicle.license_plate})
            messages.success(request, _('Maintenance added successfully'))
            return redirect('fleet:vehicle_detail', pk=vehicle.pk)
    else:
        form = MaintenanceForm()
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add maintenance for %(plate)s') % {'plate': vehicle.license_plate}})


@staff_required
def maintenance_edit(request, pk):
    maint = tenant_get_object_or_404(request, Maintenance, pk=pk)
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maint)
        if form.is_valid():
            form.save()
            log_audit(request, 'UPDATE', maint, _('Edited maintenance: %(type)s - %(plate)s') % {'type': maint.type, 'plate': maint.vehicle.license_plate})
            messages.success(request, _('Maintenance updated successfully'))
            return redirect('fleet:vehicle_detail', pk=maint.vehicle.pk)
    else:
        form = MaintenanceForm(instance=maint)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit maintenance')})


@staff_required
@require_POST
def maintenance_delete(request, pk):
    maint = tenant_get_object_or_404(request, Maintenance, pk=pk)
    vehicle_pk = maint.vehicle.pk
    log_audit(request, 'DELETE', maint, _('Deleted maintenance: %(type)s - %(plate)s') % {'type': maint.type, 'plate': maint.vehicle.license_plate})
    maint.delete()
    messages.success(request, _('Maintenance deleted successfully'))
    return redirect('fleet:vehicle_detail', pk=vehicle_pk)


@login_required
def maintenance_list(request):
    maintenances = tenant_objects(request, Maintenance).select_related('vehicle').order_by('-date')
    paginator = Paginator(maintenances, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'fleet/maintenance_list.html', {'page_obj': page_obj, 'maintenances': page_obj})


@login_required
def violation_list(request):
    vqs = tenant_objects(request, Violation)
    violations = vqs.select_related('vehicle', 'driver').order_by('-violation_date')
    paginator = Paginator(violations, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    agg = vqs.aggregate(
        fine=Sum('fine_amount'), majoration=Sum('majoration_amount'),
    )
    total_fines = (agg['fine'] or 0) + (agg['majoration'] or 0)
    return render(request, 'fleet/violation_list.html', {'page_obj': page_obj, 'violations': page_obj, 'total_fines': total_fines})


@staff_required
def violation_create(request):
    if request.method == 'POST':
        form = ViolationForm(request.POST, company=request.company)
        if form.is_valid():
            violation = form.save(commit=False)
            violation.company = request.company
            if violation.driver is None:
                booking = Booking.objects.for_company(request.company).filter(
                    vehicle=violation.vehicle,
                    status__in=['confirmed', 'rented'],
                    pickup_date__lte=violation.violation_date,
                    expected_return__gte=violation.violation_date,
                ).first()
                if booking:
                    violation.driver = booking.driver
                    violation.booking = booking
                    violation.status = 'driver_designated'
            violation.save()
            log_audit(request, 'CREATE', violation, _('Added violation: %(type)s - %(plate)s') % {'type': violation.get_violation_type_display(), 'plate': violation.vehicle.license_plate})
            if violation.driver:
                messages.success(request, _('Violation added and linked to driver %(driver)s') % {'driver': violation.driver})
            else:
                messages.success(request, _('Violation added (no driver specified)'))
            return redirect('fleet:violation_list')
    else:
        form = ViolationForm(company=request.company)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Add violation')})


@staff_required
def violation_edit(request, pk):
    violation = tenant_get_object_or_404(request, Violation, pk=pk)
    if request.method == 'POST':
        form = ViolationForm(request.POST, instance=violation, company=request.company)
        if form.is_valid():
            form.save()
            log_audit(request, 'UPDATE', violation, _('Edited violation: %(type)s - %(plate)s') % {'type': violation.get_violation_type_display(), 'plate': violation.vehicle.license_plate})
            messages.success(request, _('Violation updated successfully'))
            return redirect('fleet:violation_list')
    else:
        form = ViolationForm(instance=violation, company=request.company)
    return render(request, 'fleet/form.html', {'form': form, 'title': _('Edit violation')})


@staff_required
@require_POST
def violation_delete(request, pk):
    violation = tenant_get_object_or_404(request, Violation, pk=pk)
    log_audit(request, 'DELETE', violation, _('Deleted violation: %(type)s - %(plate)s') % {'type': violation.get_violation_type_display(), 'plate': violation.vehicle.license_plate})
    violation.delete()
    messages.success(request, _('Violation deleted successfully'))
    return redirect('fleet:violation_list')


def health_check(request):
    probe_key = 'vroom:health:probe'
    checks = {}
    status = 'ok'

    try:
        connection.ensure_connection()
        checks['database'] = 'ok'
    except OperationalError:
        checks['database'] = 'error'
        status = 'error'

    try:
        cache.set(probe_key, 'ok', timeout=10)
        checks['cache'] = 'ok' if cache.get(probe_key) == 'ok' else 'error'
        if checks['cache'] == 'error':
            status = 'error'
    except Exception:  # noqa: BLE001
        checks['cache'] = 'error'
        status = 'error'

    data = {
        'status': status,
        'checks': checks,
        'time': timezone.now().isoformat(),
    }
    response = JsonResponse(data, status=200 if status == 'ok' else 503)
    response['Cache-Control'] = 'no-store'
    return response
