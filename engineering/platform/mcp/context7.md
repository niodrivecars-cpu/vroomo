# context7 MCP

Live, up-to-date library documentation for any framework/SDK (React, Django,
MySQL, k6, ...).

## When to use
- API syntax, configuration, version migration, setup, debugging a library issue.
- CLI tool usage (e.g. k6, uvx).
- Confirming whether your training-data knowledge is stale for a library version.

## When NOT to use
- Refactoring existing code, debugging business logic, code review, general
  programming concepts.
- When the repo already documents the answer (check `knowledge/` first).

## Call order
1. `resolve-library-id` with the library name + what to look up.
2. Pick best match (exact name, description relevance, snippets, reputation,
   benchmark score).
3. `query-docs` scoped to ONE concept per call.
4. For multi-concept questions, one `query-docs` call per concept.

## Common mistakes
- Skipping `resolve-library-id` when the user didn't give a `/org/project` ID.
- Combining multiple distinct concepts in one query (dilutes ranking).
- Using it for things the repo already answers.

## Example
```
resolve-library-id: "Django" → query: "multi-tenant row-level isolation with select_for_update"
```
