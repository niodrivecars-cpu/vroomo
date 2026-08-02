# Platform Versioning

## Versioning scheme

The platform itself follows Semantic Versioning (`MAJOR.MINOR.PATCH`), tracked in
`ROADMAP.md` phases, not as a package release. A version bumps when:

- **MAJOR** — a layer is removed or renamed (breaking structural contract).
- **MINOR** — a new capability or layer is added.
- **PATCH** — corrections and refinements within a layer.

## Relationship to product versions

Product versions (e.g. `v1.0.0-rc1` for Vroom) are independent of platform
version. A product tags its own releases against its own history under
`projects/<name>/release-history/`. The platform guarantees: "if the product
passes the platform gates, the recorded evidence supports the release claim."

## Evidence immutability

Evidence files under `evidence/` are append-only. Correcting a prior release
record requires a new entry plus a supersedes pointer; never edit a closed
manifest in place. `evidence/index.json` is the single mutable index.

## Backwards compatibility

Platform docs may be referenced by multiple projects. Deprecate a pattern or
standard by marking it `Status: superseded by <X>` and leaving it in place with a
pointer — never delete silently.
