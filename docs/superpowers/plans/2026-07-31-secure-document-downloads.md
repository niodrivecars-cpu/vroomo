# Implementation Plan: Secure Document Downloads (RC1)

- **Date:** 2026-07-31
- **Status:** Ready for execution
- **Feature spec:** `docs/superpowers/specs/2026-07-31-secure-document-downloads-design.md`
- **Target:** `v1.0.0-rc1`

## Context

This is the final pre-RC1 security gap. `VehicleDocument.file` is currently served
directly from `/media/` (public, unauthenticated, un-tenant-scoped). We replace it
with private storage plus two download endpoints:

1. **Authenticated session endpoint** (`fleet:document_download`) — login + staff +
   tenant scope (superuser sees all), cross-tenant returns 404.
2. **Signed-token endpoint** (`fleet:document_download_signed`) — no login required;
   a `django.core.signing` payload with purpose, document pk, company pk, per-document
   token version, and expiry. Enables shareable temporary links that can be revoked.

Every attempt (success, denial, rate-limit block) is written to `AuditLog` with the
new `DOWNLOAD` action. `/media/` public serving is removed. Physical files are
deleted on replace/delete. Admin no longer renders raw `file.url`; it uses
authenticated downloads plus generate/revoke temporary-link controls.

Two additional long-term quality gates requested by the user are included as
Tasks 0 and 1: **repository bootstrap (git)** and a **hardened i18n catalog test**.

## Non-goals

- No user-facing UI changes outside the download link swap in `vehicle_detail.html`.
- No CI workflow changes — the CI file already runs the full fleet suite (so the
  hardened i18n test is automatically a permanent CI gate), `makemigrations --check`,
  `compilemessages`, `collectstatic`, `check --deploy`, ruff, bandit, and pip-audit.
- No form/validation changes (existing `VehicleDocument.file` validators stay).
- No middleware changes.
- No cloud object storage; `FileSystemStorage`/`InMemoryStorage` only.

## Definition of Done

- No public `/media/` serving anywhere (`config/urls.py`, nginx docs).
- All document downloads require either an authenticated staff session (tenant-scoped)
  or a valid, unexpired, unrevoked signed token matching the document and its company.
- Signed URLs expire (default TTL) and can be revoked (`download_token_version` bump).
- Every download attempt is audited (`AuditLog`, action `DOWNLOAD`, with `company` set).
- Physical files are removed on replace and delete (best-effort, never aborting).
- Admin renders only authenticated download links and offers generate/revoke controls.
- New `test_documents.py` suite green under BOTH `config.test_settings` (CI/README)
  and `config.settings.test` (spec).
- Hardened i18n catalog tests green; en/fr/ar `.po` share identical msgid sets with
  complete fr/ar translations and freshly regenerated `.mo` (via polib).
- `ruff check .`, `bandit -r fleet config -q -ll`, `pip-audit`, `check --deploy`,
  `makemigrations --check --dry-run` all clean.
- `docs/deployment.md` documents private downloads, signed URLs, and the removed
  public `/media/` block.

## Conventions and verified facts (execution context)

- All local python commands: `venv\Scripts\python.exe -m manage ...` (bare `python`
  is not on PATH). CI uses `python -m manage ...`.
- CI/README run tests with `--settings=config.test_settings` (no `InMemoryStorage`).
  `config/settings/test.py` adds `DEFAULT_FILE_STORAGE = InMemoryStorage`. New tests
  must pass under both: the `test_documents.py` base class sets
  `@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.InMemoryStorage')`.
- `Vehicle` required fields for fixtures: `company`, `license_plate` (unique),
  `make`, `model`, `year`, `daily_rate`; `status`/`current_km` have defaults.
- `Company(name=...)`, `UserProfile(user=..., company=...)`,
  `User.objects.create_user(username=..., password=..., is_staff=True)` mirror
  `fleet/tests/test_views.py::AuthTestCase`.
- Next migration after `fleet/migrations/0008_...` is `0009_*`.
- polib 1.2.0 is installed; `msgfmt` is NOT on PATH. polib's `.mo` writer excludes
  empty-`msgstr` entries exactly like `msgfmt` (verified), so regenerating `.mo` via
  polib preserves the mo/po sync test.
- `fleet/decorators.py` provides `staff_required` (default template
  `fleet/forbidden.html`) and the `forbidden(request, message=None)` helper.
- `fleet/audit.log_audit(request, action, obj=None, summary='')` writes
  user/ip/user_agent/session_key/action/content_type/object_id/object_repr/
  change_summary.
- django-ratelimit 4.1.0: `django_ratelimit.core.is_ratelimited(request, group, fn,
  key, rate, method, increment)` returns a bool. `key` may be a built-in simple key
  (`'ip'`, `'user'`, `'user_or_ip'`, `'post:<field>'`, ...) or a callable
  `(group, request)`. `method` accepts a string or list/tuple, matched
  case-insensitively (`_method_match` uppercases). `_method_match` runs before the
  key is evaluated. This codebase already uses `key='user_or_ip'` for upload limits.
- `docs/deployment.md` currently documents nginx serving `/media/` publicly — to be
  removed.
- `.gitignore` exists (covers `venv/`, `media/`, `.env`, `db.sqlite3`, `staticfiles/`,
  `__pycache__/`); needs `.ruff_cache/`, `vroomo/`, `websi/` added.
- **Not a git repo.** `vroomo/` is a stray empty nested git repo (a mistyped `git
  init` one level deep); `websi/` contains an unrelated ECC plugin repo
  (`websi/ECC/.git`) plus a stray `home.html`. Neither is part of Vroom; they are
  excluded from version control (not deleted — flagged for manual review).
- Git identity is NOT configured (global `user.name`/`user.email` unset). The
  bootstrap task prompts for repo-local identity.

---

## Task 0 — Repository bootstrap (git) — release blocker

Version control is a release blocker for RC1 (history, review, rollback, tagging,
CI push). Do this before any feature work.

