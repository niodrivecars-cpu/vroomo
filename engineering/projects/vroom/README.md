# Vroom — Fleet Management SaaS

Vroom is the first product built on the Engineering Platform (`engineering/`).
It is a multi-tenant fleet management SaaS (Arabic RTL, i18n ar/fr/en).

## Status
- **RC1 approved** — commit `19a8d2f` tagged `v1.0.0-rc1` (annotated).
- RC1 evidence: `docs/releases/v1.0.0-rc1/` (verification, release report,
  k6 outputs + summaries).
- Structured manifests: `engineering/evidence/releases/v1.0.0-rc1.json`.
- Roadmap: RC1 done → Business Rules Review (Phase 2) → Observability (Phase 3)
  → Push/Merge + v1.0.0 + Pilot. See `engineering/platform/ROADMAP.md`.

## How to work on Vroom
1. Read `engineering/knowledge/` for Django/Postgres/security/performance/test
   context and the business knowledge (`knowledge/business/`).
2. Check `engineering/domain/` for business rules and invariants before touching
   `fleet/models.py`.
3. Reuse `engineering/patterns/` (multi-tenant, audit, rbac, signed-download,
   service-layer) instead of inventing new structures.
4. Run the gates (`engineering/execution/gates/`) before release claims.

## Where things live
- Source: `fleet/`, `config/`, `tests/`, `templates/`, `docs/`.
- Platform (how we build): `engineering/platform/`.
- Decisions: `engineering/governance/` (ADRs 0001–0005).
- Evidence: `engineering/evidence/`.
