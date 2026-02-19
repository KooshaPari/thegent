#!/bin/zsh
# task-completed.sh — TaskCompleted hook
# Updates task status in TeamManager when a task is completed.
set -euo pipefail

HOOK_NAME="TASK-COMPLETED"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

TEAM_ID=$(echo "$INPUT" | jq -r '.team_id // ""')
TASK_ID=$(echo "$INPUT" | jq -r '.task_id // ""')
RESULT=$(echo "$INPUT" | jq -r '.result // ""')

if [[ -z "$TEAM_ID" || -z "$TASK_ID" ]]; then
  echo "TASK-COMPLETED: Missing TEAM_ID or TASK_ID, skipping." >&2
  exit 0
fi

python3 -c "
from thegent.team.coordination import TeamCoordinator
from pathlib import Path
import sys
tc = TeamCoordinator(Path('.'))
tc.handle_task_completed('$TEAM_ID', '$TASK_ID', '$RESULT')
"

echo "TASK-COMPLETED: Task $TASK_ID updated in team $TEAM_ID"

NOTIFIER="${BASH_SOURCE[0]%/*}/notify-agent-event.sh"
if [[ -x "$NOTIFIER" ]]; then
  "$NOTIFIER" \
    --event "taskcompleted" \
    --severity "info" \
    --title "Task Completed" \
    --message "team=$TEAM_ID task=$TASK_ID completed" \
    >/dev/null 2>&1 || true
fi

# Trigger auto-launch system
AUTO_LAUNCH_TRIGGER="${BASH_SOURCE[0]%/*}/auto-launch-trigger.sh"
if [[ -x "$AUTO_LAUNCH_TRIGGER" ]]; then
  export SESSION_ID="${SESSION_ID:-}"
  export EXIT_CODE="${EXIT_CODE:-0}"
  export WORKSTREAM_ITEM_ID="${TASK_ID:-}"
  "$AUTO_LAUNCH_TRIGGER" >/dev/null 2>&1 || true
fi

exit 0
