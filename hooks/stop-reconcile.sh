#!/bin/bash
# Hook: Stop
# Purpose: On session stop (the "silent commit"), reconcile changes against
# the documentation system. Outputs context that Claude receives as feedback.

set -eo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_FILE="${_CACHE_DIR}/stop-reconcile-${_CACHE_KEY}.result"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < 120 )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

HOOK_NAME="STOP-RECONCILE"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Stderr message on unexpected failure (set -e)
trap 'echo "STOP-RECONCILE FAIL: unexpected error at line $LINENO" >&2' ERR

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

# No changes tracked — nothing to reconcile
[[ ! -f "$CHANGE_LOG" ]] && exit 0

# Extract unique changed files into temp files (avoids unbound array issues)
CODE_TMP=$(mktemp)
DOC_TMP=$(mktemp)
TRACKER_TMP=$(mktemp)
trap 'rm -f "$CODE_TMP" "$DOC_TMP" "$TRACKER_TMP"' EXIT

while IFS='|' read -r _ts _tool fpath; do
  [[ -z "$fpath" ]] && continue
  fpath="${fpath#"$PROJECT_DIR"/}"

  if [[ "$fpath" =~ \.(sh|py|go|rs|ts|js|tsx|jsx|c|h|conf)$ ]]; then
    echo "$fpath" >> "$CODE_TMP"
  elif [[ "$fpath" == docs/reference/*TRACKER* ]] || [[ "$fpath" == docs/reference/*STATUS* ]] || [[ "$fpath" == docs/reference/*MAP* ]]; then
    echo "$fpath" >> "$TRACKER_TMP"
  elif [[ "$fpath" == *.md ]]; then
    echo "$fpath" >> "$DOC_TMP"
  fi
done < "$CHANGE_LOG"

# Deduplicate
sort -u -o "$CODE_TMP" "$CODE_TMP"
sort -u -o "$TRACKER_TMP" "$TRACKER_TMP"

CODE_COUNT=$(wc -l < "$CODE_TMP" | tr -d ' ')
TRACKER_COUNT=$(wc -l < "$TRACKER_TMP" | tr -d ' ')

# If no code files changed, nothing to check
[[ "$CODE_COUNT" -eq 0 ]] && { rm -f "$CHANGE_LOG"; exit 0; }

# Build feedback
FEEDBACK=""

# Check if trackers were updated alongside code
if [[ "$CODE_COUNT" -gt 0 ]] && [[ "$TRACKER_COUNT" -eq 0 ]]; then
  FEEDBACK+="SESSION RECONCILIATION: ${CODE_COUNT} code file(s) changed but no tracker docs updated.\n"
  FEEDBACK+="Changed code files:\n"
  while read -r f; do
    FEEDBACK+="  - $f\n"
  done < "$CODE_TMP"
  FEEDBACK+="\nConsider updating:\n"
  FEEDBACK+="  - docs/reference/FR_TRACKER.md (requirement status)\n"
  FEEDBACK+="  - docs/reference/PLAN_STATUS.md (task progress)\n"
  FEEDBACK+="  - docs/reference/CODE_ENTITY_MAP.md (if new functions added)\n"
fi

# Check CODE_ENTITY_MAP.md for unmapped files — single grep call instead of per-file loop
MAP_FILE="$PROJECT_DIR/docs/reference/CODE_ENTITY_MAP.md"
if [[ -f "$MAP_FILE" ]] && [[ -s "$CODE_TMP" ]]; then
  # Read MAP_FILE once into a variable for bash matching
  MAP_CONTENT=$(<"$MAP_FILE")
  UNMAPPED=""
  while read -r f; do
    [[ -z "$f" ]] && continue
    # Pure bash substring match — zero subprocess spawns
    [[ "$MAP_CONTENT" == *"$f"* ]] || UNMAPPED+="  - $f\n"
  done < "$CODE_TMP"
  if [[ -n "$UNMAPPED" ]]; then
    FEEDBACK+="\nUnmapped code files (not in CODE_ENTITY_MAP.md):\n"
    FEEDBACK+="$UNMAPPED"
  fi
fi

# Clean up session log
rm -f "$CHANGE_LOG"

# If we have feedback, output it as context and cache it
if [[ -n "$FEEDBACK" ]]; then
  _out=$(echo -e "$FEEDBACK")
  echo "$_out"
  # Ultra-fast cache for next time
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  echo "$_out" > "$_CACHE_FILE" 2>/dev/null || true
fi

exit 0
