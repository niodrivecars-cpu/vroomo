# Fleet — Test Matrix

| # | Case | Test | Location |
|---|---|---|---|
| F1 | Every entity created with company | exists | `fleet/tests/` (model tests) |
| F2 | Cross-tenant read/write blocked | exists | `fleet/tests/test_views.py` (IDOR) |
| F2 | Isolation under load: 0 violations | exists | k6 `tenant_isolation_violation == 0` |
| F3 | Download signed/expired/tampered | exists | `fleet/tests/test_views.py` |
| F3 | Cross-tenant download → 404 | exists | `fleet/tests/` + k6 `dl-cross-tenant` |
| F4 | Revoked link stops working | exists | `fleet/tests/` (revoke) |
| F5 | Superseded file deleted best-effort | needed | `fleet/tests/` |
| F6 | Unique plate / CIN enforced | exists | model tests |
| — | Expired doc blocks rental? | open (policy) | Business Rules Review |
| — | Maintenance due (km OR date) | needed | `fleet/tests/` |
| — | Violation overdue/paid derivation | needed | `fleet/tests/` |
| — | Violation auto-link to active booking driver | exists | `test_violation_create_auto_links_driver_from_active_booking` |

## Coverage status
Security invariants F1–F4 are well covered. Derived-state rules and file-hygiene
(F5) need reference tests — Phase 2.
