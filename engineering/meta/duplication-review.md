# Duplication Review

Detects the same concept defined in more than one place. A duplicated source of
truth is the platform's worst drift (kernel `failure-model.md`, mode 6) because
it makes the two definitions silently diverge.

## What to check
| Pattern | Allowed? |
|---|---|
| Glossary defines a term; other docs use it | ✅ (referencing) |
| Two docs both *define* the same entity/term | ❌ duplication |
| Canonical model defines entity; context doc re-declares its fields | ❌ duplication |
| Two playbooks describe the same incident procedure | ❌ duplication |
| Evidence copied into two manifests | ❌ (append-only; supersede instead) |

## Method
1. For every glossary term and canonical entity/state/command/policy, find all
   definitions (grep for the term heading).
2. A second *definition* (not a reference) is a duplication.
3. Resolve: keep the older/authoritative source, convert the other to a
   reference, or supersede it explicitly.

## Verdict
PASS if every concept has exactly one definition; FAIL with the duplicated
pairs — recorded as meta evidence.
