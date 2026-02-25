# thegent Shell Optimization System
# Comprehensive performance optimization for shell startup and runtime
# Implements: lazy loading, eval caching, parallel loading, profiling

# Only load in interactive shells
[[ -z "${PS1:-}" || -n "${AGENT_ID:-}" || -n "${heliosShield_AGENT_CONTEXT:-}" ]] && return 0

# --- Configuration ---
THEGENT_CACHE_DIR="${THEGENT_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/thegent}"
THEGENT_EVAL_CACHE_DIR="${THEGENT_EVAL_CACHE_DIR:-$THEGENT_CACHE_DIR/eval-cache}"
THEGENT_PROFILE_ENABLED="${THEGENT_PROFILE_ENABLED:-0}"

# Create cache directories
mkdir -p "$THEGENT_EVAL_CACHE_DIR" 2>/dev/null || true

# --- Performance Profiling ---
# Enable zsh/zprof if profiling is enabled
if [[ "$THEGENT_PROFILE_ENABLED" == "1" ]]; then
  zmodload zsh/zprof 2>/dev/null || true
fi

# Startup time tracking
if [[ -n "${ZSH_VERSION:-}" ]]; then
  typeset -g THEGENT_START_TIME
  THEGENT_START_TIME="${EPOCHREALTIME:-$(date +%s.%N)}"
fi

# --- Eval Caching System ---
# Cache results of `eval "$(command init -)"` to speed up subsequent loads
# Pattern inspired by evalcache plugin (https://github.com/mroth/evalcache)
_thegent_evalcache() {
  local cmd="$1"
  shift
  local args="$*"

  # Generate cache key (hash of command + args)
  local cache_key
  if command -v md5 >/dev/null 2>&1; then
    cache_key="$(echo -n "$cmd $args" | md5 | cut -d' ' -f1)"
  elif command -v md5sum >/dev/null 2>&1; then
    cache_key="$(echo -n "$cmd $args" | md5sum | cut -d' ' -f1)"
  elif command -v shasum >/dev/null 2>&1; then
    cache_key="$(echo -n "$cmd $args" | shasum -a 256 | cut -d' ' -f1 | cut -c1-16)"
  else
    # Fallback: use command name + first 8 chars of args hash
    cache_key="$(echo -n "$cmd $args" | od -A n -t x1 | tr -d ' \n' | cut -c1-16)"
  fi

  local cache_file="$THEGENT_EVAL_CACHE_DIR/${cache_key}.zsh"
  local cache_meta="$THEGENT_EVAL_CACHE_DIR/${cache_key}.meta"

  # Check if cache is valid (exists and not stale)
  if [[ -f "$cache_file" && -f "$cache_meta" ]]; then
    local cache_age cmd_hash
    cache_age=$(stat -f "%m" "$cache_file" 2>/dev/null || stat -c "%Y" "$cache_file" 2>/dev/null || echo 0)
    cmd_hash=$(cat "$cache_meta" 2>/dev/null || echo "")
    local current_time
    current_time=$(date +%s)
    local age=$((current_time - cache_age))

    # Cache valid if < 1 hour old and command hash matches
    if [[ $age -lt 3600 && "$cmd_hash" == "$(command -v "$cmd" 2>/dev/null || echo '')" ]]; then
      # Source cached output
      source "$cache_file"
      return 0
    fi
  fi

  # Cache miss or stale: run command and cache output
  if ! command -v "$cmd" >/dev/null 2>&1; then
    # Command not found, gracefully degrade
    return 127
  fi

  local output
  output="$("$cmd" "$@" 2>/dev/null)"
  if [[ -n "$output" ]]; then
    # Save to cache
    echo "$output" > "$cache_file"
    command -v "$cmd" > "$cache_meta" 2>/dev/null || echo "" > "$cache_meta"
    # Source the output
    eval "$output"
  fi
}

