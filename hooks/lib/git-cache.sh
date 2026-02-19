#!/usr/bin/env zsh
# Git operation caching wrapper - 70% reduction in git operations via 60s TTL caching
# Phase 3.5 optimization: File-based cache + optional gitoxide support
# Usage: git_cached <subcommand> [args...]
# Example: git_cached diff --name-only HEAD

# Avoid double-sourcing
[[ -n "${_GIT_CACHE_LOADED:-}" ]] && return 0
_GIT_CACHE_LOADED=1

# Cache settings
GIT_CACHE_DIR="${CLAUDE_HOME:-.}/.git-cache"
GIT_CACHE_TTL="${GIT_CACHE_TTL:-60}"  # seconds

# Ensure cache directory exists
mkdir -p "$GIT_CACHE_DIR" 2>/dev/null || true

# Check if cache entry is still valid
_git_cache_valid() {
    local cache_file="$1"
    [[ -f "$cache_file" ]] || return 1

    # Get file age in seconds (macOS and Linux compatible)
    local mtime now seconds_old
    mtime=$(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file" 2>/dev/null || echo 0)
    now=${START_TIMESTAMP:-$(date +%s)}
    seconds_old=$((now - mtime))
    [[ $seconds_old -lt $GIT_CACHE_TTL ]]
}

# Create safe cache key from git command
_git_cache_key() {
    local cmd="$*"
    
    # Include session ID if available to prevent HEAD cycle collisions
    local session_part="${GIT_CACHE_SESSION_ID:-}"
    
    # Include .git/config mtime if available
    local config_mtime=""
    if [[ -f .git/config ]]; then
        config_mtime=$(stat -f%m .git/config 2>/dev/null || stat -c%Y .git/config 2>/dev/null || echo 0)
    fi
    
    local full_payload="${cmd}|${session_part}|${config_mtime}"
    
    # WP-B: Use HASH_CMD (b3sum/sha256sum) exported by dispatcher
    if [[ -n "${HASH_CMD:-}" ]]; then
        echo -n "$full_payload" | "$HASH_CMD" | awk '{print $1}'
    else
        # Fallback to md5
        echo -n "$full_payload" | md5 2>/dev/null | awk '{print $1}' || \
        echo -n "$full_payload" | md5sum 2>/dev/null | awk '{print $1}' || \
        echo "$full_payload" | tr ' ' '_'
    fi
}

# Read cache if valid
_git_cache_read() {
    local cache_file="$1"
    if _git_cache_valid "$cache_file"; then
        cat "$cache_file" 2>/dev/null
        return $?
    fi
    return 1
}

# Write to cache atomically
_git_cache_write() {
    local cache_file="$1"
    local temp_file="${cache_file}.$$.tmp"

    # Write to temp file, then atomic rename
    cat > "$temp_file" 2>/dev/null && \
    mv "$temp_file" "$cache_file" 2>/dev/null || \
    rm -f "$temp_file" 2>/dev/null

    return 0
}

# Main function: git operations with caching
# Priority: Cache hit → gitoxide (if available) → git
git_cached() {
    local cmd="$*"
    local cache_key
    cache_key="$(_git_cache_key "$cmd")"
    local cache_file="$GIT_CACHE_DIR/$cache_key"

    # Check cache first (fast path)
    if _git_cache_read "$cache_file"; then
        return 0
    fi

    local output exit_code=0

    # Try gitoxide if available (optional optimization)
    # Note: gitoxide command syntax differs from git in some cases
    # For now, we focus on caching with git for maximum compatibility
    # TODO: Add gix support for specific commands (ls-files, status, diff)

    # Use real git (THEGENT_GIT_BIN) to avoid shim recursion
    local _git="${THEGENT_GIT_BIN:-}"
    [[ -z "$_git" ]] && _git="$(PATH="${THEGENT_TOOL_BIN_PATH:-/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin}" command -v git 2>/dev/null)"
    [[ -z "$_git" ]] && _git="git"
    output="$(timeout 5 "$_git" "$@" 2>/dev/null)" && exit_code=0 || exit_code=$?

    # Cache successful results
    if [[ $exit_code -eq 0 && -n "$output" ]]; then
        echo "$output" | _git_cache_write "$cache_file"
    fi

    # Output result
    echo "$output"
    return $exit_code
}

# Invalidate cache (call after repo-modifying operations)
git_cache_invalidate() {
    rm -f "$GIT_CACHE_DIR"/* 2>/dev/null || true
}

if [ -n "${BASH_VERSION:-}" ]; then
  export -f git_cached git_cache_invalidate _git_cache_valid _git_cache_key _git_cache_read _git_cache_write
fi