### Steps

1. **Extend `.gitignore`** (append three lines):

   ```gitignore
   # Tooling / stray artifacts
   .ruff_cache/
   vroomo/
   websi/
   ```

   `vroomo/` and `websi/` are stray artifacts (nested unrelated repos). They are
   excluded, not deleted — flag to the user that they should review and remove them
   manually.

2. **Initialize the repository on `main`:**

   ```powershell
   git init -b main
   ```

   (git 2.55.0 supports `-b`.)

3. **Set repo-local identity** (blocking — global identity is unset). Ask the user
   for name/email, then:

   ```powershell
   git config user.name "<name>"
   git config user.email "<email>"
   ```

4. **Review what would be committed** — confirm `.env`, `venv/`, `media/`,
   `db.sqlite3`, `staticfiles/`, `.ruff_cache/`, `vroomo/`, `websi/` are all absent
   from `git status`, and that `package-lock.json` + `requirements-dev.txt` are
   intentionally tracked.

   ```powershell
   git add -A
   git status
   ```

5. **Initial commit:**

   ```powershell
   git commit -m "chore: bootstrap Vroom repository at RC1 baseline"
   ```

### Verification

- `git log --oneline` shows one commit on `main`.
- `git status` clean.
- `git check-ignore vroomo websi .ruff_cache` lists all three.

### Manual / out of scope (documented for the user)

- `git remote add origin <url>` then `git push -u origin main`.
- GitHub/GitLab: enable protected `main`, required PR review, and protected release
  tags (`v1.0.0-*`).

---

## Task 1 — Harden the i18n catalog quality gate

The existing `fleet/tests/test_i18n_catalog.py` already enforces identical msgid
sets across en/fr/ar, full fr/ar translation, mo/po sync, template/python string
coverage, and `%(name)s` placeholder consistency. Hardening adds: catalog parse,
duplicate msgids, required headers, configured-locale structure, and per-language
`Plural-Forms`. Because CI runs `python -m manage test fleet`, hardening the test
automatically hardens the CI gate.

### 1a. Extend `fleet/tests/test_i18n_catalog.py`

Full final content (supersedes current file):

```python
import re
from collections import Counter
from pathlib import Path

import polib
from django.conf import settings
from django.test import SimpleTestCase

# Policy: `en` is the canonical source language, not a translation. Its .po
# msgstr values are intentionally empty (Django falls back to the msgid), with a
# few deliberate identity overrides (e.g. '%(km)s km'). Only `fr` and `ar` must
# be fully translated; test_fr_and_ar_are_fully_translated enforces that.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_DIR = PROJECT_ROOT / 'locale'
LANGS = ('en', 'fr', 'ar')

TRANS_PAT = re.compile(r"{%\s*(?:translate|trans)\s+(['\"])(.*?)\1\s*%}", re.DOTALL)
BLOCK_PAT = re.compile(r"{%\s*blocktrans(?:late)?(?:.*?)%}(.*?){%\s*endblocktrans(?:late)?\s*%}", re.DOTALL)
VAR_PAT = re.compile(r"{{\s*([\w.]+)\s*}}")
PY_PAT = re.compile(r"\b(?:gettext|gettext_lazy|ugettext|ugettext_lazy|_)\((['\"])(.*?)\1\)")
PLACEHOLDER_PAT = re.compile(r"%\((\w+)\)s")

REQUIRED_HEADERS = (
    'Project-Id-Version',
    'Report-Msgid-Bugs-To',
    'POT-Creation-Date',
    'PO-Revision-Date',
    'Last-Translator',
    'Language-Team',
    'Language',
    'MIME-Version',
    'Content-Type',
    'Content-Transfer-Encoding',
    'Plural-Forms',
)

# Standard GNU gettext plural rules per language (checked verbatim in headers).
EXPECTED_PLURAL_FORMS = {
    'en': 'nplurals=2; plural=(n != 1);',
    'fr': 'nplurals=2; plural=(n > 1);',
    'ar': ('nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : '
           'n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;'),
}


def pofile(lang):
    return polib.pofile(str(LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'))


def mofile(lang):
    return polib.mofile(str(LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.mo'))


def active_entries(lang):
    return [e for e in pofile(lang) if not e.obsolete]


class CatalogIntegrityTests(SimpleTestCase):
    def test_catalogs_parse_without_error(self):
        # polib.pofile/mofile raise on malformed content; parsing IS the assertion.
        for lang in LANGS:
            po = pofile(lang)
            mo = mofile(lang)
            self.assertGreater(len(po), 0, f'[{lang}] empty .po catalog')
            self.assertGreater(len(mo), 0, f'[{lang}] empty or missing .mo catalog')

    def test_no_duplicate_msgids(self):
        for lang in LANGS:
            counts = Counter(e.msgid for e in active_entries(lang))
            dupes = {msgid for msgid, count in counts.items() if count > 1}
            self.assertEqual(set(), dupes, f'[{lang}] duplicate msgids: {dupes}')

    def test_headers_are_complete(self):
        for lang in LANGS:
            metadata = pofile(lang).metadata
            missing = [h for h in REQUIRED_HEADERS if h not in metadata]
            self.assertEqual([], missing, f'[{lang}] missing required headers')

    def test_plural_forms_are_valid(self):
        for lang, expected in EXPECTED_PLURAL_FORMS.items():
            self.assertEqual(
                expected,
                pofile(lang).metadata.get('Plural-Forms'),
                f'[{lang}] Plural-Forms header mismatch',
            )

    def test_all_locales_have_identical_msgid_sets(self):
        first = frozenset(e.msgid for e in active_entries('en'))
        for lang in LANGS[1:]:
            self.assertEqual(
                first,
                frozenset(e.msgid for e in active_entries(lang)),
                f'[{lang}] catalog has different msgids than en',
            )

    def test_fr_and_ar_are_fully_translated(self):
        for lang in ('fr', 'ar'):
            for e in active_entries(lang):
                self.assertTrue(
                    e.msgstr.strip(),
                    f'[{lang}] untranslated msgid: {e.msgid!r}',
                )

    def test_mo_files_are_valid_and_in_sync_with_po(self):
        for lang in LANGS:
            po_filled = {e.msgid for e in active_entries(lang) if e.msgstr.strip()}
            mo_ids = {e.msgid for e in mofile(lang) if not e.obsolete}
            self.assertEqual(
                po_filled,
                mo_ids,
                f'[{lang}] .mo must compile every translated .po entry (and only those)',
            )


class LocaleStructureTests(SimpleTestCase):
    def test_configured_locales_have_catalogs(self):
        configured = {code for code, _ in settings.LANGUAGES}
        for code in configured:
            self.assertIn(code, LANGS)
            self.assertTrue(
                (LOCALE_DIR / code / 'LC_MESSAGES' / 'django.po').exists(),
                f'[{code}] missing django.po',
            )
            self.assertTrue(
                (LOCALE_DIR / code / 'LC_MESSAGES' / 'django.mo').exists(),
                f'[{code}] missing django.mo',
            )
            self.assertEqual(
                code,
                pofile(code).metadata.get('Language'),
                f'[{code}] Language header does not match locale directory',
            )


class CatalogCoverageTests(SimpleTestCase):
    def test_every_template_string_is_in_en_catalog(self):
        catalog = {e.msgid for e in active_entries('en')}
        missing = []
        for t in sorted((PROJECT_ROOT / 'fleet' / 'templates').rglob('*.html')):
            text = t.read_text(encoding='utf-8')
            for m in TRANS_PAT.finditer(text):
                if m.group(2) not in catalog:
                    missing.append((t.name, m.group(2)))
            for m in BLOCK_PAT.finditer(text):
                body = re.sub(r'\s+', ' ', m.group(1)).strip()
                body = VAR_PAT.sub(r'%(\1)s', body)
                if body and not body.startswith('{%') and body not in catalog:
                    missing.append((t.name, body))
        self.assertEqual([], missing, 'Template strings missing from en catalog')

    def test_every_python_string_is_in_en_catalog(self):
        catalog = {e.msgid for e in active_entries('en')}
        files = [
            PROJECT_ROOT / 'fleet' / p
            for p in ('models.py', 'views.py', 'forms.py', 'audit.py', 'middleware.py',
                      'validators.py', 'decorators.py', 'admin.py', 'urls.py', 'apps.py')
        ]
        files += list((PROJECT_ROOT / 'fleet' / 'management').rglob('*.py'))
        missing = []
        for f in files:
            if not f.exists():
                continue
            for m in PY_PAT.finditer(f.read_text(encoding='utf-8')):
                s = m.group(2)
                if '%' in s or s.startswith('{') or '\n' in s:
                    continue
                if s not in catalog:
                    missing.append((f.name, s))
        self.assertEqual([], missing, 'Python strings missing from en catalog')


class PlaceholderConsistencyTests(SimpleTestCase):
    def test_translations_keep_msgid_placeholders(self):
        en_by_id = {e.msgid: e for e in active_entries('en')}
        for lang in ('fr', 'ar'):
            by_id = {e.msgid: e for e in active_entries(lang)}
            for msgid in en_by_id:
                msgid_vars = Counter(PLACEHOLDER_PAT.findall(msgid))
                if not msgid_vars:
                    continue
                msgstr_vars = Counter(PLACEHOLDER_PAT.findall(by_id[msgid].msgstr))
                self.assertEqual(
                    msgid_vars,
                    msgstr_vars,
                    f'[{lang}] placeholder mismatch for {msgid!r}',
                )
```

