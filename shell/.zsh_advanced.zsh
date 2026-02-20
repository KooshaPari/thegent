# thegent Advanced Shell Optimization System
# Implements: instant prompt, async/turbo loading, advanced caching, error recovery,
# background job management, cross-platform compatibility, advanced monitoring

# Only load in interactive shells
[[ -z "${PS1:-}" || -n "${AGENT_ID:-}" || -n "${heliosShield_AGENT_CONTEXT:-}" ]] && return 0

# --- Platform Detection ---
# Detect platform for cross-platform compatibility
typeset -g THEGENT_PLATFORM
if [[ -n "${OSTYPE:-}" ]]; then
  case "$OSTYPE" in
    darwin*) THEGENT_PLATFORM="macos" ;;
    linux-gnu*) THEGENT_PLATFORM="linux" ;;
    linux-musl*) THEGENT_PLATFORM="linux" ;;
    cygwin*|msys*|mingw*) THEGENT_PLATFORM="windows" ;;
    *) THEGENT_PLATFORM="unknown" ;;
  esac
else
  # Fallback detection
  case "$(uname -s 2>/dev/null || echo '')" in
    Darwin) THEGENT_PLATFORM="macos" ;;
    Linux) THEGENT_PLATFORM="linux" ;;
    MINGW*|MSYS*) THEGENT_PLATFORM="windows" ;;
    *) THEGENT_PLATFORM="unknown" ;;
  esac
fi

# --- Configuration ---
THEGENT_CACHE_DIR="${THEGENT_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/thegent}"
THEGENT_ADVANCED_CACHE_DIR="${THEGENT_ADVANCED_CACHE_DIR:-$THEGENT_CACHE_DIR/advanced}"
THEGENT_INSTANT_PROMPT_ENABLED="${THEGENT_INSTANT_PROMPT_ENABLED:-1}"
THEGENT_ASYNC_LOADING_ENABLED="${THEGENT_ASYNC_LOADING_ENABLED:-1}"
THEGENT_METRICS_ENABLED="${THEGENT_METRICS_ENABLED:-0}"

# Create cache directories - DEFERRED for <50ms startup (create in background)
(mkdir -p "$THEGENT_ADVANCED_CACHE_DIR"/{cache-l1,cache-l2,jobs,metrics} 2>/dev/null &)

# --- Multi-Level Cache System ---
# Level 1: In-memory cache (fastest, session-scoped)
typeset -gA THEGENT_CACHE_L1
# Level 2: File cache (fast, persistent across sessions)
typeset -g THEGENT_CACHE_L2_DIR="$THEGENT_ADVANCED_CACHE_DIR/cache-l2"

_thegent_cache_l1_get() {
  local key="$1"
  echo "${THEGENT_CACHE_L1[$key]:-}"
}

_thegent_cache_l1_set() {
  local key="$1"
  local value="$2"
  THEGENT_CACHE_L1[$key]="$value"
}

_thegent_cache_l2_get() {
  local key="$1"
  local cache_file="$THEGENT_CACHE_L2_DIR/${key}.cache"
  
  # Check if cache exists and is valid (< 1 hour old)
  if [[ -f "$cache_file" ]]; then
    local cache_age
    cache_age=$(stat -f "%m" "$cache_file" 2>/dev/null || stat -c "%Y" "$cache_file" 2>/dev/null || echo 0)
    local current_time
    current_time=$(date +%s)
    local age=$((current_time - cache_age))
    
    if [[ $age -lt 3600 ]]; then
      cat "$cache_file"
      return 0
    fi
  fi
  return 1
}

_thegent_cache_l2_set() {
  local key="$1"
  local value="$2"
  local cache_file="$THEGENT_CACHE_L2_DIR/${key}.cache"
  echo "$value" > "$cache_file"
}