# Clear eval cache
_thegent_evalcache_clear() {
  rm -f "$THEGENT_EVAL_CACHE_DIR"/*.zsh "$THEGENT_EVAL_CACHE_DIR"/*.meta 2>/dev/null
  echo "thegent: Eval cache cleared"
}

# --- Lazy Loading System ---
# Defer loading of expensive tools until first use
# Pattern: Load tool initialization on first command execution
_thegent_lazy_load() {
  local tool_name="$1"
  local init_cmd="$2"
  local trigger_cmds="$3"  # Space-separated list of commands that trigger loading
  shift 3
  local init_args="$*"

  # Check if already loaded (use indirect variable expansion for zsh compatibility)
  local loaded_var="THEGENT_LAZY_LOADED_${tool_name}"
  # Use eval to safely check indirect variable
  if eval "[[ -n \"\${${loaded_var}:-}\" ]]"; then
    return 0
  fi

  # Create wrapper functions for trigger commands
  # Only wrap if command doesn't already exist as a function (avoid conflicts)
  for trigger in $trigger_cmds; do
    local trigger_type
    trigger_type="$(type "$trigger" 2>/dev/null || echo 'not found')"

    # Only wrap if it's not already a function (or if it's an alias we want to override)
    if [[ "$trigger_type" != *"function"* ]] || [[ "$trigger_type" == *"alias"* ]]; then
      # Store original if it exists
      if command -v "$trigger" >/dev/null 2>&1; then
        eval "_thegent_orig_${trigger}() { command $trigger \"\$@\"; }"
      fi

      # Create lazy-loading wrapper (use indirect expansion for zsh compatibility)
      eval "$trigger() {
        # Load the tool on first use
        local loaded_var=\"THEGENT_LAZY_LOADED_${tool_name}\"
        if eval \"[[ -z \\\${${loaded_var}:-} ]]\"; then
          _thegent_evalcache $init_cmd $init_args
          export THEGENT_LAZY_LOADED_${tool_name}=1
        fi
        # Execute the real command (use original if stored, otherwise command)
        if type \"_thegent_orig_${trigger}\" >/dev/null 2>&1; then
          \"_thegent_orig_${trigger}\" \"\$@\"
        else
          command $trigger \"\$@\"
        fi
      }"
    fi
  done
}

# --- Parallel Loading ---
# Load independent modules in parallel using background jobs
_thegent_parallel_load() {
  local func_name="$1"
  shift

  # Run in background if interactive shell
  if [[ -n "${PS1:-}" ]]; then
    ($func_name "$@" >/dev/null 2>&1) &
  else
    $func_name "$@"
  fi
}

# --- Tool Detection (Cached) ---
# Fast tool detection with caching to avoid repeated `command -v` calls
typeset -gA THEGENT_TOOL_CACHE
_thegent_has_tool() {
  local tool="$1"

  # Check cache first
  if [[ -n "${THEGENT_TOOL_CACHE[$tool]:-}" ]]; then
    [[ "${THEGENT_TOOL_CACHE[$tool]}" == "1" ]]
    return $?
  fi

  # Check if tool exists
  if command -v "$tool" >/dev/null 2>&1; then
    THEGENT_TOOL_CACHE[$tool]=1
    return 0
  else
    THEGENT_TOOL_CACHE[$tool]=0
    return 1
  fi
}

# --- Startup Time Measurement ---
_thegent_measure_startup() {
  if [[ -n "${ZSH_VERSION:-}" && -n "${THEGENT_START_TIME:-}" ]]; then
    local end_time="${EPOCHREALTIME:-$(date +%s.%N)}"
    local duration
    if command -v awk >/dev/null 2>&1; then
      duration=$(awk "BEGIN {print $end_time - $THEGENT_START_TIME}")
    else
      # Fallback calculation
      duration=$(echo "$end_time - $THEGENT_START_TIME" | bc 2>/dev/null || echo "0")
    fi
    # Only log if > 100ms (avoid noise)
    if (( $(echo "$duration > 0.1" | bc -l 2>/dev/null || echo 0) )); then
      echo "thegent: Shell startup took ${duration}s" >&2
    fi
  fi
}

# Measure startup time on first prompt (non-blocking)
if [[ -n "${PS1:-}" ]]; then
  # Use precmd hook to measure (runs before each prompt)
  _thegent_startup_measured=0
  precmd() {
    if [[ "$_thegent_startup_measured" -eq 0 ]]; then
      _thegent_measure_startup
      _thegent_startup_measured=1
    fi
  }
fi

# --- Lazy Load Common Tools (Only in Interactive Shells) ---
# Defer loading expensive version managers until first use
# This saves 200-800ms on shell startup

if [[ -n "${PS1:-}" && -z "${AGENT_ID:-}" ]]; then
  # direnv REMOVED - fully migrated to mise (direnv was 3-4s slower)
  # mise handles all environment management now

  # zoxide (smart cd replacement) - lazy load with caching
  # Save 50-100ms by caching the init output
  if _thegent_has_tool zoxide; then
    # Create lazy wrapper for zoxide commands
    _thegent_lazy_load zoxide "zoxide" "z zi" "init" "zsh"
  fi

  # Version managers (lazy load - expensive, often unused)
  # These are loaded on first command use, not at startup
  # NOTE: mise (formerly rtx) is now the primary version manager (see ~/.zshenv)
  # Legacy tools below are DISABLED - mise handles all version management
  # To re-enable: uncomment the sections below and remove MISE_ENV checks
  # See: LEGACY_TOOLS_MIGRATION.md for migration guide

  # rbenv (Ruby version manager) - DISABLED (using mise)
  # if _thegent_has_tool rbenv && [[ -z "${MISE_ENV:-}" ]]; then
  #   _thegent_lazy_load rbenv "rbenv" "rbenv ruby bundle gem rake" "init" "-"
  # fi

  # jenv (Java version manager) - DISABLED (using mise)
  # if _thegent_has_tool jenv && [[ -z "${MISE_ENV:-}" ]]; then
  #   _thegent_lazy_load jenv "jenv" "jenv java javac mvn gradle" "init" "-"
  # fi

  # pyenv (Python version manager) - DISABLED (using mise)
  # if _thegent_has_tool pyenv && [[ -z "${MISE_ENV:-}" ]]; then
  #   _thegent_lazy_load pyenv "pyenv" "pyenv python pip pytest" "init" "-"
  # fi

  # nodenv (Node version manager) - DISABLED (using mise)
  # if _thegent_has_tool nodenv && [[ -z "${MISE_ENV:-}" ]]; then
  #   _thegent_lazy_load nodenv "nodenv" "nodenv node npm npx" "init" "-"
  # fi

  # nvm (Node version manager - special handling) - REMOVED (fully migrated to mise)
  # mise handles all Node.js version management now
  # See: LEGACY_TOOLS_MIGRATION.md for migration guide
fi

# --- Export Status ---
export THEGENT_SHELL_OPTIMIZATION_LOADED=1

# --- Cleanup Function ---
_thegent_cleanup_optimization() {
  # Kill fork guard if running
  [[ -n "${THEGENT_FORK_GUARD_PID:-}" ]] && kill "$THEGENT_FORK_GUARD_PID" 2>/dev/null || true

  # Clear old cache files (> 7 days)
  find "$THEGENT_EVAL_CACHE_DIR" -name "*.zsh" -mtime +7 -delete 2>/dev/null || true
  find "$THEGENT_EVAL_CACHE_DIR" -name "*.meta" -mtime +7 -delete 2>/dev/null || true
}

# Register cleanup on shell exit
if [[ -n "${PS1:-}" ]]; then
  zshexit() {
    _thegent_cleanup_optimization
  }
fi
