# Vroom — Post-Deployment Validation

Run **after** every deploy to a production target (first release and each
upgrade). Failures here mean the deploy did not land and rollback applies
(`docs/deployment/hostinger-business.md` §8).

For each row, record the observed value in the notes column.

## Functional

| # | Check | Pass criteria | Notes |
|---|---|---|---|
| F1 | Login | Existing staff user logs in from the login page | |
| F2 | Create customer/driver | A driver record is saved and visible | |
| F3 | Create vehicle | A vehicle record is saved and visible | |
| F4 | Create booking | A booking for an available vehicle is saved | |
| F5 | Return vehicle | Marking a booking returned updates status and sets `actual_return` | |
| F6 | Create financial transaction | A payment against a booking is recorded | |
| F7 | Upload document | A document uploads to a vehicle; file lands in `MEDIA_ROOT` | |
| F8 | Download private document | Staff download succeeds; signed-link download (no login) succeeds | |
| F9 | Booking exclusivity | Overlapping booking for the same vehicle is rejected | |

## Security

| # | Check | Pass criteria | Notes |
|---|---|---|---|
| S1 | `/media/` not served | Direct `https://<domain>/media/...` returns 403/404 | |
| S2 | CSRF | A forged cross-site POST is rejected | |
| S3 | Rate limiting | >5 failed logins from one IP throttles only that IP | |
| S4 | HTTPS-only | HTTP redirects to HTTPS; no loop | |
| S5 | Tenant isolation | A record of company A is not reachable as company B | |
| S6 | Audit log | Logins/uploads/downloads write `AuditLog` rows with the real client IP | |

## Performance (soft targets — record actuals)

| # | Check | Target | Actual |
|---|---|---|---|
| P1 | Home page | < 2 s | |
| P2 | Dashboard | < 3 s | |
| P3 | `/health/` | < 200 ms | |
| P4 | Static asset TTFB | served by the host (not proxied to the app) | |

## Data

| # | Check | Pass criteria | Notes |
|---|---|---|---|
| D1 | Audit log writes | `AuditLog` rows appear for recent activity | |
| D2 | Transactions | A multi-step operation (e.g. booking + payment) leaves consistent rows; no partial writes | |
| D3 | Migrations applied | `showmigrations` shows all `[X]`; no drift | |
| D4 | Backup runs | `scripts/backup.sh` produced a fresh timestamped dump | |
| D5 | Restore proven | A restore was executed successfully in a scratch environment within the last quarter | |

## Sign-off

| Role | Date | Result |
|---|---|---|
| Deployer |  |  |
| Principal Engineer |  |  |
