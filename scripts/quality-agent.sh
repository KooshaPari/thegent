#!/usr/bin/env zsh
# quality-agent.sh — Run full quality pipeline; on failure, show output and pipe to agent.
# Flags: -h (headless), -r (reload until green)
set -euo pipefail

if [ -n "${ZSH_VERSION:-}" ]; then
  _SCRIPT_PATH="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
else
  _SCRIPT_PATH="$0"
fi
_SCRIPT_DIR="${_SCRIPT_PATH%/*}"

ROOT_DIR="$(cd "$_SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v task &>/dev/null; then
  echo "Error: 'task' (go-task) not found. Install with: brew install go-task"
  echo "Or run: brew bundle (from project root)"
  exit 127
fi

HEADLESS=0
RELOAD=0
VERBOSE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--headless) HEADLESS=1; shift ;;
    -r|--reload) RELOAD=1; shift ;;
    -v|--verbose) VERBOSE=1; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

_run_quality_agent() {
  local prompt="$1"
  # dex + copilot gpt-5-mini (copilot doesn't support flash); replaces direct copilot
  local model="${COPILOT_QUALITY_MODEL:-gpt-5-mini}"
  uv run thegent dex run "$model" "$prompt" --mode write
}

KUSH_LIB="${KUSH_LIB:-$(cd "$_SCRIPT_DIR/../.." 2>/dev/null && pwd)/lib}"
if [[ -f "${KUSH_LIB:-}/quality-agent-common.sh" ]]; then
  # shellcheck source=../../lib/quality-agent-common.sh
  source "$KUSH_LIB/quality-agent-common.sh"
fi

_do_agent() {
  local prompt="$1"
  local extra_args=""
  [[ "$VERBOSE" -eq 1 ]] && extra_args="--full"

  if [[ "$HEADLESS" -eq 1 ]]; then
    # shellcheck disable=SC2086
    uv run thegent run "$prompt" quality-agent $extra_args
  else
    if command -v codex &>/dev/null; then
      _run_quality_agent "$prompt"
    else
      echo "No codex found, falling back to thegent quality-agent..."
      # shellcheck disable=SC2086
      uv run thegent run "$prompt" quality-agent $extra_args
    fi
  fi
}

while true; do
  set +e
  # quality:dag auto-generates config, runs DAG with soft-fail, prints failed logs for agent
  RUN_OUTPUT=$(task quality:dag 2>&1)
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
