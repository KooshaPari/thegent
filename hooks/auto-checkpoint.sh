#!/usr/bin/env bash
# Auto-Checkpoint — PreCompact
# Before context compaction, record HEAD SHA and change count for recovery.
# Advisory only — never blocks compaction.
# PERF TARGET: <80ms total (including bash spawn overhead).
# ZERO external subprocesses on hot path (debounce hit).
# 2 stat subprocesses max on cold path (index mtime + ref mtime).

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
else
  HOOK_NAME="AUTO_CHECKPOINT"
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

_pdir="${PROJECT_DIR:-.}"

# Only operate in git repos
[[ -f "$_pdir/.git/HEAD" ]] || exit 0

# --- Debounce: skip if checkpoint written within last 60s (pure bash, no stat) ---
_stamp_file="$_pdir/.claude/.checkpoint-stamp"
printf -v _now_epoch '%(%s)T' -1
if [[ -f "$_stamp_file" ]]; then
  read -r _last_epoch < "$_stamp_file" 2>/dev/null || _last_epoch=0
  if (( _now_epoch - _last_epoch < 60 )); then
    echo "AUTO_CHECKPOINT: skipped (debounce <60s)"
    exit 0
  fi
fi

# --- Read git state directly from .git files (zero subprocesses) ---
HEAD_SHA="unknown"
BRANCH="unknown"
read -r _head_line < "$_pdir/.git/HEAD" 2>/dev/null || true
if [[ "$_head_line" == ref:* ]]; then
  BRANCH="${_head_line#ref: refs/heads/}"
  _ref_path="$_pdir/.git/${_head_line#ref: }"
  if [[ -f "$_ref_path" ]]; then
    read -r HEAD_SHA < "$_ref_path" 2>/dev/null || true
  elif [[ -f "$_pdir/.git/packed-refs" ]]; then
    _target_ref="${_head_line#ref: }"
    while IFS=' ' read -r _sha _ref; do
      [[ "$_ref" == "$_target_ref" ]] && { HEAD_SHA="$_sha"; break; }
    done < "$_pdir/.git/packed-refs"
  fi
else
  HEAD_SHA="$_head_line"
fi

# --- Detect changes via .git/index mtime heuristic (2 stat calls max) ---
has_changes=false
if [[ -f "$_pdir/.git/index" ]]; then
  _idx_mtime=$(stat -f%m "$_pdir/.git/index" 2>/dev/null || stat -c%Y "$_pdir/.git/index" 2>/dev/null) || _idx_mtime=0
  if [[ "$_head_line" == ref:* && -f "${_ref_path:-}" ]]; then
    _ref_mtime=$(stat -f%m "$_ref_path" 2>/dev/null || stat -c%Y "$_ref_path" 2>/dev/null) || _ref_mtime=0
  else
    _ref_mtime=0
  fi
  (( _idx_mtime > _ref_mtime + 2 )) && has_changes=true
fi

# --- Write checkpoint + debounce stamp ---
[[ -d "$_pdir/.claude" ]] || mkdir -p "$_pdir/.claude" 2>/dev/null || true

printf '{"timestamp":"%s","head_sha":"%s","branch":"%s","has_uncommitted_changes":%s}\n' \
  "$now" "$HEAD_SHA" "$BRANCH" "$has_changes" \
  > "$_pdir/.claude/last-checkpoint"

printf '%s\n' "$_now_epoch" > "$_stamp_file"

echo "AUTO_CHECKPOINT: HEAD=${HEAD_SHA:0:8} branch=$BRANCH changes=$has_changes"

exit 0
