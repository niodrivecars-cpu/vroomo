from django import forms

from .models import Booking, Driver, Maintenance, Vehicle, VehicleDocument, Violation
from .validators import validate_file_extension, validate_file_size, validate_mime_type


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'make', 'model', 'year', 'status', 'current_km', 'daily_rate', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'cin', 'phone', 'license_number', 'license_expiry', 'is_active']
        widgets = {
            'license_expiry': forms.DateInput(attrs={'type': 'date'}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle', 'driver', 'customer_name', 'customer_phone', 'pickup_date', 'expected_return', 'total_amount', 'deposit', 'notes']
        widgets = {
            'pickup_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expected_return': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['vehicle'].queryset = Vehicle.objects.for_company(company)
            self.fields['driver'].queryset = Driver.objects.for_company(company)


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['doc_type', 'doc_number', 'expiry_date', 'file']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            validate_file_extension(file)
            validate_file_size(file)
            validate_mime_type(file)
        return file

    def save(self, commit=True):
        doc = super().save(commit=False)
        uploaded = self.files.get('file')
        if uploaded is not None:
            doc.original_filename = uploaded.name
        if commit:
            doc.save()
        return doc


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['date', 'km_at_service', 'type', 'cost', 'next_service_km', 'next_service_date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'next_service_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ['vehicle', 'driver', 'violation_date', 'violation_location', 'violation_type', 'fine_amount', 'majoration_amount', 'notification_date', 'payment_deadline', 'pv_number', 'notes']
        widgets = {
            'violation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notification_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_deadline': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['vehicle'].queryset = Vehicle.objects.for_company(company)
            self.fields['driver'].queryset = Driver.objects.for_company(company)
