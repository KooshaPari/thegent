#!/usr/bin/env bash
# quality-agent.sh — Run full quality pipeline; on failure, show output and pipe to agent.
# Flags: -h (headless), -r (reload until green)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HEADLESS=0
RELOAD=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--headless) HEADLESS=1; shift ;;
    -r|--reload) RELOAD=1; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

KUSH_LIB="${KUSH_LIB:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd)/lib}"
if [[ -f "${KUSH_LIB:-}/quality-agent-common.sh" ]]; then
  # shellcheck source=../../lib/quality-agent-common.sh
  source "$KUSH_LIB/quality-agent-common.sh"
else
  _run_copilot() {
    local prompt="$1"
    local primary="${COPILOT_QUALITY_MODEL:-gemini-3-flash}"
    local fallback="gpt-5-mini"
    set +e
    printf '%s' "$prompt" | copilot --model "$primary" --allow-all-paths --allow-all-tools
    local rc=$?
    set -e
    if [[ $rc -ne 0 ]]; then
      echo "── Primary model ($primary) unavailable, retrying with $fallback ──"
      printf '%s' "$prompt" | copilot --model "$fallback" --allow-all-paths --allow-all-tools
    fi
  }
fi

_do_agent() {
  local prompt="$1"
  if [[ "$HEADLESS" -eq 1 ]]; then
    uv run thegent run "$prompt"
  else
    if command -v copilot &>/dev/null; then
      _run_copilot "$prompt"
    else
      echo "Install copilot for interactive fix."
      exit 1
    fi
  fi
}

while true; do
  set +e
  RUN_OUTPUT=$(task quality 2>&1)
  RC=$?
  set -e

  if [[ "$RC" -eq 0 ]]; then
    [[ "$RELOAD" -eq 1 ]] && echo "── Quality passed ──"
    exit 0
  fi

  echo "── Quality failed. Output below (piping to agent): ──"
  echo "$RUN_OUTPUT"
  echo "── End of quality output ──"

  PROMPT="Fix these quality issues. Apply fixes. Full quality pipeline output:

---
${RUN_OUTPUT}
---"

  [[ "$RELOAD" -eq 1 ]] && echo "── Reload: piping to agent, will rerun until green ──"
  _do_agent "$PROMPT"
  [[ "$RELOAD" -eq 0 ]] && exit 1
done
