#!/usr/bin/env bash
# PreToolUse Dispatcher -- single-process orchestrator for PreToolUse hooks.
# Sources and runs all applicable hooks INLINE (no subprocess spawns per hook).
# Runs hooks SEQUENTIALLY because PreToolUse hooks are blocking.
#
# For Write events:  doc-location-guard -> pre-write-validator -> suppression-blocker
# For Edit events:   pre-write-validator -> suppression-blocker
#
# Optimization: sources common.sh, runs hook_init_full ONCE (single jq call,
# zero base64 -- extracts both init fields and content in one pass).
# Sub-hooks detect _HOOK_DISPATCHED and skip re-parsing.

_dispatch_tmpdir=$(mktemp -d)
trap 'rm -rf "$_dispatch_tmpdir"' EXIT

# Save stdin for replay
cat > "$_dispatch_tmpdir/input.json"

HOOKS_DIR="${BASH_SOURCE[0]%/*}"

# --- Parse input once via common.sh (single jq call for all fields) ---
HOOK_NAME="PRETOOL-DISPATCHER"
source "${HOOKS_DIR}/lib/common.sh"
hook_init_full < "$_dispatch_tmpdir/input.json"

# Mark dispatched so sub-hooks skip re-parsing
export _HOOK_DISPATCHED=1
export TOOL_NAME FILE_PATH PROJECT_DIR SESSION_ID INPUT
export CWD STOP_ACTIVE VERIFY_DIR QA_STATE QUALITY_CONFIG CHANGE_LOG
export TOOL_CONTENT TOOL_NEW_STRING TOOL_OLD_STRING
export JQ_CMD TIMEOUT_CMD

# --- Determine which hooks to run based on tool name ---
declare -a HOOKS_TO_RUN=()

case "$TOOL_NAME" in
  Write)
    HOOKS_TO_RUN=(
      doc-location-guard.sh
      pre-write-validator.sh
      suppression-blocker.sh
    )
    ;;
  Edit)
    HOOKS_TO_RUN=(
      pre-write-validator.sh
      suppression-blocker.sh
    )
    ;;
  *)
    exit 0
    ;;
esac

# --- Run hooks sequentially; stop on first failure ---
# Use subshell per hook so `exit` in the hook doesn't kill the dispatcher,
# but avoid full `bash` process spawn by using ( source ... ) pattern.
for hook in "${HOOKS_TO_RUN[@]}"; do
  hook_path="${HOOKS_DIR}/${hook}"
  [[ -f "$hook_path" ]] || continue

  # Run in subshell (fork only, no exec — shares parent's env instantly)
  ( source "$hook_path" ) < "$_dispatch_tmpdir/input.json"
  rc=$?

  if (( rc != 0 )); then
    exit $rc
  fi
done

exit 0
