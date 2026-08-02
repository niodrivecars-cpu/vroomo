# Django — Overview

Reference for building Django services on this platform.

## What it is
Vroom is a multi-tenant Django service: `fleet` app + `config` project settings.
The app is where domain logic lives; the project is wiring (settings, middleware,
WSGI/ASGI). Shared settings split across `base.py`, `test.py`, `production.py`.

## How it fits
- **Settings:** `base` (shared) → `test` (SQLite in-memory, MD5 hashers,
  InMemoryStorage) → `production` (Postgres, secure cookies, security headers).
- **App layout:** views (thin), security helpers (`fleet/security.py`),
  audit (`fleet/audit.py`), middleware (proxy-aware IP), management commands
  (`loadtest_seed`), tests under `fleet/tests/`.
- **DB:** SQLite for dev/tests, Postgres for production (ADR 0001).

## Where it's heading
API expansion and mobile apps remain roadmap items (see `platform/ROADMAP.md`).
