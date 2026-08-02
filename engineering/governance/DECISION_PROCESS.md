# Decision Process

When to write an ADR vs an RFC, and how each flows.

## ADR — Architecture Decision Record

**Use when:** a decision changes the shape of the system — data model, security
posture, cross-cutting flow, tooling that affects how we build.

**Flow:**
1. Create `adr/NNNN-short-title.md` from the template.
2. Fill context, decision, consequences, and evidence.
3. Reviewer approves. The ADR becomes the reference for that decision.
4. Number sequentially. A superseded ADR is marked, never deleted.

## RFC — Request for Comments

**Use when:** a proposal is large or uncertain enough to need review before
commitment — new capability, roadmap item, major refactor, cross-project change.

**Flow:**
1. Create `rfc/NNNN-short-title.md` from the template.
2. Leave it open for comments; record comments in the document.
3. Decision: **Accepted** (proceed, record the acceptance), **Rejected**
   (record why), **Superseded** (superseded-by pointer).

## Threshold guidance

| Change | Record |
|---|---|
| Bug fix, routine feature | commit + tests |
| New endpoint / business rule in existing domain | commit + tests (domain doc update) |
| Data-model change | ADR (and migration) |
| Security posture / trust model | ADR + security review |
| New platform capability / roadmap | RFC |
| Cross-cutting refactor with risk | RFC (or ADR if decision is clear) |

## Default: document in doubt
If you are unsure whether a change deserves a record, write the record. The cost
is one file; the cost of an undocumented decision is re-litigation later.
