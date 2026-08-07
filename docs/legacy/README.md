# Legacy / reference artifacts

Preserved artifacts that are no longer active but document prior decisions or
alternative deployment paths. See `docs/platform-support.md` for which paths
are current.

| File | What it is | Why it's here |
|---|---|---|
| `cd-vps-reference.yml` | GitHub Actions CD workflow (tag `v*` → SSH → `scripts/deploy.sh` → `/health/` → rollback) | Retired when production moved to Hostinger shared hosting (hPanel auto-deploy + `scripts/deploy-hostinger.sh`). Kept as the VPS reference layout. |
