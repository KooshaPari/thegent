#!/bin/zsh
# continuous-work-guard.sh — TeammateIdle / Stop hook
# Injects instructions to keep working on backlog items when idle
# Exit 2 triggers feedback injection to keep agent working
set -euo pipefail

HOOK_NAME="CONTINUOUS-WORK-GUARD"
# shellcheck source=./lib/common.sh
source "${0:h}/lib/common.sh"
hook_init

# Escalate immediately if governance marked a regression spiral.
SPIRAL_ALERT_FILE="${VERIFY_DIR:-$PROJECT_DIR/.claude/verification}/regression-spiral-alert.json"
if [[ -f "$SPIRAL_ALERT_FILE" ]]; then
  ALERT_SEVERITY=$(jq -r '.severity // "warning"' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "warning")
  ALERT_REASON=$(jq -r '.reason // "regression spiral detected"' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "regression spiral detected")
  ALERT_POLICY_BAND=$(jq -r '.policy_band // "green"' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "green")
  ALERT_BAND_RETRY_COUNT=$(jq -r '.band_retry_count // 0' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "0")
  ALERT_COOLDOWN_UNTIL=$(jq -r '.cooldown_until // 0' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "0")
  ALERT_ESCALATION_STAGE=$(jq -r '.escalation_stage // "none"' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "none")
  ALERT_REMEDIATION_DIRECTIVE=$(jq -r '.remediation_directive // "stabilize_before_new_changes"' "$SPIRAL_ALERT_FILE" 2>/dev/null || echo "stabilize_before_new_changes")

  _now_epoch="$(date +%s)"
  _cooldown_active=false
  _cooldown_remaining_minutes=0
  if [[ "$ALERT_COOLDOWN_UNTIL" =~ ^[0-9]+$ ]] && [[ "$_now_epoch" =~ ^[0-9]+$ ]] && (( ALERT_COOLDOWN_UNTIL > _now_epoch )); then
    _cooldown_active=true
    _cooldown_remaining_minutes=$((((ALERT_COOLDOWN_UNTIL - _now_epoch) + 59) / 60))
  fi

  echo "CONTINUOUS-WORK-GUARD: active $ALERT_SEVERITY spiral alert: $ALERT_REASON" >&2
  echo "CONTINUOUS-WORK-GUARD: policy_band=$ALERT_POLICY_BAND retry_count=$ALERT_BAND_RETRY_COUNT escalation_stage=$ALERT_ESCALATION_STAGE remediation_directive=$ALERT_REMEDIATION_DIRECTIVE cooldown_until=$ALERT_COOLDOWN_UNTIL" >&2
  if [[ "$ALERT_POLICY_BAND" == "yellow" || "$ALERT_POLICY_BAND" == "red" ]]; then
    if [[ "$_cooldown_active" == "true" ]]; then
      echo "CONTINUOUS-WORK-GUARD: deterministic cooldown active for $ALERT_POLICY_BAND band (${_cooldown_remaining_minutes}m remaining)." >&2
    else
      echo "CONTINUOUS-WORK-GUARD: deterministic cooldown not active for $ALERT_POLICY_BAND band." >&2
    fi
  fi

  if [[ "$ALERT_SEVERITY" == "critical" ]]; then
    echo ""
    echo "--- Regression Spiral Interrupt ---"
    echo "CRITICAL: Governance detected regression growth. Stop feature work now."
    echo "Directive: $ALERT_REMEDIATION_DIRECTIVE"
    if [[ "$_cooldown_active" == "true" ]]; then
      echo "Cooldown: active for $_cooldown_remaining_minutes more minute(s) (until epoch $ALERT_COOLDOWN_UNTIL)."
    else
      echo "Cooldown: not active."
    fi
    echo "1. Re-run diagnostics on touched files: task lint:python"
    echo "2. Run build/env readiness checks before coding: task shims:guard && task shims:probe"
    echo "3. Run tests with e2e coverage before continuing implementation"
    echo "4. Fix failures until gate is green; do not accumulate new changes"
    echo "5. Resume backlog only after regression alert clears"
    echo ""
    exit 2
  fi
fi

# Check if there are backlog items available
BACKLOG_COUNT=$(cd "$PROJECT_DIR" && thegent plan do-next --limit 1 --format json 2>&1 | /usr/bin/grep -v "grep config error" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('next_items', [])))" 2>&1 | /usr/bin/grep -v "grep config error" || echo "0")
if [[ ! "$BACKLOG_COUNT" =~ ^[0-9]+$ ]]; then
  BACKLOG_COUNT=0
fi

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
  exit 0
fi

exit 0