### 1b. Fix the catalogs so the new tests pass

1. **Add the missing `Last-Translator` header** to all three `.po` files. In each of
   `locale/{en,fr,ar}/LC_MESSAGES/django.po`, insert after the `PO-Revision-Date`
   line:

   ```
   "Last-Translator: \n"
   ```

2. **Fix the French `Plural-Forms` header.** In `locale/fr/LC_MESSAGES/django.po`
   line 13, change:

   ```
   "Plural-Forms: nplurals=2; plural=(n != 1);"
   ```
   to the standard French rule:
   ```
   "Plural-Forms: nplurals=2; plural=(n > 1);"
   ```

   (No catalog entries use plural forms — `msgid_plural` count is 0 for all locales —
   so this changes only the header; the `.mo` regenerates cleanly.)

3. **Regenerate all `.mo` files via polib** (excludes empty-`msgstr` entries like
   `msgfmt`, preserving the mo/po sync test; `en.mo` stays at its 4 filled entries):

   ```powershell
   venv\Scripts\python.exe -c "import polib; [polib.pofile('locale/%s/LC_MESSAGES/django.po' % l).save_as_mofile('locale/%s/LC_MESSAGES/django.mo' % l) for l in ('en','fr','ar')]"
   ```

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_i18n_catalog --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_i18n_catalog --settings=config.settings.test --verbosity=2
```

Expect 12 tests OK under both settings.

### Commit

```
test(i18n): harden catalog quality gates and fix fr plural forms
```

---

## Task 2 — Models, migration 0009, audit enrichment

### 2a. `fleet/models.py`

Add imports at top (keep existing `_` and `timezone` imports):

```python
import logging

from django.core import signing
from django.db.models import F
from django.urls import reverse
from django.conf import settings  # only if not already imported

logger = logging.getLogger(__name__)
```

(`settings` is already imported via `UserProfile`.)

**`AuditLog`:** add the `DOWNLOAD` action and the `company` FK (nullable,
`SET_NULL`, so history survives company deletion — documented deviation):

```python
class AuditLog(models.Model):
    ACTION_CHOICES = [
        # ...existing choices...
        ('DOWNLOAD', _('Download')),
    ]
    # ...existing fields...
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
        verbose_name=_('Company'),
    )
