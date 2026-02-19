#!/bin/zsh
# continuous-work-guard.sh — TeammateIdle / Stop hook
# Injects instructions to keep working on backlog items when idle
# Exit 2 triggers feedback injection to keep agent working
set -euo pipefail

HOOK_NAME="CONTINUOUS-WORK-GUARD"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Check if there are backlog items available
BACKLOG_COUNT=$(cd "$PROJECT_DIR" && thegent plan do-next --limit 1 --format json 2>&1 | /usr/bin/grep -v "grep config error" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('next_items', [])))" 2>&1 | /usr/bin/grep -v "grep config error" || echo "0")

if [[ "$BACKLOG_COUNT" -gt 0 ]]; then
  echo "CONTINUOUS-WORK-GUARD: $BACKLOG_COUNT backlog item(s) available. Keep working!" >&2
  echo ""
  echo "--- Continuous Work Instruction ---"
  echo "CRITICAL: Backlog has work available. Do NOT terminate chat."
  echo "1. Get next item: thegent plan get-next"
  echo "2. Work on it directly using tools (read_file, search_replace, codebase_search, etc.)"
  echo "3. Don't just delegate - work on items yourself"
  echo "4. After completing, check for next item: thegent plan do-next --limit 1"
  echo "5. Use 'thegent plan wait-next' to block until work ready (keeps session alive)"
  echo "6. Continue until backlog empty or explicitly told to stop"
  echo ""
  # Exit 2 triggers feedback injection
  exit 2
fi

exit 0
