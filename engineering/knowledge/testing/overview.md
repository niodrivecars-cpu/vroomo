# Testing — Overview

How this platform proves correctness.

## What it is
A layered testing strategy: unit → integration → security → load, each with its
own evidence. Tests run fast on SQLite and truthfully on Postgres.

## How it fits
- 278 tests in `fleet/tests/` covering models, views, rate limits, client IP,
  tenant isolation, downloads, and i18n catalogs.
- k6 load tests assert runtime behavior (concurrency, isolation) that unit tests
  can't.
- Coverage policy: new behavior must ship with tests that fail without the change.

## Where it's heading
Business Rules Review (Phase 2) will convert every business invariant into
executable reference tests (`domain/*/test-matrix.md`).
