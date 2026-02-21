#!/bin/zsh
# Hook: SessionEnd
# Purpose: Clean up session-level state, prune stale cache dirs, and finalize
#          any pending tracker updates.
# WL-006: Adds prune_stale_caches() to remove dirs older than 7 days, and a
#         disk-usage abort guard that prevents quality-gate runs when disk > 90%.
set -euo pipefail

# Stderr message on unexpected failure (set -e)
trap 'echo "SESSION-CLEANUP FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  CHANGE_LOG="${PROJECT_DIR:-.}/.claude/session-changes.log"
  QA_STATE="${PROJECT_DIR:-.}/.claude/qa-state.json"
else
  HOOK_NAME="SESSION-CLEANUP"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

# =============================================================================
# WL-006: Disk-usage abort guard
# Aborts the quality gate phase if the filesystem containing PROJECT_DIR is
# more than 90% full.  Prevents scan tools from compounding a nearly-full disk.
# =============================================================================
_check_disk_usage() {
  local target_dir="${PROJECT_DIR:-.}"
  local threshold="${DISK_USAGE_ABORT_PCT:-90}"

  # df -P is POSIX; pick the "Use%" column from the line for the target mount.
  local pct
  pct="$(df -P "$target_dir" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')"
  if [[ -z "$pct" ]]; then
    echo "SESSION-CLEANUP: could not determine disk usage for $target_dir — skipping disk check" >&2
    return 0
  fi

  if [[ "$pct" -ge "$threshold" ]]; then
    echo "SESSION-CLEANUP FAIL: disk usage ${pct}% >= ${threshold}% threshold on $target_dir — aborting quality gate to prevent disk saturation" >&2
    # Write a sentinel so governance-gates.sh can detect this condition.
    local sentinel="${HOOK_CACHE_DIR:-/tmp}/.disk-saturation-abort"
    echo "disk_pct=${pct} threshold=${threshold} ts=$(date +%s)" > "$sentinel"
    return 1
  fi

  echo "SESSION-CLEANUP: disk usage ${pct}% — within threshold (${threshold}%)" >&2
  return 0
}

# =============================================================================
# WL-006: Prune stale cache directories
# Removes .shadow-*, .git-cache, and temp worktree dirs older than 7 days.
# Bounded to PROJECT_DIR to prevent cross-project damage.
# =============================================================================
prune_stale_caches() {
  local base_dir="${PROJECT_DIR:-.}"
  local max_age_days="${CACHE_MAX_AGE_DAYS:-7}"
  local dry_run="${CACHE_PRUNE_DRY_RUN:-0}"
  local pruned=0

  echo "SESSION-CLEANUP: pruning stale caches older than ${max_age_days}d in ${base_dir}" >&2

  # Patterns matching dirs created by quality gate and worktree tooling.
  local -a patterns=(".shadow-*" ".git-cache" ".worktrees")

  for pattern in "${patterns[@]}"; do
    # Use find with -maxdepth 3 to keep scope bounded.
    while IFS= read -r dir; do
      [[ -d "$dir" ]] || continue
      if [[ "$dry_run" == "1" ]]; then
        echo "SESSION-CLEANUP [dry-run]: would remove $dir" >&2
      else
        echo "SESSION-CLEANUP: removing stale cache dir $dir" >&2
        rm -rf -- "$dir"
      fi
      pruned=$((pruned + 1))
    done < <(find "$base_dir" -maxdepth 3 -name "$pattern" -type d \
               -mtime +"$max_age_days" 2>/dev/null || true)
  done

  # Also clean the attempt-count sentinel files written by governance-gates.sh
  # and the Taskfile quality gate so the next session starts with a fresh count.
  local attempt_files=(
    "${HOOK_CACHE_DIR:-/tmp}/.gg-attempt-count"
    "${TMPDIR:-/tmp}/.quality-gate-attempts"
  )
  for f in "${attempt_files[@]}"; do
    if [[ -f "$f" ]]; then
      rm -f "$f"
      echo "SESSION-CLEANUP: reset attempt counter $f" >&2
    fi
  done

  echo "SESSION-CLEANUP: pruned ${pruned} stale cache dir(s)" >&2
}

# --- Run disk check before any quality-gate invocations at session end ---
_check_disk_usage || {
  echo "SESSION-CLEANUP: disk saturation detected — session cleanup proceeds but quality gate is suppressed" >&2
}

# --- Prune stale caches ---
prune_stale_caches

# Clean up session change log if it wasn't consumed by stop hook
rm -f "${CHANGE_LOG:-}" 2>/dev/null || true

# Clean up qa-state.json (ephemeral per-session, written by qa-preflight)
rm -f "${QA_STATE:-}" 2>/dev/null || true

NOTIFIER="${BASH_SOURCE[0]%/*}/notify-agent-event.sh"
if [[ -x "$NOTIFIER" ]]; then
  "$NOTIFIER" \
    --event "sessionend" \
    --severity "info" \
    --title "Session Ended" \
    --message "Session cleanup complete for ${PROJECT_DIR:-.}" \
    >/dev/null 2>&1 || true
fi

exit 0
