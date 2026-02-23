#!/usr/bin/env bash
# agileplus-cycle.sh — Stop hook
# AgilePlus governance cycle: runs quick health checks on Stop.
# Implements: backlog health, estimate accuracy, velocity trends, WIP limits.
# Budget: <10s. Advisory only (exit 0 always).
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)}"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -n "${HEAD_SHA:-}" ]]; then
  _CACHE_FILE="${_CACHE_DIR}/agileplus-cycle-${HEAD_SHA}.result"
  if [[ -f "$_CACHE_FILE" ]]; then
    _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
    if (( _age < _CACHE_TTL )); then
      cat "$_CACHE_FILE"
      exit 0
    fi
  fi
else
  _CACHE_FILE=""
fi

HOOK_NAME="AGILEPLUS-CYCLE"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

# --- P1: Skip if no relevant files changed ---
# AgilePlus runs on code/config changes
if ! any_source_changed; then
  echo "AGILEPLUS-CYCLE: skipped (no source files changed)"
  exit 0
fi

AGILEPLUS_STATE="${HOME}/.claude/agileplus-state.json"
mkdir -p "$(dirname "$AGILEPLUS_STATE")"

_agileplus_main() {
echo "=== AgilePlus Governance Cycle ==="

# --- Backlog Health Check ---
BACKLOG_ISSUES=0
BACKLOG_FILE="${PROJECT_DIR}/.thegent/backlog.md"
if [[ -f "$BACKLOG_FILE" ]]; then
  # Count open items
  open_count=$(grep -cE '^\- \[ \]|^\* \[ \]' "$BACKLOG_FILE" 2>/dev/null || echo 0)
  # Count stale items (>30 days without update)
  stale_count=0
  if command -v rg >/dev/null 2>&1; then
    stale_count=$(rg -c 'updated.*[3-9][0-9] days|updated.*[1-9][0-9]{2,}' "$BACKLOG_FILE" 2>/dev/null | wc -l || echo 0)
  fi

  echo "Backlog: $open_count open items, $stale_count stale"

  if [[ $stale_count -gt 5 ]]; then
    echo "  WARN: $stale_count items haven't been updated in 30+ days"
    BACKLOG_ISSUES=$((BACKLOG_ISSUES + 1))
  fi
else
  echo "Backlog: no backlog.md found (optional)"
fi

# --- WIP Limit Check ---
WIP_ISSUES=0
WIP_STATE="${HOME}/.claude/wip-state.json"
if [[ -f "$WIP_STATE" ]]; then
  current_wip=$($JQ_CMD -r '.current_wip // 0' "$WIP_STATE" 2>/dev/null || echo 0)
  max_wip=$($JQ_CMD -r '.max_wip // 5' "$WIP_STATE" 2>/dev/null || echo 5)

  echo "WIP: $current_wip items (max: $max_wip)"

  if [[ $current_wip -gt $max_wip ]]; then
    echo "  WARN: WIP exceeds limit ($current_wip > $max_wip)"
    WIP_ISSUES=1
  fi
else
  echo "WIP: no state file (skipping)"
fi

# --- Velocity Trend (if we have history) ---
VELOCITY_ISSUES=0
if [[ -f "$AGILEPLUS_STATE" ]]; then
  last_velocity=$($JQ_CMD -r '.last_velocity // 0' "$AGILEPLUS_STATE" 2>/dev/null || echo 0)
  avg_velocity=$($JQ_CMD -r '.avg_velocity // 0' "$AGILEPLUS_STATE" 2>/dev/null || echo 0)

  if [[ $last_velocity -gt 0 && $avg_velocity -gt 0 ]]; then
    change_pct=$(( (last_velocity - avg_velocity) * 100 / avg_velocity ))
    echo "Velocity: $last_velocity (avg: $avg_velocity, change: ${change_pct}%)"

    # Warn if velocity dropped >30%
    if [[ $change_pct -lt -30 ]]; then
      echo "  WARN: Velocity dropped ${change_pct}% vs average"
      VELOCITY_ISSUES=1
    fi
  fi
fi

# --- Update state for next run ---
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
# Calculate current session contributions from change log
session_contrib=0
if [[ -f "$CHANGE_LOG" ]]; then
  session_contrib=$(grep -cE 'created|modified' "$CHANGE_LOG" 2>/dev/null || echo 0)
fi

# Update agileplus state
$JQ_CMD -n \
  --arg ts "$now" \
  --argjson last "$session_contrib" \
  --argjson avg "$(( (last_velocity + session_contrib) / 2 ))" \
  '{
    last_velocity: $last,
    avg_velocity: $avg,
    last_updated: $ts
  }' > "$AGILEPLUS_STATE.tmp" && mv "$AGILEPLUS_STATE.tmp" "$AGILEPLUS_STATE"

# --- Summary ---
TOTAL_ISSUES=$((BACKLOG_ISSUES + WIP_ISSUES + VELOCITY_ISSUES))
echo ""
if [[ $TOTAL_ISSUES -gt 0 ]]; then
  echo "AGILEPLUS: $TOTAL_ISSUES governance issue(s) found"
else
  echo "AGILEPLUS: governance cycle complete (no issues)"
fi

# Write results
RESULTS_FILE="${VERIFY_DIR}/agileplus-cycle.json"
mkdir -p "$(dirname "$RESULTS_FILE")"
$JQ_CMD -n \
  --arg ts "$now" \
  --argjson backlog "$BACKLOG_ISSUES" \
  --argjson wip "$WIP_ISSUES" \
  --argjson velocity "$VELOCITY_ISSUES" \
  --argjson total "$TOTAL_ISSUES" \
  '{
    timestamp: $ts,
    backlog_issues: $backlog,
    wip_issues: $wip,
    velocity_issues: $velocity,
    total_issues: $total
  }' > "$RESULTS_FILE"

} # end _agileplus_main

# Run main, capture output, cache result
_output=$(_agileplus_main 2>&1); _rc=$?

# Write cache
if [[ -n "${_CACHE_FILE:-}" ]]; then
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  if [[ -n "$_output" ]]; then
    echo "$_output" > "$_CACHE_FILE"
  else
    : > "$_CACHE_FILE"
  fi
fi

[[ -n "$_output" ]] && echo "$_output"
exit $_rc
