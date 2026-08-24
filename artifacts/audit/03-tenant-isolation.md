# Phase 2 — Multi-Tenant Isolation Audit

## Tenancy model

- **Tenant = Company** model (`fleet/models.py` L105)
- **Binding = UserProfile** with 1:1 FK to Django `User` and FK to `Company` (`fleet/models.py` L124-130)
- **Middleware = CompanyMiddleware** (`fleet/middleware.py` L48-63): sets `request.company = request.user.userprofile.company` for all authenticated non-superusers
- **Enforcement = view-layer** via `tenant_objects()` and `tenant_get_object_or_404()` helpers (`fleet/views.py` L43-48)

All 9 entity models have a `company` FK added in migration `0005` and made non-nullable in `0007`.

## Tenant isolation matrix

| Surface | Mechanism | Evidence | Status |
|---|---|---|---|
| HTTP views | `tenant_objects()` / `tenant_get_object_or_404()` | `views.py` L43-48, 50+ call sites | VERIFIED |
| Object list views | `tenant_objects(request, Model)` scopes by `request.company` | e.g. `vehicle_list` L84: `tenant_objects(request, Vehicle)` | VERIFIED |
| Object detail/edit/delete | `tenant_get_object_or_404(request, Model, pk=pk)` | e.g. `vehicle_detail` L109 | VERIFIED |
| Object creation | Form `save(commit=False)` + `obj.company = request.company` | `vehicle_create` L90-92, `booking_create` L221 | VERIFIED |
| Forms | `company` passed to form `__init__`, queryset filtered | `forms.py` L15-16: `Vehicle.objects.for_company(company)` | VERIFIED |
| Admin | `TenantAdminMixin` filters by `request.user.userprofile.company` (non-superuser) | `admin.py` L8-23 | VERIFIED |
| Object lookup (FK) | `tenant_get_object_or_404` includes `company=request.company` in filter | L46 | VERIFIED |

## Tests

- `test_idor.py`: 35 tests — TenantIsolationReadTests, TenantIsolationWriteTests, TenantIsolationCreateTests, TenantIsolationFormTests
- `test_authz.py`: 291 lines — authorization tests
- k6 `tenant-isolation.js`: load test with Tenant A/B data; asserts `data_B_not_in_A`
- k6 `document-download.js`: cross-tenant document download attempts (signed URL + authenticated)

## Findings

### FINDING T1 — Object-level authorization is enforced

**Evidence:** `test_security.py` `SecurityHeadersTest`, `test_idor.py` all pass. 35 IDOR tests cover read/write/create for all 7 entity types.

**Status:** VERIFIED — PASS

Tenant A cannot read, write, update, or delete Tenant B's data through standard views.

### FINDING T2 — Cross-tenant document download attempts are denied

**Evidence:** `test_documents.py` L1-380, `document-download.js` k6 test.

**Status:** VERIFIED — PASS

Signed URL verification includes company check. Authenticated download uses `tenant_get_object_or_404`.

### FINDING T3 — Admin is tenant-scoped for non-superusers

**Evidence:** `admin.py` L8-23 (TenantAdminMixin), `test_views.py` (admin tests).

**Status:** VERIFIED — PASS

Non-superuser admin queries filtered by `request.user.userprofile.company`. Superusers see all (by design).

### FINDING T4 — No `all_objects` / unscoped manager bypass found

**Evidence:** `models.py` L46-56 — only one manager (`objects = TenantScopedManager()`). No `all_objects`, no `unscoped()`.

**Status:** VERIFIED

The spec warned about `all_objects` bypasses. No such manager exists. `TenantScopedManager.for_company()` is the only queryset entry point used in views.

### FINDING T5 — Bulk operations are not exposed as endpoints

**Evidence:** `fleet/urls.py` — no bulk_create/bulk_update URLs. All mutations are single-object form posts.

**Status:** VERIFIED — PASS (no risk)

## Gates

| Gate | Status |
|---|---|
| Cross-tenant read | PASS |
| Cross-tenant write | PASS |
| Cross-tenant delete | PASS |
| Cross-tenant file access | PASS |
| Cross-tenant API access | N/A (no REST API — web UI only) |
| Cross-tenant async access | N/A (no Celery) |
| Cross-tenant cache access | PASS (no tenant-specific cache keys; health probe key is static) |
