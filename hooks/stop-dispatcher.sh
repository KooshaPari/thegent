#!/bin/zsh
# Stop Dispatcher -- single-process orchestrator for all Stop hooks.
# Reads stdin (Claude Code's JSON payload) once and replays it to each
# hook via file redirect, then runs all Stop hooks in parallel.
# Eliminates N x bash-startup overhead: Claude Code spawns 1 process
# instead of 9, and the hooks still run concurrently internally.

_dispatch_tmpdir=$(mktemp -d)
trap 'rm -rf "$_dispatch_tmpdir"' EXIT

# Save stdin (Claude Code's JSON payload) for replay to each hook
cat > "$_dispatch_tmpdir/input.json"

HOOKS_DIR="${BASH_SOURCE[0]%/*}"

# Source common.sh for shared logic (skip hooks, timeout config)
# shellcheck disable=SC1091
[[ -f "${HOOKS_DIR}/lib/common.sh" ]] && source "${HOOKS_DIR}/lib/common.sh"

# Timeout per hook (seconds) — prevent any single hook from blocking Stop
# Use idle timeout from common.sh if available, else default
HOOK_TIMEOUT="${HOOK_IDLE_TIMEOUT:-60}"

# --- Pre-compute expensive git state ONCE (saves ~52ms x 9 hooks) ---
# Extract project_dir from the saved JSON payload for git operations
_dispatch_project_dir="$(cd "$HOOKS_DIR" && cat "$_dispatch_tmpdir/input.json" \
  | grep -oE '"(cwd|project_dir|workspace)"\s*:\s*"[^"]*"' | head -1 | sed 's/"[^"]*"[[:space:]]*:[[:space:]]*"//;s/"$//' 2>/dev/null || true)"
if [[ -n "$_dispatch_project_dir" && -d "$_dispatch_project_dir" ]]; then
  _dispatch_git_dir="$_dispatch_project_dir"
else
  _dispatch_git_dir="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

# Ensure PROJECT_DIR is always set for child hooks
export PROJECT_DIR="$_dispatch_git_dir"
export VERIFY_DIR="$PROJECT_DIR/.claude/verification"
export QA_STATE="$PROJECT_DIR/.claude/qa-state.json"

# All Stop hooks
STOP_HOOKS=(
  quality-gate.sh
  security-pipeline.sh
  complexity-ratchet.sh
  spec-verifier.sh
  test-maturity.sh
  task-completion-verifier.sh
  stop-reconcile.sh
  agileplus-cycle.sh
)

_max_rc=0
for hook in "${STOP_HOOKS[@]}"; do
  hook_path="${HOOKS_DIR}/${hook}"
  [[ -f "$hook_path" ]] || continue
  
  (
    # Run hook with timeout if available
    if command -v timeout >/dev/null 2>&1; then
      timeout "$HOOK_TIMEOUT" bash "$hook_path" < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" 2>"$_dispatch_tmpdir/${hook}.err"
    else
      bash "$hook_path" < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" 2>"$_dispatch_tmpdir/${hook}.err"
    fi
    echo $? > "$_dispatch_tmpdir/${hook}.rc"
  ) &
done

wait

# Collect output and determine max exit code
for hook in "${STOP_HOOKS[@]}"; do
  [[ -f "$_dispatch_tmpdir/${hook}.rc" ]] || continue
  rc=$(cat "$_dispatch_tmpdir/${hook}.rc")
  [[ "$rc" -gt $_max_rc ]] && _max_rc=$rc
  
  # Print stdout if not empty
  [[ -s "$_dispatch_tmpdir/${hook}.out" ]] && cat "$_dispatch_tmpdir/${hook}.out"
  # Print stderr if not empty
  [[ -s "$_dispatch_tmpdir/${hook}.err" ]] && cat "$_dispatch_tmpdir/${hook}.err" >&2
done

NOTIFIER="${HOOKS_DIR}/notify-agent-event.sh"
if [[ -x "$NOTIFIER" ]]; then
  if [[ "$_max_rc" -eq 0 ]]; then
    "$NOTIFIER" --event "stop" --severity "info" --title "Stop Complete" \
      --message "legacy stop-dispatcher completed successfully" >/dev/null 2>&1 || true
  else
    "$NOTIFIER" --event "stop" --severity "error" --title "Stop Issues" \
      --message "legacy stop-dispatcher returned rc=${_max_rc}" >/dev/null 2>&1 || true
  fi
fi

exit $_max_rc
