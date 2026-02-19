#!/usr/bin/env zsh
# Git operation coordination wrapper - solves index.lock contention in multi-tenant environments
# Priority: Cache hit (read-only) → Mutex wait (write) → Native git

# Avoid double-sourcing
[[ -n "${_GIT_WRAPPER_LOADED:-}" ]] && return 0
_GIT_WRAPPER_LOADED=1
THEGENT_TOOL_BIN_PATH="${THEGENT_TOOL_BIN_PATH:-/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin}"
resolve_real_binary() {
  local _bin="$1"
  local _candidate
  _candidate="$(PATH="$THEGENT_TOOL_BIN_PATH" command -v "$_bin" 2>/dev/null || true)"
  if [[ -z "$_candidate" ]]; then
    return 1
  fi
  local _base="${_candidate##*/}"
  if [[ "$_base" == "$_bin" || "$_base" == "$_bin.exe" ]] && [[ "$_candidate" == *"/.local/bin/"* ]]; then
    return 1
  fi
  echo "$_candidate"
  return 0
}

if [[ -z "${THEGENT_GIT_BIN:-}" ]]; then
  THEGENT_GIT_BIN="$(resolve_real_binary git || true)"
fi
export THEGENT_GIT_BIN

git() {
  local cmd="$1"
  [[ -z "$cmd" ]] && {
    if [[ -z "${THEGENT_GIT_BIN:-}" ]]; then
      echo "thegent git-wrapper: unable to resolve real git executable" >&2
      return 127
    fi
    "$THEGENT_GIT_BIN"
    return $?
  }
  shift

  # --- Read-only path: Route to git_cached (5-20x speedup) ---
  case "$cmd" in
    diff|status|ls-files|rev-parse|log|show|name-rev|symbolic-ref|branch|tag|remote|config|ls-tree|cat-file|describe)
      if type git_cached &>/dev/null; then
        git_cached "$cmd" "$@"
        return $?
      fi
      ;;
  esac

  # --- Agent passthrough: codex/copilot/dex/claude/cursor are not git subcommands ---
  # Git would look for git-codex in PATH and fail with "X is not a git command".
  # Exec the agent binary directly (prefer ~/.local/bin shims when in PATH).
  case "$cmd" in
    codex|copilot|dex|claude|cursor)
      local _agent_bin
      # First try to find in safe PATH (avoids git routing)
      _agent_bin="$(PATH="$THEGENT_TOOL_BIN_PATH" command -v "$cmd" 2>/dev/null || true)"
      # If not found, try regular PATH
      [[ -z "$_agent_bin" ]] && _agent_bin="$(command -v "$cmd" 2>/dev/null || true)"
      if [[ -n "$_agent_bin" && -x "$_agent_bin" ]]; then
        exec "$_agent_bin" "$@"
      else
        # Agent not found - emit clear error instead of letting git try
        echo "thegent git-wrapper: $cmd not found in PATH" >&2
        return 127
      fi
      ;;
  esac

  # --- Write path: Handle index.lock contention ---
  # Determine repo root to find .git/index.lock
  local repo_root
  if [[ -z "${THEGENT_GIT_BIN:-}" ]]; then
    echo "thegent git-wrapper: unable to resolve real git executable" >&2
    return 127
  fi
  repo_root=$("$THEGENT_GIT_BIN" rev-parse --show-toplevel 2>/dev/null || echo ".")
  local lock_file="${repo_root}/.git/index.lock"
  
  local max_retries=20
  local retry_count=0
  
  while [[ -f "$lock_file" ]]; do
    # Lock Stealer: If lock is > 10s old, it's likely a crashed process
    local mtime now age
    if [[ "$OSTYPE" == "darwin"* ]]; then
      mtime=$(stat -f %m "$lock_file" 2>/dev/null || echo 0)
    else
      mtime=$(stat -c %Y "$lock_file" 2>/dev/null || echo 0)
    fi
    now=$(date +%s)
    age=$(( now - mtime ))

    if [[ $age -gt 10 ]]; then
      echo "GIT-MUTEX: Stealing stale lock ($age seconds old) from crashed process..." >&2
      rm -f "$lock_file" 2>/dev/null || true
      break
    fi

    # Lock Contention: Wait and retry
    if [[ $retry_count -ge $max_retries ]]; then
      echo "GIT-MUTEX: Max retries reached waiting for git lock ($lock_file). Failing." >&2
      return 128
    fi

    # Adaptive wait: starts small, grows slightly
    local sleep_time
    sleep_time=$(awk "BEGIN {print 0.1 + ($retry_count * 0.1)}")
    
    echo "GIT-MUTEX: Waiting ${sleep_time}s for git index.lock (held by another agent/tenant)..." >&2
    sleep "$sleep_time"
    retry_count=$(( retry_count + 1 ))
  done

  # Invalidate cache on write operations
  case "$cmd" in
    add|commit|checkout|reset|rm|mv|pull|push|merge|rebase|fetch|stash|am|apply)
      [[ -n "${_GIT_CACHE_LOADED:-}" ]] && git_cache_invalidate
      ;;
  esac

  # Execute native git
  "$THEGENT_GIT_BIN" "$cmd" "$@"
}

if [ -n "${BASH_VERSION:-}" ]; then
  export -f git
fi
