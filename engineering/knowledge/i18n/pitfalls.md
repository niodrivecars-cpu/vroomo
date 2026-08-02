# i18n Knowledge — Pitfalls

- **`msgfmt` missing** → `compilemessages` fails (`CommandError`). Windows dev
  machines lack GNU gettext; CI installs it. Don't hand-edit `.mo`.
- **Stale `.mo` after `.po` edit** → the sync test fails. Always recompile.
- **RTL layout breakage** — mirror pagination, isolate LTR values (phone
  numbers, CINs) inside RTL text or they render reversed/garbled.
- **Non-translated strings** — every Python/template string must be in the `en`
  catalog (`test_every_python_string_is_in_en_catalog`).
- **Locales with different msgid sets** — all locales must share identical
  msgids (`test_all_locales_have_identical_msgid_sets`).
- **Plural forms** — must be valid per locale (`test_plural_forms_are_valid`).
