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
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--unsafe) UNSAFE=1; shift ;;
    -a|--agent)  AGENT_ON_FAIL=1; shift ;;
    -h|--headless) HEADLESS=1; shift ;;
    -r|--reload) RELOAD=1; shift ;;
    -v|--verbose) VERBOSE=1; shift ;;
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
  _run_quality_agent() {
    local prompt="$1"
    # dex + copilot gpt-5-mini (copilot doesn't support flash); replaces direct copilot
    local model="${COPILOT_QUALITY_MODEL:-gpt-5-mini}"
    uv run thegent dex run "$model" "$prompt" --mode write
  }
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
