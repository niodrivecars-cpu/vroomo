# i18n Knowledge — Best Practices

- **Wrap all user-facing strings** in `gettext`/`{% trans %}` from the start;
  retrofitting is painful.
- **Recompile after every `.po` change** (`compilemessages`) and let the tests
  verify.
- **Test catalog integrity automatically** — parse, completeness, placeholders,
  `.mo`/`.po` sync, headers, plural forms are all enforced by `test_i18n_catalog`.
- **Design for RTL from the start** — mirrored pagination and LTR value isolation
  are layout contracts, not afterthoughts.
- **Keep placeholder names stable** across locales so translations can't drift.
