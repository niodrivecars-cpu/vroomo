# Code Review Standard

The contract for every code review on this platform.

## What must be true before review starts

- [ ] Automated checks pass: ruff, bandit `-ll`, pip-audit, migration check.
- [ ] Tests exist for the change (new behavior → new/updated tests).
- [ ] Security review requested for anything security-touching (auth, tenant
      scoping, downloads, rate limits, cookies, headers).
- [ ] No unrelated changes in the same diff.

## Review checklist

- **Correctness** — does the change do what it claims? Are edge cases handled?
- **Tenant safety** — any new query scoped to the tenant? Any IDOR path?
- **Security** — inputs validated, rate limits respected, no secrets logged.
- **Concurrency** — any race introduced? If the change touches shared state,
  is there a test under concurrency?
- **Tests** — do they fail without the change (red) and pass with it (green)?
  Do they match `fleet/tests/` conventions?
- **Complexity** — is there a simpler way? Unnecessary layers added?
- **i18n** — user-facing strings translatable, RTL respected?
- **Migrations** — reversible where sensible; no data drift.

## Review rules

1. Review the diff, not the author.
2. Every blocking comment is either a concrete defect or a testable concern —
   never a taste preference.
3. Approve only when all blocking items are resolved; non-blocking items go into
   a follow-up note.
4. The reviewer's job is to protect the evidence chain: a merge without passing
   checks breaks the platform's promise.

## Outcome recording

Record the review verdict (approved / changes-requested) and, for
security-touching changes, the security reviewer's sign-off — so the evidence
exists that review happened.
