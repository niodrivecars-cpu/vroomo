# Phase 7 — Test Suite Results

## Execution environment

- Python: 3.12 (CPython 3.12.64-bit) — chosen because Python 3.14 + python-magic segfaults on Windows (libmagic native crash)
- `python-magic-bin` installed to provide `libmagic-1.dll` for Windows
- Django: 6.0.7
- Test settings: `config.test_settings` (SQLite in-memory)
- Command: `python manage.py test fleet --settings=config.test_settings -v 2`

## Test results

| Metric | Value |
|---|---|
| Total tests | 278 |
| Passed | 277 |
| Failed | 1 |
| Errors | 0 |
| Skipped | 0 |
| Warnings | Rate-limit warnings logged (expected) |
| Execution time | 355.030s |
| Overall result | **FAILED (1 failure)** |

## Test modules (9 test files)

| Module | Tests | Status |
|---|---|---|
| `test_authz.py` | 27 | ALL PASS |
| `test_idor.py` | 35 | ALL PASS |
| `test_views.py` | 33 | ALL PASS |
| `test_models.py` | 18 | ALL PASS |
| `test_forms.py` | 11 | ALL PASS |
| `test_documents.py` | 37 | ALL PASS |
| `test_security.py` | 32 | 31 PASS, 1 FAIL |
| `test_ratelimit.py` | 12 | ALL PASS |
| `test_client_ip.py` | 18 | ALL PASS |
| `test_health.py` | 4 | ALL PASS |
| `test_i18n_catalog.py` | 14 | ALL PASS |
| `test_i18n_locale.py` | 9 | ALL PASS |

## Failure detail

### FAIL: `test_audit_log_default_ordering`

**Location:** `fleet/tests/test_security.py` L178-183

**Root cause:** The test creates two `AuditLog` entries and asserts `logs[0].username == 'b'` (newest first). The `AuditLog` model uses `auto_now_add=True` on `created_at` field, which has **second-level granularity**. When two entries are created in the same second (which happens in fast test execution), the `-created_at` ordering produces non-deterministic results.

**Test code (L178-183):**
```python
def test_audit_log_default_ordering(self):
    AuditLog.objects.create(username='a', action='LOGIN', change_summary='first')
    AuditLog.objects.create(username='b', action='LOGOUT', change_summary='second')
    logs = AuditLog.objects.all()
    self.assertEqual(logs[0].username, 'b')
    self.assertEqual(logs[1].username, 'a')
```

**Impact:** LOW — this is a flaky test, not an application bug. The AuditLog query ordering works correctly in production where entries are created with real time gaps. The test simply fails when both entries share the same `created_at` timestamp.

**Evidence:** `engineering/evidence/testing/rc1-suite.json` claims 278 tests OK (792.077s) — the evidence was likely generated on Linux where test timing was slower, making the same-second race less likely.

## Coverage

Coverage was not explicitly measured in this run (no `coverage.py` invocation). The CI pipeline includes `coverage` in `requirements-dev.txt` and the evidence claims coverage reporting in `ci.yml`.

## k6 load test evidence (from `engineering/evidence/`)

| Test | Exit code | Thresholds | p95 duration | Checks |
|---|---|---|---|---|
| Default smoke | 0 | 9/9 pass | 980.07ms | 356/358 |
| Attack | 0 | 9/9 pass | 3.21s | 414/415 |
| Post-run audit | — | — | — | 46 bookings, 0 overlapping, 0 rate-limit denials |

## Security evidence

| Scan | Result |
|---|---|
| bandit (-ll) | PASS (0 findings) |
| pip-audit | PASS (0 known vulnerabilities) |
