# Engineering Platform

An Engineering Operating System for building Django-based products (and, in time,
any backend service) with repeatable quality. Vroom is the first project hosted
on this platform; Nio Drive and future projects will follow without changing the
platform itself.

## Layered architecture

```
engineering/
  platform/       How the platform itself works
  governance/     How decisions are made (principles, standards, ADRs, RFCs)
  knowledge/      What we know (engineering + business reference library)
  patterns/       Approved solutions (when to use, when not, with evidence)
  domain/         Business rules per domain (Vroom's fleet/booking world)
  execution/      How we execute (pipelines, gates, playbooks, runbooks)
  verification/   How we prove correctness (standard, confidence, risk)
  evidence/       What the proof is (machines verifiable artifacts)
  projects/       Products built on the platform (vroom/, nio/...)
```

## First project on the platform

- **Vroom** — multi-tenant fleet management, RC1 tagged `v1.0.0-rc1`.
  See `projects/vroom/README.md`.

## How to navigate

| I want to... | Go to |
|---|---|
| Understand the platform | `platform/README.md`, `platform/ARCHITECTURE.md` |
| Know the engineering rules | `governance/GOVERNANCE.md` |
| Look up an approved solution | `patterns/` |
| Understand a business domain | `domain/<domain>/` |
| Run a release | `execution/playbooks/release-playbook.md` |
| Prove a change is safe | `verification/verification-standard.md` |
| Find recorded proof | `evidence/index.json` |
| See project history | `projects/vroom/` |
