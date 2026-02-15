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

# Skip hooks are now loaded from common.sh via _hook_load_skip_hooks


exit $_max_rc
