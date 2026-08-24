# Phase 1 — Architecture Verification

## Overview

Comparing actual repository structure against the Vroom domain model and engineering evidence.

## Verified architecture

The Vroom application is a **single-Django-app, multi-tenant (company-scoped) B2B fleet management system** with a web UI only (no REST API). The domain model is:

- **Company** = tenant (isolation boundary)
- **UserProfile** = binds Django User to Company (1:1)
- **Vehicle** = rentable asset (license plate unique globally)
- **VehicleDocument** = private expiring documents (signed-URL downloads)
- **Driver** = driver record (CIN unique globally)
- **Booking** = reservation/rental window (overlap prevention at view layer)
- **Maintenance** = service records
- **Violation** = traffic violations (auto-links to active booking driver)
- **AuditLog** = tenant-scoped action trail

Multi-tenancy is enforced via:
1. **TenantScopedModel** base class (all entities have `company` FK)
2. **TenantScopedManager** with `for_company()` method
3. **CompanyMiddleware** sets `request.company` on every authenticated request
4. **View-layer helper functions** `tenant_objects()` and `tenant_get_object_or_404()` that scope all queries to `request.company`
5. **TenantAdminMixin** scopes admin queries for non-superusers

## Claims vs. Evidence

### Claim: Multi-tenant isolation is enforced

**Evidence:** `fleet/models.py` L46-56 (TenantScopedManager, TenantScopedModel), `fleet/middleware.py` L48-63 (CompanyMiddleware), `fleet/views.py` L43-48 (tenant_objects, tenant_get_object_or_404).

**Status:** VERIFIED

All views call `tenant_objects(request, Model)` (which calls `Model.objects.for_company(request.company)`) or `tenant_get_object_or_404(request, Model, pk=pk)` (which passes `company=request.company` as a filter). The k6 tenant-isolation tests and 35 unit tests in `test_idor.py` confirm cross-tenant access is denied with 404.

### Claim: Booking double-booking prevention

**Evidence:** `fleet/views.py` L212-232 (booking_create with `select_for_update` + overlap check), `fleet/views.py` L253-270 (booking_edit with same pattern).

**Status:** VERIFIED

Uses `transaction.atomic()` + `Vehicle.objects.select_for_update()` + overlap query on `[pickup_date, expected_return)` window with `status__in=['confirmed', 'rented']`. k6 `sameVehicleBooking` test confirms exactly 1 success under 5 VUs racing the same vehicle+window.

### Claim: Document downloads are private with signed URLs

**Evidence:** `fleet/downloads.py` (114 lines), `fleet/views.py` L427-456 (document_download, document_download_signed).

**Status:** VERIFIED

- Authenticated download requires staff + company-scoped lookup
- Signed URL uses Django `signing.dumps` with version, company, purpose, expiry
- `download_token_version` allows revocation (P13)
- MIME type derived from filename, not client-supplied
- Rate limited per-user (20/h) and per-IP anon (10/h)
- All attempts audited to `AuditLog`
