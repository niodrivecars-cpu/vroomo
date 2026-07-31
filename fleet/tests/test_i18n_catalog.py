import re
from pathlib import Path

import polib
from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCALE_DIR = PROJECT_ROOT / 'locale'
LANGS = ('en', 'fr', 'ar')

TRANS_PAT = re.compile(r"{%\s*(?:translate|trans)\s+(['\"])(.*?)\1\s*%}", re.DOTALL)
BLOCK_PAT = re.compile(r"{%\s*blocktrans(?:late)?(?:.*?)%}(.*?){%\s*endblocktrans(?:late)?\s*%}", re.DOTALL)
VAR_PAT = re.compile(r"{{\s*([\w.]+)\s*}}")
PY_PAT = re.compile(r"\b(?:gettext|gettext_lazy|ugettext|ugettext_lazy|_)\((['\"])(.*?)\1\)")
PLACEHOLDER_PAT = re.compile(r"%\((\w+)\)s")


def pofile(lang):
    return polib.pofile(str(LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.po'))


def mofile(lang):
    return polib.mofile(str(LOCALE_DIR / lang / 'LC_MESSAGES' / 'django.mo'))


def active_entries(lang):
    return [e for e in pofile(lang) if not e.obsolete]


class CatalogIntegrityTests(SimpleTestCase):
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
                msgid_vars = set(PLACEHOLDER_PAT.findall(msgid))
                if not msgid_vars:
                    continue
                msgstr_vars = set(PLACEHOLDER_PAT.findall(by_id[msgid].msgstr))
                self.assertEqual(
                    msgid_vars,
                    msgstr_vars,
                    f'[{lang}] placeholder mismatch for {msgid!r}',
                )
