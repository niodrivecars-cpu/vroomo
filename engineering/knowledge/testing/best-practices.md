# Testing — Best Practices

- **Test against `config.test_settings` always** (SQLite in-memory, MD5 hashers,
  InMemoryStorage) — fast and hermetic.
- **One concern per file.** `test_views`, `test_ratelimit`, `test_client_ip`,
  `test_i18n_catalog` — clear mapping from failure to feature.
- **Security tests are first-class.** IDOR, cross-tenant, expired/tampered
  downloads, rate-limit behavior — each has dedicated cases.
- **Red-green discipline.** Write the failing test first, then the fix.
- **Concurrency gets load proof.** `same_vehicle_booking_success == 1` under
  concurrent VUs is the standard for exclusivity claims.
- **I18n integrity is tested.** `.mo`/`.po` sync, complete msgids, placeholder
  consistency — enforced by `test_i18n_catalog`.
