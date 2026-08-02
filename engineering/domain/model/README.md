# Canonical Model

The **single official definition** of Vroom's business model. Everything else in
`domain/`, `knowledge/`, and `patterns/` **references** this model; nothing
redefines it. This prevents documentation drift: one source per entity, state,
event, command, and policy.

```text
domain/model/          ← canonical (this directory)
  entities.md             responsibilities, owners, lifecycles, constraints
  relationships.md        cardinality + deletion rules
  state-machines.md       states, legal + forbidden transitions
  events.md               business events (real / derived / aspirational)
  commands.md             allowed actions with guards
  policies.md             the business policies (the source of truth)
  use-cases.md            end-to-end scenarios binding commands, policies, events, tests
```

Every policy in `policies.md` carries **governance** fields — Owner, Source,
Criticality, Risk, Priority, and a Decision status (✅ Enforced / 🟡 Validated /
🔵 Proposed / ⚪ Out of Scope / ❌ Rejected). Phase 2A is *Business Rule
Validation & Ownership*: validate the policy first, then approve → implement →
test → evidence.

## Grounded in code — and honest about it

The model is derived from `fleet/models.py` (the implementation truth at RC1).
Every file marks the status of each item:

| Mark | Meaning |
|---|---|
| ✅ | Represented + enforced + tested |
| ⚠️ | Represented in code, missing dedicated test |
| 🔲 | **Not represented** — a discovery gap for Phase 2A |
| 🧾 | Policy/decision question open |

## Canonical discipline

1. Define an entity **here**, once. Refer to it elsewhere (`domain/<ctx>/…`,
   `knowledge/…`), never re-declare its fields.
2. State machines live here (`state-machines.md`); per-context files link here.
3. When implementation changes, **this model is updated first**, then the
   invariants, then tests, then code — the source-of-truth order.
4. New entities (e.g. Invoice, Payment) are added here **before** any code.

## Truths the inventory surfaced (vs. common assumptions)

- **Vehicle has no `reserved` state.** A reservation is a `confirmed` booking.
  "Reserved" is a derived state of the vehicle, never stored.
- **Customer is not an entity** — it is embedded data on Booking
  (`customer_name`, `customer_phone`). Whether it becomes an entity is a Phase 2A
  decision.
- **Invoice and Payment are not modeled.** They appear here as planned entities
  with zero representation.

See the Business Completeness Gate (`execution/gates/business-completeness-gate.md`)
for how completeness is checked.
