#!/usr/bin/env bash
# init-worktree.sh — Initialize a worktree with randomized high ports
# Usage: ./scripts/init-worktree.sh <topic-name> [<repo-name>]
# Example: ./scripts/init-worktree.sh feature-auth heliosApp

set -euo pipefail

TOPIC="${1:?Usage: $0 <topic-name> [<repo-name>]}"
REPO="${2:-$(basename "$PWD")}"
PORT_BASE=30000
PORT_MAX=39999

generate_port() {
  echo $((PORT_BASE + RANDOM % (PORT_MAX - PORT_BASE)))
}

MAIN_PORT=$(generate_port)
API_PORT=$(generate_port)
AUX_PORT=$(generate_port)

ENV_FILE=".env.worktree"

printf "# Worktree port allocation for: %s\n" "$TOPIC" > "$ENV_FILE"
printf "# Repo: %s\n" "$REPO" >> "$ENV_FILE"
printf "# Generated: %s\n" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$ENV_FILE"
printf "# DO NOT commit this file (it is in .gitignore)\n" >> "$ENV_FILE"
printf "\n" >> "$ENV_FILE"
printf "WORKTREE_TOPIC=%s\n" "$TOPIC" >> "$ENV_FILE"
printf "WORKTREE_PORT=%s\n" "$MAIN_PORT" >> "$ENV_FILE"
printf "WORKTREE_API_PORT=%s\n" "$API_PORT" >> "$ENV_FILE"
printf "WORKTREE_AUX_PORT=%s\n" "$AUX_PORT" >> "$ENV_FILE"
printf "\n" >> "$ENV_FILE"
printf "# Shared infra — always use canonical ports\n" >> "$ENV_FILE"
printf "POSTGRES_PORT=5432\n" >> "$ENV_FILE"
printf "NATS_PORT=4222\n" >> "$ENV_FILE"
printf "REDIS_PORT=6379\n" >> "$ENV_FILE"
printf "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/phenotype\n" >> "$ENV_FILE"
printf "NATS_URL=nats://localhost:4222\n" >> "$ENV_FILE"

echo "Worktree '$TOPIC' initialized:"
echo "  Main port:  $MAIN_PORT"
echo "  API port:   $API_PORT"
echo "  Aux port:   $AUX_PORT"
echo "  Written to: $ENV_FILE"
echo ""
echo "To start with these ports:"
echo "  source .env.worktree && <your-dev-command>"
