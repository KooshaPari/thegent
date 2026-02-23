#!/usr/bin/env bash
# quality-agent-common.sh — Shared copilot/thegent agent logic for quality scripts.
# Source this from project scripts. Requires: ROOT_DIR, HEADLESS (0/1).
# Provides: _run_copilot, _do_agent
# Override: THGENT_HEADLESS_CMD for custom headless command.

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

_do_agent() {
  local prompt="$1"
  if [[ "${HEADLESS:-0}" -eq 1 ]]; then
    if [[ -n "${THGENT_HEADLESS_CMD:-}" ]]; then
      bash -c "\"$THGENT_HEADLESS_CMD\" \"\$1\"" _ "$prompt"
    elif [[ -f "${ROOT_DIR:-.}/pyproject.toml" ]] && grep -q 'name = "thegent"' "${ROOT_DIR:-.}/pyproject.toml" 2>/dev/null; then
      (cd "${ROOT_DIR:-.}" && uv run thegent run "$prompt")
    elif command -v thegent &>/dev/null; then
      thegent run "$prompt"
    elif [[ -d "${ROOT_DIR:-.}/../thegent" ]] && [[ -f "${ROOT_DIR:-.}/../thegent/pyproject.toml" ]]; then
      (cd "${ROOT_DIR:-.}/../thegent" && uv run thegent run "$prompt")
    else
      echo "Install thegent or run from sibling of thegent for headless fix."
      exit 1
    fi
  else
    if command -v copilot &>/dev/null; then
      _run_copilot "$prompt"
    else
      echo "Install copilot for interactive fix."
      exit 1
    fi
  fi
}
