#!/usr/bin/env bash
# subagent-quality-gate.sh — SubagentStart/SubagentStop hook
# Ultra-lightweight: start records a timestamp, stop computes elapsed.
# Advisory only (always exits 0). Lint deferred to Stop hooks.
set -euo pipefail

ACTION="${1:-}"
STARTS_FILE="$HOME/.claude/.subagent-starts"

# ---------- Start: record epoch, nothing else ----------
if [[ "$ACTION" == "start" ]]; then
  echo "${EPOCHSECONDS}" >> "$STARTS_FILE" 2>/dev/null || true
  exit 0
fi

# ---------- Stop: compute elapsed from last start ----------
if [[ "$ACTION" == "stop" ]]; then
  ELAPSED=0
  if [[ -f "$STARTS_FILE" ]]; then
    # Read last line with bash builtin (no tail fork)
    while IFS= read -r _line; do _last="$_line"; done < "$STARTS_FILE" 2>/dev/null || true
    [[ -n "${_last:-}" ]] && ELAPSED=$(( EPOCHSECONDS - _last )) || true
    rm -f "$STARTS_FILE" 2>/dev/null || true
  fi
  echo "Subagent quality gate: ${ELAPSED}s elapsed (lint deferred to Stop)"
  exit 0
fi

exit 0
