# Redis — Overview

Caching and rate-limit backends (planned).

## What it is
Planned infrastructure for caching and durable rate limiting at production
scale. Not yet used in Vroom (RC1 uses in-process/Django-level rate limiting).

## Why planned
- Cacheable per-request work: catalog lookups, signed-URL derivation.
- A shared rate-limit store if multiple gunicorn workers need coordinated
  limits.

## Status
Not configured. This folder is a placeholder for when caching is added;
document the exact cache keys, invalidation, and failure behavior here.