```

**`VehicleDocument`:** add two fields and three methods:

```python
class VehicleDocument(TenantScopedModel):
    # ...existing fields...
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
```

### 2b. `config/settings/base.py`

Add the signed-URL TTL (env-overridable, default 24 h):

```python
DOCUMENT_SIGNED_URL_TTL = int(os.environ.get('DOCUMENT_SIGNED_URL_TTL', str(24 * 60 * 60)))
```

### 2c. `fleet/audit.py` — record company on `log_audit`

Modify `log_audit` to derive `company_id` from the object when it has a
`vehicle` (covers `VehicleDocument`), and pass it to the `AuditLog` row:

```python
def log_audit(request, action, obj=None, summary=''):
    # ...existing header lines...
    company_id = None
    if obj is not None:
        vehicle = getattr(obj, 'vehicle', None)
        if vehicle is not None:
            company_id = vehicle.company_id
    # ...existing body, then in AuditLog.objects.create(...) add:
    company_id=company_id,
```

### 2d. Migration `0009`

Generate the schema migration, then append the backfill as a `RunPython`:

```powershell
venv\Scripts\python.exe -m manage makemigrations fleet --settings=config.test_settings
```

Edit the generated `fleet/migrations/0009_*.py` to append the data migration:

```python
def backfill_auditlog_company(apps, schema_editor):
    AuditLog = apps.get_model('fleet', 'AuditLog')
    VehicleDocument = apps.get_model('fleet', 'VehicleDocument')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ct = ContentType.objects.filter(app_label='fleet', model='vehicledocument').first()
    if ct is None:
        return
    for log in AuditLog.objects.filter(content_type=ct).only('id', 'object_id', 'company_id').iterator():
        doc = (
            VehicleDocument.objects.filter(pk=log.object_id)
            .select_related('vehicle')
            .only('id', 'vehicle__company_id')
            .first()
        )
        if doc is not None and doc.vehicle_id:
            log.company_id = doc.vehicle.company_id
            log.save(update_fields=['company_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    # ...existing autogenerated dependencies/operations...
    operations = [
        # ...autogenerated AddField operations...
        migrations.RunPython(backfill_auditlog_company, noop),
    ]
```

### 2e. Tests — start `fleet/tests/test_documents.py`

Base fixture (reused by all later tasks):

```python
from datetime import timedelta

from django.contrib.auth.models import User
from django.core import signing
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from fleet.models import AuditLog, Company, UserProfile, Vehicle, VehicleDocument

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
            doc_type='carte_grise',
            expiry_date=timezone.now().date() + timedelta(days=90),
            file=ContentFile(FILE_BYTES, name=name),
            original_filename=name,
        )
```

Model tests (Task 2):

```python
class VehicleDocumentModelTests(DocumentTestCase):
    def test_get_signed_download_url_points_to_signed_route(self):
        url = self.doc.get_signed_download_url()
        self.assertIn(reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk}), url)
        self.assertIn('token=', url)

    def test_signed_url_token_encodes_expected_payload(self):
        url = self.doc.get_signed_download_url(ttl=3600)
        token = url.split('token=', 1)[1]
        data = signing.loads(token)
        self.assertEqual(1, data['v'])
        self.assertEqual(self.doc.pk, data['doc'])
        self.assertEqual(self.company.pk, data['company'])
        self.assertEqual('vehicle_document_download', data['purpose'])
        self.assertEqual(self.doc.download_token_version, data['version'])
        self.assertAlmostEqual(timezone.now().timestamp() + 3600, float(data['exp']), delta=10)

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
```

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.settings.test --verbosity=2
venv\Scripts\python.exe -m manage makemigrations --check --dry-run --settings=config.test_settings
```

### Commit

```
feat(downloads): add VehicleDocument token fields and AuditLog company
```

---

## Task 3 — Download service + session download endpoint

### 3a. New module `fleet/downloads.py`

```python
import logging
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404
from django.utils import timezone
from django_ratelimit.core import is_ratelimited

from .audit import log_audit  # noqa: F401  (re-exported for views)
from .models import VehicleDocument

logger = logging.getLogger(__name__)

TOKEN_VERSION = 1
TOKEN_PURPOSE = 'vehicle_document_download'

# Whitelisted extension -> MIME map. Never trust the client: derive the content
# type from the stored file name, not from any request-supplied value.
EXTENSION_MIME = {
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
}


def _content_type_for_name(name):
    return EXTENSION_MIME.get(Path(name).suffix.lower())


def get_document_or_none(pk, company_id=None):
    qs = VehicleDocument.objects.select_related('vehicle', 'vehicle__company')
    try:
        doc = qs.get(pk=pk)
    except (VehicleDocument.DoesNotExist, ValueError, TypeError):
        return None
    if company_id is not None and doc.vehicle.company_id != company_id:
        return None
    return doc


def decode_token(token):
    """Validate the signed token; return the payload dict or None."""
    if not isinstance(token, str) or not token:
        return None
    try:
        data = signing.loads(token)
    except (signing.BadSignature, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get('v') != TOKEN_VERSION:
        return None
    if data.get('purpose') != TOKEN_PURPOSE:
        return None
    try:
        exp = float(data.get('exp'))
    except (TypeError, ValueError):
        return None
    if timezone.now().timestamp() > exp:
        return None
    return data


def is_download_rate_limited(request):
    """Rate-limit downloads per user (authenticated) or per IP (anonymous).

    Uses the built-in 'user_or_ip' simple key, matching the existing upload
    rate-limit convention. Called directly (not via a blocking decorator) so the
    view can audit the denial before returning 403.
    """
    rate = settings.SECURITY_RATE_LIMITS.get(
        'download_per_user' if request.user.is_authenticated else 'download_anon_ip',
        '20/h',
    )
    return is_ratelimited(
        request=request,
        group='document-download',
        key='user_or_ip',
        rate=rate,
        method='GET',
        increment=True,
    )


def serve_document(doc, request):
    if not doc.file or not doc.file.name:
        raise Http404
    storage = doc.file.storage
    name = doc.file.name
    if not storage.exists(name):
        raise Http404
    content_type = _content_type_for_name(name)
    if content_type is None:
        raise Http404
    try:
        f = storage.open(name, 'rb')
    except OSError:
        logger.exception('Could not open document %s', name)
        raise Http404
    filename = doc.original_filename or Path(name).name
    ascii_name = filename.encode('ascii', 'ignore').decode() or 'download'
    response = FileResponse(f, content_type=content_type)
    response['Content-Disposition'] = (
        f"attachment; filename=\"{ascii_name}\"; "
        f"filename*=UTF-8''{quote(filename)}"
    )
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
```

