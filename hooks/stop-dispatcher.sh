#!/usr/bin/env bash
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

# Timeout per hook (seconds) — prevent any single hook from blocking Stop
HOOK_TIMEOUT=60

# --- Pre-compute expensive git state ONCE (saves ~52ms x 9 hooks) ---
# Extract project_dir from the saved JSON payload for git operations
_dispatch_project_dir="$(cd "$HOOKS_DIR" && cat "$_dispatch_tmpdir/input.json" \
  | grep -oE '"(cwd|project_dir|workspace)"\s*:\s*"[^"]*"' | head -1 | sed 's/"[^"]*"[[:space:]]*:[[:space:]]*"//;s/"$//' 2>/dev/null || true)"
if [[ -n "$_dispatch_project_dir" && -d "$_dispatch_project_dir" ]]; then
  _dispatch_git_dir="$_dispatch_project_dir"
else
  _dispatch_git_dir="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

# Ensure PROJECT_DIR is always set for child hooks (prevents /.claude/verification path bugs)
# Fallback chain: extracted dir -> git root -> BASH_SOURCE path -> HOME
if [[ -z "$_dispatch_git_dir" || "$_dispatch_git_dir" == "/" ]]; then
  if [[ "${BASH_SOURCE[0]}" == *".claude/hooks"* ]]; then
    _dispatch_git_dir="${BASH_SOURCE[0]%/.claude/hooks/*}"
  fi
fi
if [[ -z "$_dispatch_git_dir" || "$_dispatch_git_dir" == "/" ]]; then
  _dispatch_git_dir="${HOME:-$(pwd)}"
fi
export PROJECT_DIR="$_dispatch_git_dir"
export VERIFY_DIR="$PROJECT_DIR/.claude/verification"
export QA_STATE="$PROJECT_DIR/.claude/qa-state.json"

export HEAD_SHA
HEAD_SHA="$(cd "$_dispatch_git_dir" && git rev-parse HEAD 2>/dev/null || echo "unknown")"

export CHANGED_FILES
CHANGED_FILES="$(cd "$_dispatch_git_dir" && git diff --name-only HEAD 2>/dev/null || true)"

export CHANGED_FILES_SORTED
CHANGED_FILES_SORTED="$(echo "$CHANGED_FILES" | sort)"

export STOP_DISPATCH_ACTIVE=1
unset _dispatch_project_dir _dispatch_git_dir

# Detect timeout command
if command -v gtimeout >/dev/null 2>&1; then
  _TIMEOUT_CMD=gtimeout
elif command -v timeout >/dev/null 2>&1; then
  _TIMEOUT_CMD=timeout
else
  _TIMEOUT_CMD=""
fi

# All Stop hooks to dispatch (order is irrelevant -- all run in parallel)
STOP_HOOKS=(
  governance-gates.sh
  qa-supply-chain-verifier.sh
  quality-gate.sh
  complexity-ratchet.sh
  security-pipeline.sh
  spec-verifier.sh
  test-maturity.sh
  stop-reconcile.sh
  task-completion-verifier.sh
)

for hook in "${STOP_HOOKS[@]}"; do
  hook_path="${HOOKS_DIR}/${hook}"
  [[ -f "$hook_path" ]] || continue
  (
    export PROJECT_DIR VERIFY_DIR QA_STATE
    if [[ -n "${_TIMEOUT_CMD:-}" ]]; then
      "$_TIMEOUT_CMD" "$HOOK_TIMEOUT" env PROJECT_DIR="$PROJECT_DIR" VERIFY_DIR="$VERIFY_DIR" QA_STATE="$QA_STATE" bash "$hook_path" < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" \
        2>"$_dispatch_tmpdir/${hook}.err"
    else
      env PROJECT_DIR="$PROJECT_DIR" VERIFY_DIR="$VERIFY_DIR" QA_STATE="$QA_STATE" bash "$hook_path" < "$_dispatch_tmpdir/input.json" \
        > "$_dispatch_tmpdir/${hook}.out" \
        2>"$_dispatch_tmpdir/${hook}.err"
    fi
    echo $? > "$_dispatch_tmpdir/${hook}.rc"
  ) &
done

wait

# Collect results: print outputs and track highest exit code
_max_rc=0
_failed_hooks=""
for hook in "${STOP_HOOKS[@]}"; do
  rc_file="$_dispatch_tmpdir/${hook}.rc"

  # Hook didn't run (file not found) — skip
  [[ -f "$rc_file" ]] || continue

  rc=$(cat "$rc_file" 2>/dev/null)
  # Guard against empty or non-numeric rc
  [[ "$rc" =~ ^[0-9]+$ ]] || rc=1

  # Print stdout (advisory output from hooks)
  [[ -s "$_dispatch_tmpdir/${hook}.out" ]] && cat "$_dispatch_tmpdir/${hook}.out"

  # Print stderr
  [[ -s "$_dispatch_tmpdir/${hook}.err" ]] && cat "$_dispatch_tmpdir/${hook}.err" >&2

  # Track failures
  if (( rc > 0 )); then
    _failed_hooks="${_failed_hooks:+${_failed_hooks}; }${hook%.sh}(rc=${rc})"
    (( rc > _max_rc )) && _max_rc=$rc
  fi
done

# Emit dispatcher-level stderr so Claude Code shows a useful message
if (( _max_rc > 0 )); then
  echo "STOP DISPATCHER: non-zero from: ${_failed_hooks}" >&2
fi

exit $_max_rc
