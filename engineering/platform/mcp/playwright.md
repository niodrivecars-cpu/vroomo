# playwright MCP

Browser automation via `@playwright/mcp` for E2E and visual verification of the
Bootstrap RTL UI.

## Prerequisites
- `npx`/`node` present (yes on this machine).
- `BROWSER=chromium` set in `opencode.jsonc` environment.
- First run may download Chromium (`npx playwright install chromium`).

## When to use
- Verifying a form flow end-to-end (booking create/edit, login, download).
- Checking RTL rendering, pagination mirroring, and i18n locale switching.
- Reproducing a user-reported UI bug with a scripted browser session.
- Accessibility spot-checks (labels, keyboard nav) before the a11y audit.

## When NOT to use
- Server-side logic, business rules, or DB behavior — that's the Django test
  suite (and the MySQL dev DB).
- Static code questions — read the repo.
- Full load testing — that's k6, not the browser.

## Call order
1. Start a local dev server (`manage.py runserver`).
2. Point playwright MCP at it.
3. Walk the happy path first, then edge cases (expired/tampered download,
   cross-tenant access, rate-limit feedback).
4. Assert DOM state (visibility, error blocks, locale) — not just navigation.

## Common mistakes
- Testing with the wrong locale/tenant context (each tenant sees its own data).
- Forgetting the dev server isn't running.
- Relying on browser E2E for things the unit suite covers (slow, flaky) — use it
  for integration-shaped flows only.

## Example
```
Navigate to /login → fill tenant A creds → submit → expect dashboard →
book a vehicle → confirm success redirect (302) → logout.
```
