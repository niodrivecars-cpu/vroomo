# Evidence

The machine-verifiable proof trail. Append-only artifacts keyed by gate and
release. The mutable entry point is `index.json`.

## Structure
```
evidence/
  schema.json               JSON Schema for manifests
  index.json                The index (single mutable file)
  releases/<version>.json   Release manifests (append-only)
  security/                 Security gate artifacts (scans)
  performance/              Load gate artifacts (k6)
  testing/                  Test suite artifacts
```

## Rules
- Evidence files are append-only. Corrections add a new entry + supersedes
  pointer (see `platform/VERSIONING.md`).
- Every artifact is timestamped and references the commit it ran against.
- `index.json` is regenerated, never hand-maintained (Phase 4 automation).