### 3b. `fleet/views.py` — session endpoint

Add imports (merge with existing; `login_required`, `staff_required`,
`tenant_get_object_or_404`, `log_audit`, `require_GET` already present or added):

```python
from django.http import FileResponse, HttpResponseForbidden  # FileResponse if used here
from django.utils.translation import gettext as _
from .downloads import decode_token, get_document_or_none, is_download_rate_limited, serve_document
```

Append the view:

```python
@require_GET
@login_required
@staff_required
def document_download(request, pk):
    doc = tenant_get_object_or_404(request, VehicleDocument, pk=pk)
    if is_download_rate_limited(request):
        log_audit(request, 'DOWNLOAD', summary=_('Download denied: rate limit exceeded'))
        return HttpResponseForbidden(_('Download denied: rate limit exceeded'))
    log_audit(request, 'DOWNLOAD', obj=doc, summary=_('Document downloaded'))
    return serve_document(doc, request)
```

### 3c. `fleet/urls.py`

```python
path('documents/<int:pk>/download/', views.document_download, name='document_download'),
```

### 3d. Remove public `/media/` serving — `config/urls.py`

Delete the DEBUG block serving `/media/` and remove the now-unused `static` import:

```python
# remove:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# remove the import line: from django.conf.urls.static import static
```

### 3e. `fleet/templates/fleet/vehicle_detail.html`

Locate the only `{{ doc.file.url }}` occurrence (document list, ~line 85) and replace
the link with the authenticated download view, labeled for translation:

```html
<a href="{% url 'fleet:document_download' doc.pk %}" title="{% translate 'Download document' %}">{% translate 'Download document' %}</a>
```

### 3f. Session-endpoint tests

