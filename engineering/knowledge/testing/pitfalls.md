# Testing — Pitfalls

- **Running tests against the default DB.** Always `--settings=config.test_settings`
  or tests hit dev state. The suite hangs/behaves oddly when the wrong settings
  are used.
- **Heavy RAM on in-memory SQLite.** The full suite swaps on low-RAM machines
  (a full run took 792s locally with ~1 GB free). Run it when resources are
  available, not mid-session.
- **Testing only the happy path.** Security flows (cross-tenant, expired,
  tampered) must be tested as first-class cases.
- **Asserting on rendered markup that RTL/i18n changes.** Error-block detection
  relies on `invalid-feedback` markup; locale changes can break it — keep tests
  on stable contracts.
- **No load evidence for concurrency claims.** Unit tests alone don't prove
  exclusivity under concurrent VUs; add a k6 assertion.
