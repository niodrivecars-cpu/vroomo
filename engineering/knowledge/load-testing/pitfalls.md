# Load Testing Knowledge — Pitfalls

- **Running against a dirty DB/cache** — prior bookings shift results and can
  hide or fake conflicts. Fresh state only.
- **Reading mean, not p95** — the tail is what users feel.
- **Download VUs colliding on one user** — under `ATTACK=1` the VU→user mapping
  can place both download VUs on the same account, blowing the 20/h limit and
  producing 403s that look like a regression. `authDownloads` iterations are
  capped at 9 (2 VUs × 9 = 18 < 20) for this reason.
- **Mistaking the SQLite lock artifact for a real failure.** HTTP 200 with no
  error markup = swallowed `database is locked` (dev only). Distinguish via
  `isSqliteLockArtifact` before treating a check as failed.
- **Adding scenarios without re-checking `__VU % users.length`** — extra
  scenarios shift VU numbering and can change which users download.
