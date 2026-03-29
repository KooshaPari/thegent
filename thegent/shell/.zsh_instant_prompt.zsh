# thegent Instant Prompt System
# Provides p10k-like instant prompt for Starship
# Shows prompt immediately before zsh finishes loading
#
# How it works:
# 1. At shell startup, load cached prompt from previous session
# 2. Print it immediately (user sees instant prompt)
# 3. Redirect stdout/stderr during zsh init (hide loading noise)
# 4. After starship loads, update cache for next session
# 5. Restore stdout/stderr and show full prompt
#
# Based on: Powerlevel10k Instant Prompt
# Adapted for: Starship + thegent shell

# --- Configuration ---
# Set defaults (use := for parameter expansion with default)
: "${THEGENT_INSTANT_PROMPT_CACHE:="${XDG_CACHE_HOME:-$HOME/.cache}/thegent/instant-prompt-${(%):-%n}.zsh"}"
: "${THEGENT_INSTANT_PROMPT_ENABLED:=1}"
: "${THEGENT_INSTANT_PROMPT_VERBOSE:=0}"

# --- Instant Prompt Initialization ---
# This MUST be called at the very top of .zshrc, before ANYTHING else
_thegent_instant_prompt_init() {
    # Skip if disabled
    if [[ "$THEGENT_INSTANT_PROMPT_ENABLED" != "1" ]]; then
        return 0
    fi

    # Skip in non-interactive shells or agents
    if [[ -z "${PS1:-}" || -n "${AGENT_ID:-}" || -n "${heliosShield_AGENT_CONTEXT:-}" ]]; then
        return 0
    fi

    # Check if cache exists and is readable
    if [[ -r "$THEGENT_INSTANT_PROMPT_CACHE" ]]; then
        # Source the cached instant prompt
        # This sets PS1 and redirects stdout/stderr
        source "$THEGENT_INSTANT_PROMPT_CACHE"
        
        # Mark that instant prompt is active
        export THEGENT_INSTANT_PROMPT_ACTIVE=1
        
        if [[ "$THEGENT_INSTANT_PROMPT_VERBOSE" == "1" ]]; then
            echo "thegent: Instant prompt loaded from cache" >&2
        fi
    else
        # No cache yet - create directory for future caching
        mkdir -p "$(dirname "$THEGENT_INSTANT_PROMPT_CACHE")" 2>/dev/null || true
        
        # Set minimal fallback prompt while zsh loads
        PS1='%n@%m %1~ %# '
        
        if [[ "$THEGENT_INSTANT_PROMPT_VERBOSE" == "1" ]]; then
            echo "thegent: No instant prompt cache, using minimal prompt" >&2
        fi
    fi
}

# --- Instant Prompt Finalization ---
# Call this AFTER starship loads to:
# 1. Restore stdout/stderr (if redirected)
# 2. Generate cache for next session
_thegent_instant_prompt_finalize() {
    # Skip if instant prompt wasn't active
    if [[ -z "${THEGENT_INSTANT_PROMPT_ACTIVE:-}" ]]; then
        return 0
    fi

    # Restore stdout/stderr if they were redirected
    if [[ -n "${THEGENT_INSTANT_PROMPT_RESTORE_FD:-}" ]]; then
        exec 1>&3 2>&4 3>&- 4>&- 2>/dev/null || true
        unset THEGENT_INSTANT_PROMPT_RESTORE_FD
    fi

    # Clear the instant prompt active flag
    unset THEGENT_INSTANT_PROMPT_ACTIVE

    # Mark that full prompt is now loaded
    export THEGENT_PROMPT_LOADED=1

    # Generate cache for next session (in background to avoid blocking)
    _thegent_cache_instant_prompt_async
}

