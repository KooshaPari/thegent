#!/bin/zsh
# P8: Background daemon — pre-warm caches on file system changes.
# Polls for changes every 5s; invalidates shared cache and pre-warms when files change.
# Run: hooks/hook-watcher.sh [project_dir] &
# Started by qa-preflight when daemon_mode: true
set -euo pipefail

PROJECT_DIR="${1:-.}"
[[ -d "$PROJECT_DIR" ]] || PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_DIR" || exit 1

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_LIB="${HOOK_DIR}/lib"
# shellcheck source=./lib/common.sh
source "${HOOK_LIB}/common.sh"
export PROJECT_DIR
hook_init 2>/dev/null || true

CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
SHARED_DIR="${CACHE_DIR}/shared"
LAST_HASH_FILE="${CACHE_DIR}/watcher_last_hash"
PID_FILE="${CACHE_DIR}/hook_watcher.pid"
INTERVAL="${HOOK_WATCHER_INTERVAL:-5}"

_get_changed_hash() {
  {
    git diff --name-only HEAD 2>/dev/null
    git ls-files --others --exclude-standard 2>/dev/null
  } | grep -v -E '^(node_modules|vendor|\.git|target|out|dist|build|coverage|__pycache__)/' \
    | sort -u | hash_for_cache 2>/dev/null || echo "none"
}

# Single-instance: exit if already running
if [[ -f "$PID_FILE" ]]; then
  old_pid=$(cat "$PID_FILE" 2>/dev/null)
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    exit 0
  fi
fi
echo $$ > "$PID_FILE"

while true; do
  current="$(_get_changed_hash)"
  if [[ -f "$LAST_HASH_FILE" ]]; then
    last=$(cat "$LAST_HASH_FILE")
    if [[ "$current" != "$last" ]]; then
      rm -f "${SHARED_DIR}/changed_files" 2>/dev/null || true
      rm -f "${SHARED_DIR}/fr_ids" "${SHARED_DIR}/fr_index" 2>/dev/null || true
      hook_prewarm_all 2>/dev/null || true
    fi
  fi
  echo "$current" > "$LAST_HASH_FILE"
  sleep "$INTERVAL"
done
