# Mission

The Engineering Platform exists to make engineering **repeatable and provable**
across products. It is not documentation about Vroom — Vroom is the first tenant.
Nio Drive and future products inherit the same discipline without restructuring
the platform.

## What we guarantee
1. **One source of truth per concept.** The canonical model, glossary, and
   ontology define every term once; everything else references, never redefines.
2. **Evidence over assertion.** A claim that is not backed by a test, scan,
   measurement, or signed review is a starting point, not a conclusion.
3. **Traceability.** Every rule is linked Rule → Invariant → Code → Test →
   Evidence. A broken link is a recorded, owned gap.
4. **Validation before implementation.** A policy is validated and approved
   before it is built (Phase 2A: Business Rule Validation & Ownership).
5. **Self-governance.** The platform reviews its own agents, docs, and gates
   (`meta/`), and models its own failure modes (`failure-model.md`), so it does
   not drift into bureaucracy.

## What we refuse
- Undocumented decisions (ADR/RFC are required by `governance/DECISION_PROCESS.md`).
- Untraced rules (a rule without a test row is debt).
- Silent gaps (every 🔲/🧾 has an owner and a phase).
- Evidence without confidence (a manifest is a record, not a verdict).
- Duplicated truth (a second definition of the same concept is drift, not depth).
- Platform growth for its own sake (simplicity is an asset — `principles.md`).

## Scope boundary
The kernel governs **how the platform and its projects are engineered**. It does
not define product business rules (that is `domain/model/`) nor product
standards (that is `governance/`). When the platform is reused for a new
product, the kernel does not change; only `projects/<name>/` is added.
