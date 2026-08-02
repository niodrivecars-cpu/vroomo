# i18n Knowledge

Internationalization and localization for Vroom: ar, fr, en.

## What it is
- Django i18n with `.po`/`.mo` catalogs under `locale/`.
- Locales: Arabic (`ar`), French (`fr`), English (`en`).
- Full RTL support (Arabic) including mirrored pagination and LTR isolation of
  values embedded in RTL text.

## How it fits
- All user-facing strings go through `gettext`/templates.
- `compilemessages` (gettext `msgfmt`) produces `.mo` from `.po`.
- Catalog integrity is enforced by tests: `test_i18n_catalog` checks parsing,
  completeness, placeholder consistency, `.mo`/`.po` sync, and header validity.

## Where it's heading
Full CSP (which affects locale switching), more locales as the pilot grows.
