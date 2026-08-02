# Performance — Overview

What makes the app slow and how the platform keeps releases fast.

## What it is
Performance is measured, not assumed. Every release has a load gate with
thresholds (see `execution/gates/performance-gate.md`).

## How it fits
- k6 smoke + attack profiles assert p95 latency and error budgets.
- `knowledge/load-testing/` documents the methodology.
- N+1 queries, missing indexes, and un-indexed tenant filters are the usual
  suspects in Django.

## Where it's heading
Production-data-driven tuning (real dashboards, SLOs) after observability lands.
