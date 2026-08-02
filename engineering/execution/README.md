# Execution

How work happens on the platform: pipelines, gates, playbooks, runbooks,
checklists, and templates.

## Contents
- `pipelines/` — ordered sequences (review, release).
- `gates/` — pass/fail thresholds per concern (release, security, migration,
  performance).
- `playbooks/` — procedural guides for events (release, incident).
- `runbooks/` — operator procedures (deploy, backup/restore).
- `checklists/` — quick verification lists.
- `templates/` — reusable scaffolds (task, meeting).

## Core idea
Execution is repeatable and evidence-producing: every procedure that ends in
"PASS" should leave a record in `evidence/`.
