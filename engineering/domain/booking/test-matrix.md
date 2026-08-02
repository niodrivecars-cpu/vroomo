# Booking — Test Matrix

Every invariant (B1–B6) mapped to an executable test. This is the contract that
the Business Rules Review phase enforces with reference tests.

| # | Case | Test (exists/needed) | Location |
|---|---|---|---|
| B1 | Same vehicle, same window → 1 success | exists | `tests/performance/booking-workflow.js` (`sameVehicleBooking`), k6 threshold |
| B1 | Adjacent windows → both allowed | needed | `fleet/tests/` |
| B1 | Overlapping windows → blocked | exists | `fleet/tests/test_views.py` |
| B2 | Cross-tenant vehicle reference → rejected | exists | `fleet/tests/test_views.py`, IDOR cases |
| B2 | Booking list scoped to tenant | exists | `fleet/tests/test_views.py` |
| B3 | expected_return <= pickup_date → invalid | needed | `fleet/tests/` |
| B4 | Negative amount/deposit → invalid | needed | `fleet/tests/` |
| B5 | State transitions valid/invalid | needed | `fleet/tests/` |
| B6 | Delete vehicle/driver under booking → blocked | needed | `fleet/tests/` |
| B1+ | Concurrency artifact: SQLite lock 200 is not a phantom failure | exists | `tests/performance/common.js` (`isSqliteLockArtifact`) |

## Coverage status
Unit coverage of B1, B2 exists. B3–B6 need reference tests — tracked in
`platform/ROADMAP.md` Phase 2 (Business Rules Review).
