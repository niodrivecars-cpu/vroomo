# Verification

How the platform proves correctness. Verification is a first-class layer: a
claim without a recorded artifact is not verified.

## Files
- `verification-standard.md` — what "verified" means and the evidence tiers.
- `confidence-model.md` — how much to trust each type of evidence.
- `risk-matrix.md` — categorizing and responding to residual risk.
- `review-pipeline.md` — the human-in-the-loop part of verification.
- `traceability/` — Business Traceability Gate snapshots (rule → test → evidence).
- `completeness/` — Business Completeness Gate matrices (entity → six slots).

## The core idea
Evidence tiers (see standard) map to confidence (see confidence model) which
maps to risk (see risk matrix). A release verdict is the intersection of all
three: enough evidence, enough confidence, and acceptable residual risk for the
release stage.
