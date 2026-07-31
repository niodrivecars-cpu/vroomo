from django.db import migrations


def populate_default_company(apps, schema_editor):
    Company = apps.get_model('fleet', 'Company')
    UserProfile = apps.get_model('fleet', 'UserProfile')
    User = apps.get_model('auth', 'User')
    Vehicle = apps.get_model('fleet', 'Vehicle')
    VehicleDocument = apps.get_model('fleet', 'VehicleDocument')
    Driver = apps.get_model('fleet', 'Driver')
    Booking = apps.get_model('fleet', 'Booking')
    Maintenance = apps.get_model('fleet', 'Maintenance')
    Violation = apps.get_model('fleet', 'Violation')

    default_company, _ = Company.objects.get_or_create(name='Default Company')

    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user, company=default_company)

    for model_cls in [Vehicle, VehicleDocument, Driver, Booking, Maintenance, Violation]:
        model_cls.objects.filter(company__isnull=True).update(company=default_company)


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0005_company_booking_company_driver_company_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_default_company),
    ]
