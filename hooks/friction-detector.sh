#!/usr/bin/env zsh
# friction-detector.sh — PostToolUse hook (Edit|Write|Execute)
# Detects UX/DX/AX friction patterns in code and commands.
# Advisory only (exit 0 always). Budget: <500ms.
set -euo pipefail

if [ -n "${ZSH_VERSION:-}" ]; then
  _SCRIPT_PATH="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
else
  _SCRIPT_PATH="$0"
fi
_SCRIPT_DIR="${_SCRIPT_PATH%/*}"

# Fast-path: skip common.sh if dispatched
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # FILE_PATH, TOOL_NAME, PROJECT_DIR already exported
  :
else
  HOOK_NAME="FRICTION-DETECTOR"
  source "$_SCRIPT_DIR/lib/common.sh"
  hook_init
fi

# Only run on Write/Edit/Execute
[[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Execute" ]] && exit 0

FRICTION_DETECTOR="${PROJECT_DIR}/scripts/friction_detector.py"
[[ ! -f "$FRICTION_DETECTOR" ]] && exit 0

# For Execute: scan command
if [[ "$TOOL_NAME" == "Execute" ]]; then
  COMMAND="${TOOL_INPUT:-}"
  [[ -z "$COMMAND" ]] && exit 0
  
  FINDINGS=$(timeout 2 python3 "$FRICTION_DETECTOR" --command "$COMMAND" --format json 2>/dev/null || echo "[]")
  [[ "$FINDINGS" == "[]" ]] && exit 0
  
  echo "FRICTION DETECTED in command:"
  echo "$FINDINGS" | python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"  [{f['priority']}] {f['category'].upper()}: {f['type']} - {f['description']}\") for f in d]"
  exit 0
fi

# For Write/Edit: scan file
[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

FINDINGS=$(timeout 2 python3 "$FRICTION_DETECTOR" --file "$FILE_PATH" --format json 2>/dev/null || echo "[]")
[[ "$FINDINGS" == "[]" ]] && exit 0

echo "FRICTION DETECTED in ${FILE_PATH##*/}:"
echo "$FINDINGS" | python3 -c "import sys, json; d=json.load(sys.stdin); [print(f\"  [{f['priority']}] {f['category'].upper()}: {f['type']} - {f['description']} (line {f['location'].split(':')[-1]})\") for f in d]"

exit 0