_thegent_cache_get() {
  local key="$1"
  
  # Try L1 first
  local value
  value="$(_thegent_cache_l1_get "$key")"
  if [[ -n "$value" ]]; then
    echo "$value"
    return 0
  fi
  
  # Try L2
  if value="$(_thegent_cache_l2_get "$key")"; then
    # Populate L1 for next time
    _thegent_cache_l1_set "$key" "$value"
    echo "$value"
    return 0
  fi
  
  return 1
}

_thegent_cache_set() {
  local key="$1"
  local value="$2"
  
  # Set in both levels
  _thegent_cache_l1_set "$key" "$value"
  _thegent_cache_l2_set "$key" "$value"
}

# --- Instant Prompt System ---
# Print prompt immediately, load everything else in background
if [[ "$THEGENT_INSTANT_PROMPT_ENABLED" == "1" && -n "${ZSH_VERSION:-}" ]]; then
  # Check if instant prompt cache exists
  typeset -g THEGENT_INSTANT_PROMPT_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/thegent/instant-prompt-${(%):-%n}.zsh"
  
  if [[ -r "$THEGENT_INSTANT_PROMPT_CACHE" ]]; then
    # Load cached instant prompt
    source "$THEGENT_INSTANT_PROMPT_CACHE"
  else
    # Generate instant prompt cache (minimal prompt)
    mkdir -p "$(dirname "$THEGENT_INSTANT_PROMPT_CACHE")" 2>/dev/null || true
    cat > "$THEGENT_INSTANT_PROMPT_CACHE" <<'INSTANTPROMPT'
# Instant prompt - minimal prompt printed immediately
# Full prompt will be loaded in background
if [[ -z "${THEGENT_PROMPT_LOADED:-}" ]]; then
  # Minimal prompt
  PS1='%n@%m %1~ %# '
  # Redirect stdout/stderr during initialization
  exec 3>&1 4>&2
  exec 1>/dev/null 2>&1
  # Mark that we're initializing
  export THEGENT_INITIALIZING=1
fi
INSTANTPROMPT
    source "$THEGENT_INSTANT_PROMPT_CACHE"
  fi
fi

# --- Background Job Management ---
typeset -gA THEGENT_BACKGROUND_JOBS
typeset -g THEGENT_JOB_REGISTRY="$THEGENT_ADVANCED_CACHE_DIR/jobs/registry"
typeset -g THEGENT_ASYNC_CURRENT_JOBS=0

_thegent_job_register() {
  local job_name="$1"
  local pid="$2"
  THEGENT_BACKGROUND_JOBS[$job_name]=$pid
  THEGENT_ASYNC_CURRENT_JOBS=$((${THEGENT_ASYNC_CURRENT_JOBS:-0} + 1))
  echo "$job_name:$pid" >> "$THEGENT_JOB_REGISTRY" 2>/dev/null || true
}

_thegent_job_wait() {
  local job_name="$1"
  local pid="${THEGENT_BACKGROUND_JOBS[$job_name]:-}"

  if [[ -n "$pid" ]]; then
    wait "$pid" 2>/dev/null || true
    unset "THEGENT_BACKGROUND_JOBS[$job_name]"
    THEGENT_ASYNC_CURRENT_JOBS=$((${THEGENT_ASYNC_CURRENT_JOBS:-0} - 1))
  fi
}

_thegent_job_cleanup() {
  # Avoid extended_glob and bad math from empty vars
  setopt local_options
  unsetopt extended_glob 2>/dev/null || true
  # Clean up all background jobs (ensure array exists)
  [[ ${+THEGENT_BACKGROUND_JOBS} -eq 0 ]] && typeset -gA THEGENT_BACKGROUND_JOBS
  for job_name in "${(@k)THEGENT_BACKGROUND_JOBS}"; do
    local pid="${THEGENT_BACKGROUND_JOBS[$job_name]}"
    # Check if process exists before killing
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  THEGENT_BACKGROUND_JOBS=()
  THEGENT_ASYNC_CURRENT_JOBS=0
}

