#!/usr/bin/env bash
# disk-hygiene.sh — WL-006 standalone disk hygiene script for thegent
#
# Usage: ./scripts/disk-hygiene.sh [--dry-run] [--project-root PATH]
#        [--max-age-days N] [--disk-threshold PCT]
#
# Cleans stale thegent cache dirs, bounded to the project root.
# Safe to run manually or via cron: 0 3 * * * /path/to/thegent/scripts/disk-hygiene.sh
#
# What it removes (default: dirs older than 7 days):
#   .shadow-*      Quality gate shadow workdirs created by jscpd / gitleaks scans
#   .git-cache     Git operation caches created by Rust crates in crates/
#   .worktrees     Ephemeral git worktrees used during parallel agent work
#
# Exit codes:
#   0  — clean run (or dry-run)
#   1  — disk usage above threshold (reported but does NOT abort the script)
#   2  — invalid arguments
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults (all overridable via env or flags)
# ---------------------------------------------------------------------------
DRY_RUN=0
PROJECT_ROOT=""
MAX_AGE_DAYS="${CACHE_MAX_AGE_DAYS:-7}"
DISK_THRESHOLD="${DISK_USAGE_ABORT_PCT:-90}"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --max-age-days)
      MAX_AGE_DAYS="$2"
      shift 2
      ;;
    --disk-threshold)
      DISK_THRESHOLD="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,/^set /p' "$0" | grep '^#' | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      echo "Usage: $0 [--dry-run] [--project-root PATH] [--max-age-days N] [--disk-threshold PCT]" >&2
      exit 2
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Resolve project root — default to directory containing this script's parent
# ---------------------------------------------------------------------------
_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -z "$PROJECT_ROOT" ]]; then
  PROJECT_ROOT="$(cd "$_SCRIPT_DIR/.." && pwd)"
fi

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "ERROR: project root does not exist: $PROJECT_ROOT" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_log() { echo "[disk-hygiene] $*" >&2; }

_log_dry() { echo "[disk-hygiene] [dry-run] $*" >&2; }

_remove_dir() {
  local dir="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    _log_dry "would remove: $dir"
  else
    _log "removing: $dir"
    rm -rf -- "$dir"
  fi
}

# ---------------------------------------------------------------------------
# Disk usage check
# ---------------------------------------------------------------------------
_disk_usage_pct() {
  df -P "$1" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}'
}

disk_pct="$(_disk_usage_pct "$PROJECT_ROOT")"
_DISK_OVER_THRESHOLD=0

if [[ -n "$disk_pct" ]]; then
  _log "disk usage: ${disk_pct}% (threshold: ${DISK_THRESHOLD}%)"
  if [[ "$disk_pct" -ge "$DISK_THRESHOLD" ]]; then
    _log "WARNING: disk usage ${disk_pct}% exceeds threshold ${DISK_THRESHOLD}% — immediate cleanup required"
    _DISK_OVER_THRESHOLD=1
  fi
else
  _log "WARNING: could not determine disk usage for $PROJECT_ROOT"
fi

# ---------------------------------------------------------------------------
# Prune stale cache directories
# ---------------------------------------------------------------------------
_PATTERNS=(".shadow-*" ".git-cache" ".worktrees")
_total_pruned=0
_total_bytes=0

_log "scanning $PROJECT_ROOT for stale cache dirs (maxdepth=4, mtime >+${MAX_AGE_DAYS}d)"

for pattern in "${_PATTERNS[@]}"; do
  while IFS= read -r dir; do
    [[ -d "$dir" ]] || continue
    # Compute size before removal (best-effort; du may fail on some systems)
    _size="$(du -sk "$dir" 2>/dev/null | awk '{print $1}' || echo 0)"
    _total_bytes=$((_total_bytes + _size))
    _remove_dir "$dir"
    _total_pruned=$((_total_pruned + 1))
  done < <(find "$PROJECT_ROOT" -maxdepth 4 -name "$pattern" -type d \
             -mtime +"$MAX_AGE_DAYS" 2>/dev/null || true)
done

# ---------------------------------------------------------------------------
# Reset quality-gate attempt counters written by governance-gates.sh / Taskfile
# These counters are per-session sentinels; clearing them ensures a clean slate.
# ---------------------------------------------------------------------------
_ATTEMPT_FILES=(
  "${TMPDIR:-/tmp}/.quality-gate-attempts"
  "${TMPDIR:-/tmp}/.gg-attempt-count"
  "${XDG_CACHE_HOME:-$HOME/.cache}/thegent/.gg-attempt-count"
)

for f in "${_ATTEMPT_FILES[@]}"; do
  if [[ -f "$f" ]]; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      _log_dry "would reset attempt counter: $f"
    else
      rm -f "$f"
      _log "reset attempt counter: $f"
    fi
  fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
_log "done: pruned ${_total_pruned} dir(s), ~${_total_bytes}KB freed"

if [[ "$DRY_RUN" -eq 1 ]]; then
  _log "(dry-run mode — no files were removed)"
fi

# Exit 1 if disk was over threshold even after cleanup (caller can decide)
if [[ "$_DISK_OVER_THRESHOLD" -eq 1 ]]; then
  _post_pct="$(_disk_usage_pct "$PROJECT_ROOT")"
  _log "post-cleanup disk usage: ${_post_pct:-unknown}%"
  exit 1
fi

exit 0