```python
class DocumentDownloadViewTests(DocumentTestCase):
    def test_download_requires_login(self):
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 302)

    def test_download_requires_staff(self):
        self.client.force_login(
            User.objects.create_user(username='regular', password='pass1234'),
        )
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 403)

    def test_staff_downloads_document(self):
        self.client.force_login(self.user)
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FILE_BYTES, b''.join(response.streaming_content))
        disposition = response['Content-Disposition']
        self.assertIn('attachment', disposition)
        self.assertIn('registration.pdf', disposition)
        self.assertEqual('application/pdf', response['Content-Type'])
        self.assertEqual('nosniff', response['X-Content-Type-Options'])
        self.assertEqual('private, no-store', response['Cache-Control'])
        self.assertEqual('0', response['Expires'])

    def test_download_uses_original_filename_for_non_ascii(self):
        self.client.force_login(self.user)
        self.doc.original_filename = 'document à télécharger.pdf'
        self.doc.save()
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertIn('filename*=UTF-8', response['Content-Disposition'])

    def test_download_audits_success_row(self):
        self.client.force_login(self.user)
        self.client.get(self._download_url(self.doc.pk))
        row = AuditLog.objects.filter(action='DOWNLOAD').latest('id')
        self.assertEqual(self.company.pk, row.company_id)
        self.assertIn('Document downloaded', row.change_summary)

    def test_download_hides_cross_tenant_document(self):
        self.client.force_login(self.user)
        response = self.client.get(self._download_url(self.other_doc.pk))
        self.assertEqual(response.status_code, 404)

    def test_superuser_downloads_any_company(self):
        superuser = User.objects.create_superuser(
            username='root', password='pass1234', email='root@example.com',
        )
        self.client.force_login(superuser)
        response = self.client.get(self._download_url(self.other_doc.pk))
        self.assertEqual(response.status_code, 200)

    def test_download_missing_file_returns_404(self):
        self.client.force_login(self.user)
        name = self.doc.file.name
        self.doc.file.storage.delete(name)
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 404)

    def test_download_non_whitelisted_extension_returns_404(self):
        self.client.force_login(self.user)
        self.doc.file = ContentFile(b'not allowed', name='evil.exe')
        self.doc.save()
        response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(response.status_code, 404)
```

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.settings.test --verbosity=2
```

### Commit

```
feat(downloads): private document download service and session endpoint
```

---

## Task 4 — Signed URL download endpoint

### 4a. `fleet/views.py`

```python
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
```

No login/staff decorators — that is the point of a shareable signed link. The token
itself carries authentication and tenant scope.

### 4b. `fleet/urls.py`

```python
path('documents/<int:pk>/download/signed/', views.document_download_signed, name='document_download_signed'),
```

### 4c. Signed-endpoint tests

```python
class DocumentDownloadSignedTests(DocumentTestCase):
    def _signed_token(self, doc, **overrides):
        payload = {
            'v': 1,
            'doc': doc.pk,
            'company': doc.vehicle.company_id,
            'purpose': 'vehicle_document_download',
            'version': doc.download_token_version,
            'exp': timezone.now().timestamp() + 3600,
        }
        payload.update(overrides)
        return signing.dumps(payload)

    def _signed_url(self, doc, **overrides):
        url = reverse('fleet:document_download_signed', kwargs={'pk': doc.pk})
        return f'{url}?token={self._signed_token(doc, **overrides)}'

    def test_signed_download_works_without_login(self):
        response = self.client.get(self._signed_url(self.doc))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FILE_BYTES, b''.join(response.streaming_content))

    def test_signed_download_rejects_expired_token(self):
        url = self._signed_url(self.doc, exp=timezone.now().timestamp() - 10)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_revoked_token(self):
        url = self._signed_url(self.doc)
        self.doc.revoke_download_links()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_company(self):
        url = self._signed_url(self.doc, company=self.other_company.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_document(self):
        url = self._signed_url(self.doc)
        wrong = reverse('fleet:document_download_signed', kwargs={'pk': self.other_doc.pk})
        response = self.client.get(f'{wrong}?token={url.split("token=", 1)[1]}')
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_tampered_token(self):
        token = self._signed_token(self.doc)
        tampered = (token[:-4] + ('A' if token[-4] != 'A' else 'B') + token[-3:])
        url = reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk})
        response = self.client.get(f'{url}?token={tampered}')
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_missing_token(self):
        url = reverse('fleet:document_download_signed', kwargs={'pk': self.doc.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_purpose(self):
        url = self._signed_url(self.doc, purpose='other')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_rejects_wrong_version(self):
        url = self._signed_url(self.doc, version=999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_signed_download_audits_success_and_denial(self):
        url = self._signed_url(self.doc)
        self.client.get(url)
        self.assertEqual(1, AuditLog.objects.filter(action='DOWNLOAD').count())
        self.client.get(self._signed_url(self.doc, exp=timezone.now().timestamp() - 10))
        self.assertEqual(2, AuditLog.objects.filter(action='DOWNLOAD').count())
```

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.settings.test --verbosity=2
```

### Commit

```
feat(downloads): signed URL download endpoint
```

---

## Task 5 — Rate limiting + security hardening

### 5a. `config/settings/base.py` — `SECURITY_RATE_LIMITS`

Add two download limits (values must match the existing `^\d+/(s|m|h|d)$` shape
enforced by `test_security.py::SecurityRateLimitConfigTests`):

```python
SECURITY_RATE_LIMITS = {
    # ...existing keys...
    'download_per_user': os.environ.get('DOWNLOAD_RATE_LIMIT', '20/h'),
    'download_anon_ip': os.environ.get('DOWNLOAD_ANON_RATE_LIMIT', '10/h'),
}
```

`is_download_rate_limited()` (Task 3) already reads these keys and applies the
built-in `'user_or_ip'` key, so authenticated staff are limited per user and
anonymous signed-link downloads per IP. No `DOWNLOAD_RATE_LIMIT` standalone setting
is needed — env vars feed `SECURITY_RATE_LIMITS` directly, matching the login/upload
pattern.

### 5b. Rate-limit and edge-case tests

```python
@override_settings(SECURITY_RATE_LIMITS={
    'download_per_user': '1/h',
    'download_anon_ip': '1/h',
})
class DocumentDownloadRateLimitTests(DocumentTestCase):
    def setUp(self):
        super().setUp()
        from django.core.cache import cache
        cache.clear()

    def test_session_download_rate_limit_denies_and_audits(self):
        self.client.force_login(self.user)
        first = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(200, first.status_code)
        second = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(403, second.status_code)
        denied = AuditLog.objects.filter(
            action='DOWNLOAD', change_summary__icontains='rate limit exceeded',
        ).count()
        self.assertEqual(1, denied)

    def test_signed_download_rate_limit_denies_anonymous(self):
        url = self._signed_url(self.doc)
        first = self.client.get(url)
        self.assertEqual(200, first.status_code)
        second = self.client.get(url)
        self.assertEqual(403, second.status_code)


class DocumentServeEdgeCaseTests(DocumentTestCase):
    def test_oserror_reading_file_returns_404(self):
        self.client.force_login(self.user)
        with patch('fleet.downloads.default_storage', spec=True):
            from django.core.files.storage import default_storage  # noqa: F401
            storage = default_storage
        name = self.doc.file.name
        with patch.object(self.doc.file.storage, 'open', side_effect=OSError('boom')):
            response = self.client.get(self._download_url(self.doc.pk))
        self.assertEqual(404, response.status_code)
        _ = name
```

Add the required `from unittest.mock import patch` import to the test module header.

Note: the OSError path is also covered by patching `storage.open`; keep this test
simple by patching `VehicleDocument` file storage `open` as shown.

### 5c. `test_security.py` note

`SecurityRateLimitConfigTests` iterates `SECURITY_RATE_LIMITS`; the two new keys
automatically become part of that gate (presence + `^\d+/(s|m|h|d)$` format). No
edit needed.

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_documents fleet.tests.test_security --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.settings.test --verbosity=2
```

### Commit

```
feat(downloads): rate limiting and security hardening for downloads
```

---

## Task 6 — Admin integration

### 6a. `fleet/admin.py`

Add the widget, wire it via `formfield_overrides`, add change-form buttons, the
generate-link admin view, and the company column on `AuditLogAdmin`.

```python
from django import forms
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext as _

from .audit import log_audit


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
```

On `VehicleDocumentAdmin`:

```python
class VehicleDocumentAdmin(TenantAdminMixin, admin.ModelAdmin):
    # ...existing fields...
    formfield_overrides = {
        models.FileField: {'widget': AdminDocumentFileWidget},
    }
    change_form_template = 'admin/fleet/vehicledocument/change_form.html'

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
```

`AuditLogAdmin`: add `'company'` to `list_display` (and optionally `list_filter`).

### 6b. Templates (all under `fleet/templates/`, so the i18n coverage test scans them)

`fleet/templates/admin/fleet/widgets/document_file.html`:

```html
{% load i18n %}
{% if widget.download_url %}
  <p class="file-upload"><a href="{{ widget.download_url }}" class="button">{% translate 'Download document' %}</a></p>
{% endif %}
{% if widget.is_initial %}
  <p class="file-upload"><input type="checkbox" name="{{ widget.checkbox_name }}" id="{{ widget.checkbox_id }}"{% if widget.attrs.disabled %} disabled{% endif %}>
  <label for="{{ widget.checkbox_id }}">{% translate 'Clear' %}</label></p>
{% endif %}
<input type="{{ widget.type }}" name="{{ widget.name }}"{% include "django/forms/widgets/attrs.html" %}>
```

`fleet/templates/admin/fleet/vehicledocument/change_form.html`:

```html
{% extends "admin/change_form.html" %}
{% block submit_buttons_bottom %}{% include "admin/fleet/vehicledocument/submit_line.html" %}{% endblock %}
```

`fleet/templates/admin/fleet/vehicledocument/submit_line.html`:

```html
{% load i18n admin_urls %}
<div class="submit-row">
  <input type="submit" value="{% translate 'Generate temporary download link' %}" name="_generate_link">
  <input type="submit" value="{% translate 'Revoke temporary links' %}" name="_revoke_links">
  {% if show_save %}<input type="submit" value="{% translate 'Save' %}" class="default" name="_save">{% endif %}
  {% if show_delete_link %}<p class="deletelink-box"><a href="{% url opts|admin_urlname:'delete' original.pk|admin_urlquote %}" class="deletelink">{% translate "Delete" %}</a></p>{% endif %}
</div>
```

`fleet/templates/admin/fleet/vehicledocument/generate_link.html`:

```html
{% extends "admin/base_site.html" %}
{% block content %}
<h1>{% translate 'Generate temporary download link' %}</h1>
<p>{{ doc }}</p>
<form method="post">{% csrf_token %}
  <fieldset class="module aligned">
    <div class="form-row">
      <label for="id_ttl">{% translate 'Link TTL' %}:</label>
      <select name="ttl" id="id_ttl">
        <option value="15m">{% translate '15 minutes' %}</option>
        <option value="1h" selected>{% translate '1 hour' %}</option>
        <option value="24h">{% translate '24 hours' %}</option>
      </select>
    </div>
  </fieldset>
  <div class="submit-row"><input type="submit" value="{% translate 'Generate' %}" class="default"></div>
</form>
{% endblock %}
```

`fleet/templates/admin/fleet/vehicledocument/download_link.html`:

```html
{% extends "admin/base_site.html" %}
{% block content %}
<h1>{% translate 'Temporary download link' %}</h1>
<p>{{ doc }}</p>
<div class="form-row" style="margin:1em 0">
  <input id="download-link" type="text" value="{{ download_url }}" readonly style="width:100%">
  <button type="button" onclick="navigator.clipboard.writeText(document.getElementById('download-link').value)">{% translate 'Copy link' %}</button>
</div>
<p><a href="{% url 'admin:fleet_vehicledocument_change' doc.pk %}">{% translate 'Back' %}</a></p>
{% endblock %}
```

### 6c. Admin tests

```python
from django.test import Client


class AdminDocumentDownloadTests(DocumentTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_change_form_offers_generate_and_revoke(self):
        url = reverse('admin:fleet_vehicledocument_change', args=[self.doc.pk])
        response = self.client.get(url)
        self.assertContains(response, 'Generate temporary download link')
        self.assertContains(response, 'Revoke temporary links')

    def test_change_form_hides_raw_media_url(self):
        url = reverse('admin:fleet_vehicledocument_change', args=[self.doc.pk])
        response = self.client.get(url)
        self.assertNotIn(self.doc.file.url, response.content.decode())

    def test_generate_link_requires_staff(self):
        anonymous = Client()
        url = reverse('admin:fleet_vehicledocument_generate_link', args=[self.doc.pk])
        response = anonymous.get(url)
        self.assertIn(response.status_code, (302, 403))

    def test_generate_link_returns_absolute_url(self):
        url = reverse('admin:fleet_vehicledocument_generate_link', args=[self.doc.pk])
        response = self.client.post(url, {'ttl': '1h'})
        self.assertEqual(200, response.status_code)
        self.assertIn('http://testserver', response.content.decode())

    def test_revoke_links_from_change_form_increments_version(self):
        url = reverse('admin:fleet_vehicledocument_change', args=[self.doc.pk])
        self.client.post(url, {'_revoke_links': '1'})
        self.doc.refresh_from_db()
        self.assertEqual(2, self.doc.download_token_version)

    def test_auditlog_admin_lists_company(self):
        from fleet.admin import AuditLogAdmin
        self.assertIn('company', AuditLogAdmin.list_display)
```

### Verification

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.settings.test --verbosity=2
```

### Commit

```
feat(admin): authenticated document downloads in admin
```

---

## Task 7 — File lifecycle, `original_filename`, localization

### 7a. Capture `original_filename` in upload views — `fleet/views.py`

In both `document_create` and `document_edit`, after `form.save(commit=False)` (or
the equivalent current pattern), insert:

```python
if 'file' in request.FILES:
    doc.original_filename = request.FILES['file'].name
```

For edit, only overwrite when a new file is uploaded (existing `original_filename`
is preserved otherwise).

### 7b. Add the new translatable strings to all three catalogs

Append the following entries to each of
`locale/{en,fr,ar}/LC_MESSAGES/django.po` (order irrelevant; polib/msgfmt sort).
`en` msgstr stays empty (canonical source); `fr`/`ar` get translations. Verify at
execution time with the Task 1 gate whether `Save`/`Delete` (used by
`submit_line.html`) are already present; add them if not.

| msgid | fr msgstr | ar msgstr |
|---|---|---|
| `Download denied: invalid or expired token` | `Téléchargement refusé : jeton invalide ou expiré` | `تم رفض التحميل: الرمز غير صالح أو منتهي الصلاحية` |
| `Download denied: token does not match document` | `Téléchargement refusé : le jeton ne correspond pas au document` | `تم رفض التحميل: الرمز لا يطابق المستند` |
| `Download denied: rate limit exceeded` | `Téléchargement refusé : limite de débit dépassée` | `تم رفض التحميل: تم تجاوز الحد الأقصى للمعدل` |
| `Document downloaded` | `Document téléchargé` | `تم تحميل المستند` |
| `Document downloaded via signed link` | `Document téléchargé via un lien signé` | `تم تحميل المستند عبر رابط موقّع` |
| `Original filename` | `Nom de fichier d'origine` | `اسم الملف الأصلي` |
| `Download token version` | `Version du jeton de téléchargement` | `إصدار رمز التحميل` |
| `Generate temporary download link` | `Générer un lien de téléchargement temporaire` | `إنشاء رابط تحميل مؤقت` |
| `Revoke temporary links` | `Révoquer les liens temporaires` | `إبطال الروابط المؤقتة` |
| `Temporary links revoked` | `Liens temporaires révoqués` | `تم إبطال الروابط المؤقتة` |
| `Temporary download link` | `Lien de téléchargement temporaire` | `رابط تحميل مؤقت` |
| `Link TTL` | `Durée de validité du lien` | `مدة صلاحية الرابط` |
| `15 minutes` | `15 minutes` | `١٥ دقيقة` |
| `1 hour` | `1 heure` | `ساعة واحدة` |
| `24 hours` | `24 heures` | `٢٤ ساعة` |
| `Generate` | `Générer` | `إنشاء` |
| `Copy link` | `Copier le lien` | `نسخ الرابط` |
| `Back` | `Retour` | `رجوع` |
| `Download document` | `Télécharger le document` | `تحميل المستند` |
| `Clear` | `Effacer` | `مسح` |

Add only to `fleet`'s `django.po`/`django.mo`. `Download` (AuditLog choice) already
exists in all three catalogs.

### 7c. Regenerate `.mo` via polib

```powershell
venv\Scripts\python.exe -c "import polib; [polib.pofile('locale/%s/LC_MESSAGES/django.po' % l).save_as_mofile('locale/%s/LC_MESSAGES/django.mo' % l) for l in ('en','fr','ar')]"
```

### Verification — the hardened gate must stay green

```powershell
venv\Scripts\python.exe -m manage test fleet.tests.test_i18n_catalog --settings=config.test_settings --verbosity=2
venv\Scripts\python.exe -m manage test fleet.tests.test_documents --settings=config.test_settings --verbosity=2
```

If the coverage tests report any template/python string missing (e.g. `Save`,
`Delete`), add it (en empty msgstr, fr/ar translations) and re-run.

### Commit

```
feat(downloads): file lifecycle cleanup and localization
```

---

## Task 8 — Docs, env examples, final verification gate

### 8a. `docs/deployment.md`

- Remove the public `/media/` nginx `location` block.
- Add a "Document downloads" section: files are private; all downloads go through
  `fleet:document_download` (staff, tenant-scoped) or `fleet:document_download_signed`
  (temporary signed links); tokens expire (default `DOCUMENT_SIGNED_URL_TTL`, 24 h),
  are revocable per document, and are rate-limited (`download_per_user` / `download_anon_ip`
  in `SECURITY_RATE_LIMITS`); every attempt is written to `AuditLog`; physical files
  are removed on replace/delete.

### 8b. `.env.example` and `.env.production.example`

Add (with a one-line comment):

```
# Signed download link TTL in seconds (default 86400)
DOCUMENT_SIGNED_URL_TTL=86400
# Download rate limits (format: N/(s|m|h|d))
DOWNLOAD_RATE_LIMIT=20/h
DOWNLOAD_ANON_RATE_LIMIT=10/h
```

### 8c. Final verification gate (all commands from repo root)

```powershell
venv\Scripts\python.exe -m ruff check .
venv\Scripts\python.exe -m bandit -r fleet config -q -ll
venv\Scripts\python.exe -m pip_audit -r requirements.txt -r requirements-dev.txt
venv\Scripts\python.exe -m manage makemigrations --check --dry-run --settings=config.test_settings
venv\Scripts\python.exe -m manage test fleet --settings=config.test_settings --verbosity=1
venv\Scripts\python.exe -m manage test fleet --settings=config.settings.test --verbosity=1
$env:SECRET_KEY='ci-only-9Zx3vQ7wT2mR8pN5cL6bK1hD4fG0jS7aY3uE8iW'; $env:DEBUG='False'; $env:ALLOWED_HOSTS='localhost'; $env:CSRF_TRUSTED_ORIGINS='https://localhost'; $env:DATABASE_URL='sqlite:///db.sqlite3'; venv\Scripts\python.exe -m manage check --deploy --settings=config.settings.production
```

All must pass. Then tag the release candidate:

```powershell
git tag v1.0.0-rc1
```

### Commit

```
docs: private download deployment notes and env examples
```

---

## Commit sequence (9 commits)

1. `chore: bootstrap Vroom repository at RC1 baseline`
2. `test(i18n): harden catalog quality gates and fix fr plural forms`
3. `feat(downloads): add VehicleDocument token fields and AuditLog company`
4. `feat(downloads): private document download service and session endpoint`
5. `feat(downloads): signed URL download endpoint`
6. `feat(downloads): rate limiting and security hardening for downloads`
7. `feat(admin): authenticated document downloads in admin`
8. `feat(downloads): file lifecycle cleanup and localization`
9. `docs: private download deployment notes and env examples`

After commit 9: tag `v1.0.0-rc1`.

## Known deviations (approved)

- `AuditLog.company` uses `on_delete=SET_NULL` so audit history survives company
  deletion, rather than `CASCADE`.
- Download rate limiting intentionally uses direct `is_ratelimited()` calls (not the
  codebase's `block=True` decorator pattern) so denials can be audited inside the
  view before returning 403.
- `en` catalog entries are left empty (canonical source) except the 4 pre-existing
  deliberate identity overrides; the hardened gate documents rather than forbids them.
