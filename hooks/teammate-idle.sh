#!/bin/zsh
# teammate-idle.sh — TeammateIdle hook
# Detects if a teammate agent is idle and injects feedback to keep it working.
# Exit 2 triggers feedback injection in the wrapper.
set -euo pipefail

HOOK_NAME="TEAMMATE-IDLE"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Input JSON contains 'stdout' of the teammate
STDOUT=$(echo "$INPUT" | jq -r '.stdout // ""')

if [[ -z "$STDOUT" ]]; then
  exit 0
fi

# Use TeamCoordinator to detect idle via python script
IDLE=$(python3 -c "
from thegent.team.coordination import TeamCoordinator
from pathlib import Path
import sys
tc = TeamCoordinator(Path('.'))
print('true' if tc.detect_idle(sys.stdin.read()) else 'false')
" <<< "$STDOUT")

if [[ "$IDLE" == "true" ]]; then
  NOTIFIER="${BASH_SOURCE[0]%/*}/notify-agent-event.sh"
  if [[ -x "$NOTIFIER" ]]; then
    "$NOTIFIER" \
      --event "teammateidle" \
      --severity "warning" \
      --title "Teammate Idle" \
      --message "A teammate appears idle and may need follow-up input." \
      >/dev/null 2>&1 || true
  fi
  echo "TEAMMATE-IDLE: Teammate is idle, requesting feedback." >&2
  # Exit 2 is the sentinel for "inject feedback prompt"
  exit 2
fi

exit 0
