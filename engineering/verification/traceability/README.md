# Traceability

The run output of the Business Traceability Gate
(`execution/gates/business-traceability-gate.md`): one snapshot per project and
stage, mapping every business rule through

```text
Rule → Invariant → Code → Test → Evidence
```

A broken link is a **gap**, and every gap must be owned and tracked in the
roadmap — the gate passes only when no gap is silent.

## Files
- `<project>-<stage>.md` — the snapshot matrix + gap list.
- Evidence: `evidence/traceability/<project>-<stage>.json`.

## Legend
- ✅ — link present and green.
- ⚠️ — link present but test "needed" (gap, owned).
- ❌ — link missing (gap, must be recorded).
- 🔲 — rule not yet represented (discovery item).