# --- Async Cache Generation ---
# Generate instant prompt cache for next session
_thegent_cache_instant_prompt_async() {
    # Run in background to avoid blocking
    (
        # Get current directory info
        local dir="${PWD/#$HOME/~}"
        local user="$USER"
        local host="${HOST%%.*}"
        
        # Create a minimal but useful instant prompt
        # This will be shown immediately on next shell startup
        local cache_content
        cache_content="# thegent Instant Prompt Cache (auto-generated)
# Do not edit - regenerated automatically on each prompt load
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# Directory: $dir

# Set minimal prompt immediately
if [[ -z \"\${THEGENT_PROMPT_LOADED:-}\" ]]; then
  # Print initial prompt line (shows immediately)
  print -P '%n@%m %~ %# '
  
  # Redirect stdout/stderr during zsh init (hide loading noise)
  exec 3>&1 4>&2
  exec 1>/dev/null 2>&1
  
  # Mark that we need to restore FDs later
  export THEGENT_INSTANT_PROMPT_RESTORE_FD=1
  export THEGENT_INSTANT_PROMPT_ACTIVE=1
fi
"
        
        # Write to cache file atomically
        local cache_dir="$(dirname "$THEGENT_INSTANT_PROMPT_CACHE")"
        mkdir -p "$cache_dir" 2>/dev/null || exit 1
        
        # Write to temp file first, then move (atomic)
        local temp_cache="${THEGENT_INSTANT_PROMPT_CACHE}.tmp.$$"
        echo "$cache_content" > "$temp_cache" 2>/dev/null || exit 1
        mv "$temp_cache" "$THEGENT_INSTANT_PROMPT_CACHE" 2>/dev/null || rm -f "$temp_cache"
    ) & disown 2>/dev/null
}

# --- Sync Cache Generation ---
# For when we need to cache immediately (e.g., on first prompt)
_thegent_cache_instant_prompt_sync() {
    # Get current directory info
    local dir="${PWD/#$HOME/~}"
    
    # Create cache content
    local cache_content="# thegent Instant Prompt Cache (auto-generated)
# Do not edit - regenerated automatically
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

if [[ -z \"\${THEGENT_PROMPT_LOADED:-}\" ]]; then
  print -P '%n@%m %~ %# '
  exec 3>&1 4>&2
  exec 1>/dev/null 2>&1
  export THEGENT_INSTANT_PROMPT_RESTORE_FD=1
  export THEGENT_INSTANT_PROMPT_ACTIVE=1
fi
"
    
    # Write to cache
    local cache_dir="$(dirname "$THEGENT_INSTANT_PROMPT_CACHE")"
    mkdir -p "$cache_dir" 2>/dev/null || return 1
    echo "$cache_content" > "$THEGENT_INSTANT_PROMPT_CACHE" 2>/dev/null
}

# --- Clear Cache ---
# Useful for troubleshooting or after config changes
_thegent_instant_prompt_clear_cache() {
    rm -f "$THEGENT_INSTANT_PROMPT_CACHE" 2>/dev/null
    rm -f "${THEGENT_INSTANT_PROMPT_CACHE}".tmp.* 2>/dev/null
    echo "thegent: Instant prompt cache cleared"
}

# --- Status Check ---
_thegent_instant_prompt_status() {
    echo "Instant Prompt Status:"
    echo "  Enabled: ${THEGENT_INSTANT_PROMPT_ENABLED:-0}"
    echo "  Cache: $THEGENT_INSTANT_PROMPT_CACHE"
    echo "  Cache exists: $([[ -f "$THEGENT_INSTANT_PROMPT_CACHE" ]] && echo "yes" || echo "no")"
    echo "  Currently active: ${THEGENT_INSTANT_PROMPT_ACTIVE:-0}"
    echo "  Prompt loaded: ${THEGENT_PROMPT_LOADED:-0}"
}

# --- Auto-Initialize in Interactive Shells Only ---
# Only run initialization in interactive shells
if [[ -n "${PS1:-}" && -z "${AGENT_ID:-}" && -z "${heliosShield_AGENT_CONTEXT:-}" ]]; then
    _thegent_instant_prompt_init
fi

# --- Export Status ---
export THEGENT_INSTANT_PROMPT_LOADED=1
