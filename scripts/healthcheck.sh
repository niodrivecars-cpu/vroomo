#!/usr/bin/env bash
# Probe the Vroom /health/ endpoint.
#
# Usage: scripts/healthcheck.sh <ENV_FILE> [BASE_URL]
#   BASE_URL defaults to http://127.0.0.1:8000
#
# Exits 0 when the endpoint returns HTTP 200 with "status":"ok".
set -euo pipefail

ENV_FILE="${1:?Usage: healthcheck.sh ENV_FILE [BASE_URL]}"
BASE_URL="${2:-http://127.0.0.1:8000}"

# Locate the site's own allowed host so ALLOWED_HOSTS accepts the request.
set -a
. "$ENV_FILE"
set +a

HOST="${ALLOWED_HOSTS%%,*}"
if [ -n "$HOST" ]; then
    HOST_HEADER="Host: $HOST"
else
    HOST_HEADER=""
fi

for attempt in 1 2 3; do
    if RESPONSE=$(curl -fsS --max-time 10 ${HOST_HEADER:+-H "$HOST_HEADER"} "$BASE_URL/health/"); then
        STATUS=$(printf '%s' "$RESPONSE" | sed -n 's/.*"status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        if [ "$STATUS" = "ok" ]; then
            echo "Health OK: $RESPONSE"
            exit 0
        fi
        echo "Health degraded (status=$STATUS): $RESPONSE" >&2
        exit 1
    fi
    echo "Attempt $attempt failed, retrying..." >&2
    sleep 3
done

echo "Health check FAILED after 3 attempts" >&2
exit 1
