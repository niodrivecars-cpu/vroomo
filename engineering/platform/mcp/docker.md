# docker MCP

Planned. Covers container lifecycle for the local MySQL service and any future
service composition.

## When to use (planned)
- `docker compose up/down/ps` for the MySQL dev service.
- Inspecting container logs/state during debugging.

## When NOT to use
- Deployment to Hostinger shared hosting — that's the hPanel Python App /
  Passenger path (`scripts/deploy-hostinger.sh`), not Docker.
- Anything that should be answered from `knowledge/` or the repo.

## Status
Not yet configured in `opencode.jsonc`. Enable once Docker is a standard part of
the local workflow (MySQL dev DB is the first use case).
