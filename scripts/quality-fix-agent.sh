#!/usr/bin/env zsh
# quality-fix-agent.sh — Run quality fix; on failure, pipe output to agent.
# Flags: -d/--unsafe (ruff --unsafe-fixes), -a (agent on fail), -h (headless), -r (reload until green)
set -euo pipefail

if [ -n "${BASH_VERSION:-}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
else
  _SCRIPT_PATH="$0"
fi
_SCRIPT_DIR="${_SCRIPT_PATH%/*}"
ROOT_DIR="$(cd "$_SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

UNSAFE=0
AGENT_ON_FAIL=0
HEADLESS=0
RELOAD=0
VERBOSE=0
MAX_ATTEMPTS="${QUALITY_MAX_ATTEMPTS:-2}"
MAX_PROMPT_CHARS="${QUALITY_MAX_PROMPT_CHARS:-20000}"
MAX_RUNTIME_SEC="${QUALITY_MAX_RUNTIME_SEC:-1200}"

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

if ! [[ "$MAX_ATTEMPTS" =~ ^[0-9]+$ ]] || [[ "$MAX_ATTEMPTS" -lt 1 ]]; then
  echo "Invalid QUALITY_MAX_ATTEMPTS='$MAX_ATTEMPTS' (must be integer >= 1)"
  exit 1
fi

if ! [[ "$MAX_RUNTIME_SEC" =~ ^[0-9]+$ ]] || [[ "$MAX_RUNTIME_SEC" -lt 60 ]]; then
  echo "Invalid QUALITY_MAX_RUNTIME_SEC='$MAX_RUNTIME_SEC' (must be integer >= 60)"
  exit 1
fi

if [[ "${THEGENT_QUALITY_AGENT_ACTIVE:-0}" == "1" ]]; then
  echo "QUALITY LOOP GUARD: nested quality-fix-agent invocation blocked to prevent recursion."
  exit 2
fi
export THEGENT_QUALITY_AGENT_ACTIVE=1

_cleanup_storage() {
  if [[ "${QUALITY_AUTO_CLEANUP:-1}" == "1" ]]; then
    local shadow_cleanup_hours="${QUALITY_SHADOW_CLEANUP_HOURS:-${QUALITY_SHADOW_MAX_AGE_HOURS:-24}}"
    uv run python scripts/quality_cleanup.py \
      --shadow-max-age-hours "${shadow_cleanup_hours}" \
      --log-max-age-days "${QUALITY_LOG_RETENTION_DAYS:-7}"
  fi
}

_cleanup_storage

_run_fix() {
  if [[ "$UNSAFE" -eq 1 ]]; then
    uv run ruff format .
    uv run ruff check . --fix --unsafe-fixes
  else
    task format
  fi
}

KUSH_LIB="${KUSH_LIB:-$(cd "$_SCRIPT_DIR/../.." 2>/dev/null && pwd)/lib}"
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

_truncate_output() {
  local input="$1"
  if [[ "${#input}" -le "$MAX_PROMPT_CHARS" ]]; then
    printf '%s' "$input"
    return 0
  fi
  local clipped="${input:0:$MAX_PROMPT_CHARS}"
  printf '%s\n\n[...truncated quality output to %s chars...]\n' "$clipped" "$MAX_PROMPT_CHARS"
}

if [[ "$AGENT_ON_FAIL" -eq 0 ]] && [[ "$RELOAD" -eq 0 ]]; then
  _run_fix
  exit 0
fi

while true; do
  START_TS="${START_TS:-$SECONDS}"
  if [[ "$((SECONDS - START_TS))" -ge "$MAX_RUNTIME_SEC" ]]; then
    echo "Reached QUALITY_MAX_RUNTIME_SEC=${MAX_RUNTIME_SEC}s; stopping quality-fix reload loop."
    exit 1
  fi
  ATTEMPT="${ATTEMPT:-1}"
  if [[ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]]; then
    echo "Reached QUALITY_MAX_ATTEMPTS=$MAX_ATTEMPTS; stopping reload loop."
    exit 1
  fi
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

  TRUNCATED_OUTPUT="$(_truncate_output "$RUN_OUTPUT")"
  PROMPT="Fix these quality/lint issues. Apply fixes automatically. Output from ruff/format:

---
${TRUNCATED_OUTPUT}
---"

  [[ "$RELOAD" -eq 1 ]] && echo "── Quality fix failed: attempt ${ATTEMPT}/${MAX_ATTEMPTS}; piping to agent ──"
  _do_agent "$PROMPT"
  _cleanup_storage
  ATTEMPT=$((ATTEMPT + 1))
  [[ "$RELOAD" -eq 0 ]] && exit 1
done
