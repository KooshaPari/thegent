#!/usr/bin/env bash
# PostToolUse Dispatcher -- single-process orchestrator for all PostToolUse hooks.
# Sources common.sh ONCE and runs all hooks in PARALLEL subshells.
# Uses ( source ) instead of bash to avoid exec overhead.
# PostToolUse hooks are advisory (non-blocking), so we never fail-closed.

_dispatch_tmpdir=$(mktemp -d)
trap 'rm -rf "$_dispatch_tmpdir"' EXIT

# Save stdin for replay
cat > "$_dispatch_tmpdir/input.json"

HOOKS_DIR="${BASH_SOURCE[0]%/*}"

# Timeout per hook (seconds)
HOOK_TIMEOUT=15

# Source common.sh and run hook_init_full ONCE (single jq call for all fields)
HOOK_NAME="POSTTOOL-DISPATCHER"
# shellcheck source=./lib/common.sh
source "${HOOKS_DIR}/lib/common.sh"
hook_init_full < "$_dispatch_tmpdir/input.json"

# Mark dispatched so sub-hooks skip re-parsing
export _HOOK_DISPATCHED=1
export INPUT CWD SESSION_ID TOOL_NAME FILE_PATH STOP_ACTIVE
export PROJECT_DIR VERIFY_DIR QA_STATE QUALITY_CONFIG CHANGE_LOG
export TOOL_CONTENT TOOL_NEW_STRING TOOL_OLD_STRING
export HOOK_CACHE_DIR HOOK_SHARED_DIR
export JQ_CMD HUNIQ_CMD TIMEOUT_CMD

# Use the already-detected timeout command
_TIMEOUT_CMD="${TIMEOUT_CMD:-}"

# All PostToolUse hooks (all run in parallel -- advisory only)
POSTTOOL_HOOKS=(
  change-doc-tracker.sh
  qa-evidence-recorder.sh
  qa-policy-test.sh
  post-edit-checker.sh
  agent-antipattern-detector.sh
  async-test-runner.sh
  speculative-stop-prewarmer.sh
)

for hook in "${POSTTOOL_HOOKS[@]}"; do
  hook_path="${HOOKS_DIR}/${hook}"
  [[ -f "$hook_path" ]] || continue
  (
    if [[ -n "${_TIMEOUT_CMD:-}" ]]; then
      "$_TIMEOUT_CMD" "$HOOK_TIMEOUT" bash -c "source '$hook_path'" < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" \
        2>"$_dispatch_tmpdir/${hook}.err"
    else
      ( source "$hook_path" ) < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" \
        2>"$_dispatch_tmpdir/${hook}.err"
    fi
    echo $? > "$_dispatch_tmpdir/${hook}.rc"
  ) &
done

wait

# Collect results (advisory only -- never fail-closed)
_failed_hooks=""
for hook in "${POSTTOOL_HOOKS[@]}"; do
  rc_file="$_dispatch_tmpdir/${hook}.rc"
  [[ -f "$rc_file" ]] || continue

  rc=$(cat "$rc_file" 2>/dev/null)
  [[ "$rc" =~ ^[0-9]+$ ]] || rc=1

  [[ -s "$_dispatch_tmpdir/${hook}.out" ]] && cat "$_dispatch_tmpdir/${hook}.out"
  [[ -s "$_dispatch_tmpdir/${hook}.err" ]] && cat "$_dispatch_tmpdir/${hook}.err" >&2

  if (( rc > 0 )); then
    _failed_hooks="${_failed_hooks:+${_failed_hooks}; }${hook%.sh}(rc=${rc})"
  fi
done

if [[ -n "$_failed_hooks" ]]; then
  echo "POSTTOOL DISPATCHER: advisory failures: ${_failed_hooks}" >&2
fi

exit 0