# Define _thegent_load_full_prompt before it's used in async loading
_thegent_load_full_prompt() {
  # Load full prompt configuration
  # This would typically load your actual prompt theme
  export THEGENT_PROMPT_LOADED=1
  
  # If using powerlevel10k or similar, it will handle prompt
  # Otherwise, set a reasonable default
  if [[ -z "${POWERLEVEL9K_MODE:-}" ]]; then
    PS1='%n@%m %1~ %# '
  fi
}

# --- Async/Turbo Loading System ---
# Load plugins/tools asynchronously with wait conditions
if [[ "$THEGENT_ASYNC_LOADING_ENABLED" == "1" ]]; then
  typeset -ga THEGENT_ASYNC_QUEUE

  # Limit async jobs to prevent fork exhaustion
  typeset -g THEGENT_ASYNC_MAX_JOBS=5
  # THEGENT_ASYNC_CURRENT_JOBS is initialized earlier in Background Job Management section

  _thegent_async_load() {
    local wait_condition="$1"
    local load_func="$2"
    shift 2
    local load_args=("$@")

    # Check job limit
    if [[ $THEGENT_ASYNC_CURRENT_JOBS -ge $THEGENT_ASYNC_MAX_JOBS ]]; then
      # Skip spawning if at limit
      return 0
    fi

    # Export function to subshells if it exists
    if typeset -f "$load_func" >/dev/null 2>&1; then
      functions -x "$load_func" 2>/dev/null || true
    fi

    # Parse wait condition
    if [[ "$wait_condition" =~ ^[0-9]+$ ]]; then
      # Time-based wait (wait"N") - limit to max 5 seconds to prevent accumulation
      local wait_seconds="$wait_condition"
      ((wait_seconds > 5)) && wait_seconds=5  # Cap at 5 seconds
      (
        # Source function if available
        if typeset -f "$load_func" >/dev/null 2>&1; then
          eval "$(typeset -f "$load_func")"
        fi
        sleep "$wait_seconds"
        "$load_func" "${load_args[@]}" 2>/dev/null || true
      ) &
      _thegent_job_register "async_${load_func}_${wait_seconds}" $!
    elif [[ "$wait_condition" == "0" || -z "$wait_condition" ]]; then
      # Load immediately in background (wait"0")
      (
        # Source function if available
        if typeset -f "$load_func" >/dev/null 2>&1; then
          eval "$(typeset -f "$load_func")"
        fi
        "$load_func" "${load_args[@]}" 2>/dev/null || true
      ) &
      _thegent_job_register "async_${load_func}_0" $!
    elif [[ "$wait_condition" =~ ^\[\[.*\]\]$ ]]; then
      # Condition-based wait (wait'[[ condition ]]') - with timeout
      local condition="${wait_condition#\[\[ }"
      condition="${condition% \]\]}"
      (
        # Source function if available
        if typeset -f "$load_func" >/dev/null 2>&1; then
          eval "$(typeset -f "$load_func")"
        fi
        local timeout=30
        local elapsed=0
        while ! eval "$condition"; do
          sleep 0.5
          elapsed=$((elapsed + 1))
          if [[ $elapsed -ge $((timeout * 2)) ]]; then
            break  # Timeout after 30 seconds
          fi
        done
        "$load_func" "${load_args[@]}" 2>/dev/null || true
      ) &
      _thegent_job_register "async_${load_func}_cond" $!
    else
      # Unknown condition, load immediately
      "$load_func" "${load_args[@]}" 2>/dev/null || true
    fi
  }
  
  # Trigger-load: Create function that loads plugin on first call
  _thegent_trigger_load() {
    local trigger_cmd="$1"
    local load_func="$2"
    shift 2
    local load_args=("$@")
    
    # Create wrapper function
    eval "$trigger_cmd() {
      if [[ -z \"\${THEGENT_LOADED_${trigger_cmd}:-}\" ]]; then
        $load_func ${load_args[@]}
        export THEGENT_LOADED_${trigger_cmd}=1
      fi
      command $trigger_cmd \"\$@\"
    }"
  }
fi

# --- Error Recovery System ---
# Circuit breaker pattern, graceful degradation, retry logic
typeset -gA THEGENT_CIRCUIT_BREAKERS
typeset -g THEGENT_CIRCUIT_BREAKER_DIR="$THEGENT_ADVANCED_CACHE_DIR/circuit-breakers"

_thegent_circuit_breaker_open() {
  local service="$1"
  local threshold="${2:-5}"
  local cooldown="${3:-60}"
  
  local failure_file="$THEGENT_CIRCUIT_BREAKER_DIR/${service}.failures"
  local state_file="$THEGENT_CIRCUIT_BREAKER_DIR/${service}.state"
  
  mkdir -p "$THEGENT_CIRCUIT_BREAKER_DIR" 2>/dev/null || true
  
  # Count failures
  local failures=0
  if [[ -f "$failure_file" ]]; then
    failures=$(cat "$failure_file")
  fi
  
  failures=$((failures + 1))
  echo "$failures" > "$failure_file"
  
  # Open circuit if threshold exceeded
  if [[ $failures -ge $threshold ]]; then
    echo "open:$(date +%s)" > "$state_file"
    return 1
  fi
  
  return 0
}

_thegent_circuit_breaker_is_open() {
  local service="$1"
  local cooldown="${2:-60}"
  
  local state_file="$THEGENT_CIRCUIT_BREAKER_DIR/${service}.state"
  
  if [[ ! -f "$state_file" ]]; then
    return 1  # Circuit closed
  fi
  
  local state
  state=$(cat "$state_file")
  if [[ "$state" != "open:"* ]]; then
    return 1  # Circuit closed
  fi
  
  # Check cooldown
  local open_time="${state#open:}"
  local current_time
  current_time=$(date +%s)
  local elapsed=$((current_time - open_time))
  
  if [[ $elapsed -lt $cooldown ]]; then
    return 0  # Circuit open
  else
    # Cooldown expired, close circuit
    rm -f "$state_file"
    rm -f "$THEGENT_CIRCUIT_BREAKER_DIR/${service}.failures"
    return 1  # Circuit closed
  fi
}

_thegent_circuit_breaker_reset() {
  local service="$1"
  rm -f "$THEGENT_CIRCUIT_BREAKER_DIR/${service}.state"
  rm -f "$THEGENT_CIRCUIT_BREAKER_DIR/${service}.failures"
}

_thegent_safe_exec() {
  local cmd="$1"
  shift
  local args=("$@")
  local max_retries="${THEGENT_MAX_RETRIES:-3}"
  local retry_delay="${THEGENT_RETRY_DELAY:-1}"
  
  # Check circuit breaker
  if _thegent_circuit_breaker_is_open "$cmd"; then
    echo "thegent: Circuit breaker open for $cmd, using fallback" >&2
    return 1
  fi
  
  # Retry logic with exponential backoff
  local attempt=0
  while [[ $attempt -lt $max_retries ]]; do
    if "$cmd" "${args[@]}" 2>/dev/null; then
      # Success, reset circuit breaker
      _thegent_circuit_breaker_reset "$cmd"
      return 0
    fi
    
    attempt=$((attempt + 1))
    if [[ $attempt -lt $max_retries ]]; then
      sleep $((retry_delay * attempt))
    fi
  done
  
  # All retries failed, open circuit breaker
  _thegent_circuit_breaker_open "$cmd"
  return 1
}

# --- Predictive Preloading ---
# Preload tools based on usage patterns
_thegent_predictive_preload() {
  # Load frequently used tools in background
  local common_tools=("git" "rg" "fd" "fzf")
  
  for tool in "${common_tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      # Preload tool detection into cache
      _thegent_cache_set "tool:$tool" "$(command -v "$tool")"
    fi
  done
}

# --- Advanced Monitoring ---
if [[ "$THEGENT_METRICS_ENABLED" == "1" ]]; then
  typeset -gA THEGENT_METRICS
  typeset -g THEGENT_METRICS_FILE="$THEGENT_ADVANCED_CACHE_DIR/metrics/stats"
  
  _thegent_metrics_record() {
    local metric="$1"
    local value="${2:-1}"
    
    THEGENT_METRICS[$metric]=$((${THEGENT_METRICS[$metric]:-0} + value))
    
    # Persist to file
    echo "$metric:$value" >> "$THEGENT_METRICS_FILE" 2>/dev/null || true
  }
  
  _thegent_metrics_get() {
    local metric="$1"
    echo "${THEGENT_METRICS[$metric]:-0}"
  }
  
  _thegent_metrics_report() {
    echo "=== thegent Metrics Report ==="
    for metric in "${(@k)THEGENT_METRICS}"; do
      echo "$metric: ${THEGENT_METRICS[$metric]}"
    done
  }
fi

# --- Cross-Platform Compatibility ---
# Platform-specific optimizations and fallbacks
case "$THEGENT_PLATFORM" in
  macos)
    # macOS-specific: use gtimeout instead of timeout
    if command -v gtimeout >/dev/null 2>&1; then
      _thegent_timeout_cmd() { command gtimeout "$@"; }
    else
      _thegent_timeout_cmd() { command timeout "$@"; }
    fi
    ;;
  linux)
    # Linux-specific: use timeout
    _thegent_timeout_cmd() { command timeout "$@"; }
    ;;
  windows)
    # Windows/WSL-specific: limited timeout support
    _thegent_timeout_cmd() {
      # Fallback: run without timeout on Windows
      "$@"
    }
    ;;
  *)
    # Unknown platform: use basic timeout if available
    if command -v timeout >/dev/null 2>&1; then
      _thegent_timeout_cmd() { command timeout "$@"; }
    else
      _thegent_timeout_cmd() { "$@"; }
    fi
    ;;
