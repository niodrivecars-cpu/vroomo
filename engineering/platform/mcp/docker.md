# docker MCP

Planned. Covers container lifecycle for the local postgres service and any
future service composition.

## When to use (planned)
- `docker compose up/down/ps` for the postgres dev service.
- Inspecting container logs/state during debugging.

## When NOT to use
- Deployment to the Hostinger VPS — that's a manual/scripted path
  (`scripts/deploy.sh`), not Docker.
- Anything that should be answered from `knowledge/` or the repo.

## Status
Not yet configured in `opencode.jsonc`. Enable once Docker is a standard part of
the local workflow (postgres dev DB is the first use case).
