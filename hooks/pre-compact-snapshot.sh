#!/usr/bin/env bash
# pre-compact-snapshot.sh — PreCompact hook
# Snapshots current quality state before context compression.
# Advisory only (always exits 0).
# PERF TARGET: <80ms total (including bash spawn overhead).
# ZERO external subprocesses on hot path (debounce hit).
# 1 subprocess max on cold path (stat for session log size, if file exists).

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
  CHANGE_LOG="${PROJECT_DIR:-.}/.claude/session-changes.log"
else
  HOOK_NAME="PRE-COMPACT-SNAPSHOT"
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

SNAPSHOT_FILE="$HOME/.claude/.pre-compact-state.json"
_STAMP_FILE="$HOME/.claude/.pre-compact-stamp"

# --- Debounce: skip if ran within last 60s (pure bash, no stat subprocess) ---
printf -v _now_epoch '%(%s)T' -1
if [[ -f "$_STAMP_FILE" ]]; then
  read -r _last_epoch < "$_STAMP_FILE" 2>/dev/null || _last_epoch=0
  if (( _now_epoch - _last_epoch < 60 )); then
    echo "Pre-compact snapshot: skipped (debounce <60s)"
    exit 0
  fi
fi

# --- Gather state (zero git subprocesses) ---

# Session change count: approximate from file size (1 stat subprocess, only if file exists)
SESSION_CHANGE_COUNT=0
if [[ -s "${CHANGE_LOG:-}" ]]; then
  _cl_size=$(stat -f%z "$CHANGE_LOG" 2>/dev/null || stat -c%s "$CHANGE_LOG" 2>/dev/null) || _cl_size=0
  SESSION_CHANGE_COUNT=$(( _cl_size / 80 ))
  (( SESSION_CHANGE_COUNT < 1 && _cl_size > 0 )) && SESSION_CHANGE_COUNT=1
fi

# Presence checks (no jq, no subshells)
_qg=false; [[ -f "$HOME/.claude/.quality-gate-result.json" ]] && _qg=true
_tr=false; [[ -f "$HOME/.claude/.async-test-results.json" ]] && _tr=true
_sv=false; [[ -f "$HOME/.claude/.spec-verification.json" ]] && _sv=true

# Git: read HEAD and branch directly from .git files (no subprocess)
_pdir="${PROJECT_DIR:-.}"
GIT_BRANCH="unknown"
GIT_HEAD="unknown"
if [[ -f "$_pdir/.git/HEAD" ]]; then
  read -r _head_line < "$_pdir/.git/HEAD" 2>/dev/null || true
  if [[ "$_head_line" == ref:* ]]; then
    GIT_BRANCH="${_head_line#ref: refs/heads/}"
    if [[ -f "$_pdir/.git/${_head_line#ref: }" ]]; then
      read -r GIT_HEAD < "$_pdir/.git/${_head_line#ref: }" 2>/dev/null || true
      GIT_HEAD="${GIT_HEAD:0:8}"
    elif [[ -f "$_pdir/.git/packed-refs" ]]; then
      while IFS=' ' read -r _sha _ref; do
        [[ "$_ref" == "${_head_line#ref: }" ]] && { GIT_HEAD="${_sha:0:8}"; break; }
      done < "$_pdir/.git/packed-refs"
    fi
  else
    GIT_HEAD="${_head_line:0:8}"
  fi
fi

# --- Write snapshot + debounce stamp ---
_esc_pdir="${_pdir//\\/\\\\}"; _esc_pdir="${_esc_pdir//\"/\\\"}"
_esc_branch="${GIT_BRANCH//\\/\\\\}"; _esc_branch="${_esc_branch//\"/\\\"}"

printf '{"timestamp":"%s","project_dir":"%s","session_change_count":%s,"git_branch":"%s","git_head":"%s","quality_gate_present":%s,"test_results_present":%s,"spec_verification_present":%s}\n' \
  "$now" "$_esc_pdir" "$SESSION_CHANGE_COUNT" "$_esc_branch" "$GIT_HEAD" "$_qg" "$_tr" "$_sv" \
  > "$SNAPSHOT_FILE"

# Write debounce stamp (epoch seconds, pure bash readable)
printf '%s\n' "$_now_epoch" > "$_STAMP_FILE"

# Copy session-changes.log as backup (background, fire-and-forget)
[[ -f "${CHANGE_LOG:-}" ]] && cp "$CHANGE_LOG" "$HOME/.claude/.pre-compact-changes.log" 2>/dev/null &

# --- Output ---
echo "Quality state snapshot saved for context preservation"
echo "  Session changes: $SESSION_CHANGE_COUNT | Git: $GIT_BRANCH @ $GIT_HEAD"
[[ "$_qg" == "true" ]] && echo "  Quality gate: present"
[[ "$_tr" == "true" ]] && echo "  Test results: present"
[[ "$_sv" == "true" ]] && echo "  Spec verification: present"

exit 0
