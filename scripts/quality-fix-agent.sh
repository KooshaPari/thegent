#!/usr/bin/env bash
# quality-fix-agent.sh — Run quality fix; on failure, pipe output to agent.
# Flags: -d/--unsafe (ruff --unsafe-fixes), -a (agent on fail), -h (headless), -r (reload until green)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

UNSAFE=0
AGENT_ON_FAIL=0
HEADLESS=0
RELOAD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--unsafe) UNSAFE=1; shift ;;
    -a|--agent)  AGENT_ON_FAIL=1; shift ;;
    -h|--headless) HEADLESS=1; shift ;;
    -r|--reload) RELOAD=1; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

_run_fix() {
  uv run ruff format .
  if [[ "$UNSAFE" -eq 1 ]]; then
    uv run ruff check . --fix --unsafe-fixes
  else
    uv run ruff check . --fix
  fi
}

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
      echo "Quality fix failed. Output:"
      echo "$prompt"
      echo ""
      echo "Install copilot for interactive fix."
      exit 1
    fi
  fi
}

if [[ "$AGENT_ON_FAIL" -eq 0 ]] && [[ "$RELOAD" -eq 0 ]]; then
  _run_fix
  exit 0
fi

while true; do
  set +e
  RUN_OUTPUT=$(_run_fix 2>&1)
  RC=$?
  set -e

  if [[ "$RC" -eq 0 ]]; then
    [[ "$RELOAD" -eq 1 ]] && echo "── Quality fix passed ──"
    exit 0
  fi

  if [[ "$AGENT_ON_FAIL" -eq 0 ]]; then
    echo "── Quality fix failed (use -a with -r for reload loop) ──"
    exit 1
  fi

  PROMPT="Fix these quality/lint issues. Apply fixes automatically. Output from ruff/format:

---
${RUN_OUTPUT}
---"

  [[ "$RELOAD" -eq 1 ]] && echo "── Quality fix failed, piping to agent (reload until green) ──"
  _do_agent "$PROMPT"
  [[ "$RELOAD" -eq 0 ]] && exit 1
done
