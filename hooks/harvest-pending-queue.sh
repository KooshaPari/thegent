#!/bin/zsh
# harvest-pending-queue.sh — Stop hook
# Flushes pending queue ($defer/$pending) to handoff file on session stop.
set -euo pipefail

trap 'echo "HARVEST-PENDING-QUEUE FAIL: unexpected error at line $LINENO" >&2' ERR

PROJECT_DIR="${PROJECT_DIR:-}"
STATE_DIR="${STATE_DIR:-$HOME/.claude}"
GLOBAL_QUEUE="$STATE_DIR/pending-queue.jsonl"
GLOBAL_HANDOFF="$STATE_DIR/pending-handoff.md"
QUEUE_FILE="$GLOBAL_QUEUE"
HANDOFF_FILE="$GLOBAL_HANDOFF"

# Project-scoped: prefer PROJECT_DIR/.claude/pending-queue.jsonl
if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]]; then
  PROJ_QUEUE="${PROJECT_DIR}/.claude/pending-queue.jsonl"
  PROJ_HANDOFF="${PROJECT_DIR}/docs/research/pending-handoff.md"
  if [[ -f "$PROJ_QUEUE" ]] && [[ -s "$PROJ_QUEUE" ]]; then
    QUEUE_FILE="$PROJ_QUEUE"
    mkdir -p "$(dirname "$PROJ_HANDOFF")"
    HANDOFF_FILE="$PROJ_HANDOFF"
  fi
fi

# Fallback to global queue if project queue empty/missing
if [[ ! -f "$QUEUE_FILE" ]] || [[ ! -s "$QUEUE_FILE" ]]; then
  if [[ -f "$GLOBAL_QUEUE" ]] && [[ -s "$GLOBAL_QUEUE" ]]; then
    QUEUE_FILE="$GLOBAL_QUEUE"
    HANDOFF_FILE="$GLOBAL_HANDOFF"
    mkdir -p "$STATE_DIR"
  else
    exit 0
  fi
fi

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)
COUNT=0

{
  echo "# Pending prompts (from session stop $TS)"
  echo ""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    PROMPT=$(echo "$line" | jq -r '.prompt // empty' 2>/dev/null)
    [[ -z "$PROMPT" ]] && continue
    (( COUNT++ )) || true
    echo "$COUNT. $PROMPT"
    echo ""
  done < "$QUEUE_FILE"
} >> "$HANDOFF_FILE"

# Clear queue
: > "$QUEUE_FILE"

echo "Pending queue: flushed $COUNT item(s) to $HANDOFF_FILE" >&2
exit 0
