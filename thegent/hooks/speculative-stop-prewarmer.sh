#!/bin/zsh
# Speculative Stop Pre-Warmer — PostToolUse:Write|Edit
# Pre-warms caches for Stop hooks after each file edit.
# Uses debouncing to batch rapid edits. Background-forks expensive work.
# Foreground cost: < 50ms (debounce check + fork).
# OPTIMIZED: Skip common.sh when dispatched. Inline debounce logic.

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # Env vars already set: TOOL_NAME, FILE_PATH, PROJECT_DIR
  :
else
  HOOK_NAME="SPECULATIVE_PREWARMER"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

# Only run for Write/Edit events
case "${TOOL_NAME:-}" in
  Write|Edit) ;;
  *) exit 0 ;;
esac

# Skip if no project dir
[[ -d "${PROJECT_DIR:-}" ]] || exit 0

# --- Inline debounce (avoid calling hook_debounce_file which uses flock + awk + sleep) ---
_DEBOUNCE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)/debounce"
_DEBOUNCE_LOCK="${_DEBOUNCE_DIR}/SPECULATIVE_PREWARMER.lock"
mkdir -p "$_DEBOUNCE_DIR" 2>/dev/null || true

# Simple mtime-based debounce: skip if lock file is < 1s old
if [[ -f "$_DEBOUNCE_LOCK" ]]; then
  _lock_age=$(( $(date +%s) - $(stat -f '%m' "$_DEBOUNCE_LOCK" 2>/dev/null || stat -c '%Y' "$_DEBOUNCE_LOCK" 2>/dev/null || echo 0) ))
  (( _lock_age < 1 )) && exit 0
fi
touch "$_DEBOUNCE_LOCK"

# Leader: fork background pre-warming processes
(
  cd "$PROJECT_DIR" || exit 0
  _CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)/shared"
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true

  # Pre-warm shared changed files list
  if [[ ! -f "$_CACHE_DIR/changed_files" ]]; then
    {
      git diff --name-only HEAD 2>/dev/null
      git ls-files --others --exclude-standard 2>/dev/null
    } | sort -u | grep -v -E '^(node_modules|vendor|\.git|target|out|dist|build|coverage|__pycache__)/' > "$_CACHE_DIR/changed_files" 2>/dev/null &
  fi

  # Pre-warm FR index if FR spec exists
  if [[ -f "FUNCTIONAL_REQUIREMENTS.md" && ! -f "$_CACHE_DIR/fr_ids" ]]; then
    grep -oE 'FR-[A-Z]+-[0-9]+' FUNCTIONAL_REQUIREMENTS.md 2>/dev/null | sort -u > "$_CACHE_DIR/fr_ids" &
  fi

  wait
) &

# Foreground exits immediately
exit 0