esac

# --- Restore stdout/stderr after instant prompt ---
if [[ -n "${THEGENT_INITIALIZING:-}" && "$THEGENT_INITIALIZING" == "1" ]]; then
  # Restore file descriptors
  exec 1>&3 2>&4
  exec 3>&- 4>&-
  unset THEGENT_INITIALIZING
fi

# --- Load Full Prompt ---
if [[ -n "${THEGENT_INITIALIZING:-}" && "$THEGENT_INITIALIZING" == "1" ]]; then
  # Load full prompt in background
  if [[ "$THEGENT_ASYNC_LOADING_ENABLED" == "1" ]]; then
    _thegent_async_load "0" "_thegent_load_full_prompt" &
    _thegent_job_register "load_full_prompt" $!
  else
    _thegent_load_full_prompt
  fi
fi

# --- Predictive Preloading on Startup ---
# Defer predictive preload to avoid blocking startup (load after 2 seconds)
# Only run once per session (check if already registered)
if [[ "$THEGENT_ASYNC_LOADING_ENABLED" == "1" && -z "${THEGENT_PREDICTIVE_PRELOAD_STARTED:-}" ]]; then
  export THEGENT_PREDICTIVE_PRELOAD_STARTED=1
  _thegent_async_load "2" "_thegent_predictive_preload" &
  _thegent_job_register "predictive_preload" $!
fi

# --- Cleanup on Exit ---
if [[ -n "${PS1:-}" ]]; then
  zshexit() {
    _thegent_job_cleanup
    [[ "$THEGENT_METRICS_ENABLED" == "1" ]] && _thegent_metrics_report >&2 || true
  }
fi

# --- Export Status ---
export THEGENT_ADVANCED_LOADED=1
export THEGENT_PLATFORM
