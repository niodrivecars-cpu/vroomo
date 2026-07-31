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
