"""Seed a deterministic dataset for the k6 concurrency smoke tests.

Creates two tenant companies with staff users, vehicles, drivers and one
uploaded document per vehicle, then writes a JSON config that the k6 scripts
in ``tests/performance/`` read at runtime.

The command is idempotent: re-running it reuses the same companies, users,
vehicles, drivers and documents (users get their password reset so a fresh
run always works) and only regenerates the signed-URL tokens in the config.
"""

import json

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from fleet.models import Company, Driver, UserProfile, Vehicle, VehicleDocument

DEFAULT_PASSWORD = 'Loadtest!2026'

# (key, company name, license-plate prefix)
COMPANIES = [
    ('A', 'Loadtest Alpha', 'LT-A'),
    ('B', 'Loadtest Beta', 'LT-B'),
]

VEHICLES_PER_COMPANY = 3
DRIVERS_PER_COMPANY = 2
USERS_PER_COMPANY = 2
DOC_TYPE = 'insurance'
DOC_EXPIRY = '2027-12-31'


def _pdf_bytes(padding=1024):
    """A minimal, validation-passing PDF byte string of deterministic size."""
    head = b'%PDF-1.4\n'
    body = (
        b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        b'2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n'
        b'trailer\n<< /Root 2 0 R >>\n'
    )
    pad = b'%' * padding
    eof = b'\n%%EOF\n'
    return head + body + pad + eof


def _tampered(url):
    """Return the same signed URL with a corrupted token (signature must fail)."""
    _, sep, token = url.partition('token=')
    if not sep:
        return url
    last = token[-1]
    corrupted = token[:-1] + ('x' if last != 'x' else 'y')
    return url[: url.index('token=')] + 'token=' + corrupted


class Command(BaseCommand):
    help = 'Seed the load-test dataset and write the k6 config JSON.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='loadtest_config.json',
            help='Path to write the k6 config JSON (default: loadtest_config.json in the CWD).',
        )
        parser.add_argument(
            '--password',
            default=DEFAULT_PASSWORD,
            help='Password assigned to every seeded user.',
        )

    def handle(self, *args, **options):
        output = options['output']
        password = options['password']

        config = {
            'companies': {},
            'users': [],
            'vehicles': [],
            'drivers': [],
            'documents': [],
        }

        for company_key, company_name, plate_prefix in COMPANIES:
            company, _ = Company.objects.get_or_create(name=company_name)
            config['companies'][company_key] = company_name

            for i in range(USERS_PER_COMPANY):
                username = f'loadtest.{company_key.lower()}.{i + 1}'
                user, _ = User.objects.get_or_create(username=username)
                user.is_staff = True
                user.set_password(password)
                user.save()
                UserProfile.objects.get_or_create(user=user, defaults={'company': company})
                config['users'].append({
                    'username': username,
                    'password': password,
                    'company': company_key,
                })

            vehicles = []
            for i in range(VEHICLES_PER_COMPANY):
                plate = f'{plate_prefix}-{i + 1:02d}'
                vehicle, _ = Vehicle.objects.get_or_create(
                    license_plate=plate,
                    defaults={
                        'company': company,
                        'make': 'Loadtest',
                        'model': f'Model {i + 1}',
                        'year': 2022,
                        'status': 'available',
                        'daily_rate': '100.00',
                    },
                )
                vehicles.append(vehicle)
                config['vehicles'].append({
                    'id': vehicle.pk,
                    'company': company_key,
                    'plate': plate,
                })

            for i in range(DRIVERS_PER_COMPANY):
                cin = f'CIN-{plate_prefix}-{i + 1:02d}'
                driver, _ = Driver.objects.get_or_create(
                    cin=cin,
                    defaults={
                        'company': company,
                        'first_name': 'Loadtest',
                        'last_name': f'Driver {i + 1}',
                        'phone': f'0600{i:04d}',
                        'license_number': f'LIC-{plate_prefix}-{i + 1}',
                        'license_expiry': '2028-06-30',
                        'is_active': True,
                    },
                )
                config['drivers'].append({'id': driver.pk, 'company': company_key})

            for vehicle in vehicles:
                document = VehicleDocument.objects.filter(
                    vehicle=vehicle, doc_type=DOC_TYPE,
                ).first()
                if document is None:
                    payload = _pdf_bytes()
                    document = VehicleDocument.objects.create(
                        vehicle=vehicle,
                        company=company,
                        doc_type=DOC_TYPE,
                        doc_number=f'{plate_prefix}-DOC-{vehicle.pk}',
                        expiry_date=DOC_EXPIRY,
                        original_filename=f'{plate_prefix}-{vehicle.pk}.pdf',
                        file=ContentFile(payload, name=f'{plate_prefix}-{vehicle.pk}.pdf'),
                    )
                signed = document.get_signed_download_url()
                config['documents'].append({
                    'id': document.pk,
                    'company': company_key,
                    'size': document.file.size,
                    'signed_url': signed,
                    'expired_signed_url': document.get_signed_download_url(ttl=-60),
                    'tampered_signed_url': _tampered(signed),
                })

        with open(output, 'w', encoding='utf-8') as fh:
            json.dump(config, fh, indent=2)

        n_users = len(config['users'])
        n_vehicles = len(config['vehicles'])
        n_drivers = len(config['drivers'])
        n_docs = len(config['documents'])
        n_companies = len(config['companies'])
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {n_users} users, {n_vehicles} vehicles, {n_drivers} drivers, '
            f'{n_docs} documents across {n_companies} companies.'
        ))
        self.stdout.write(f'Config written to: {output}')
