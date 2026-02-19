# thegent Shell Safeguards
# Comprehensive protection against common shell issues:
# - Command aliasing problems (ls tree, etc.)
# - Fork explosions
# - Timeout issues
# - Resource limits
# - Eval security issues

# Only load in interactive shells (not in scripts/agents)
[[ -z "${PS1:-}" || -n "${AGENT_ID:-}" || -n "${SHARECLI_AGENT_CONTEXT:-}" ]] && return 0

# --- Resource Limits (Prevent Fork Explosions) ---
# Set reasonable limits to prevent fork bombs and resource exhaustion
if command -v ulimit >/dev/null 2>&1; then
  # Limit number of processes per user (prevent fork explosions)
  ulimit -u 4096 2>/dev/null || true
  
  # Limit number of open file descriptors
  ulimit -n 1024 2>/dev/null || true
  
  # Limit virtual memory (prevent memory exhaustion)
  ulimit -v 4194304 2>/dev/null || true  # 4GB
fi

# --- Command Safeguards (Prevent Problematic Aliases) ---
# Restore normal behavior for commands that are commonly aliased incorrectly

# ls: Ensure single-level output by default (not tree/recursive)
if alias ls >/dev/null 2>&1; then
  local ls_alias_content
  ls_alias_content="$(alias ls | sed "s/^alias ls='//; s/'$//")"
  # Check if alias has problematic flags by default
  if [[ "$ls_alias_content" =~ (--tree|tree|recursive|-R)\s*$ ]] || \
     [[ "$ls_alias_content" =~ ^(lsd|exa|tree)\s+.*(--tree|-R|--recursive) ]]; then
    # Alias forces tree/recursive output, remove it
    unalias ls 2>/dev/null || true
  fi
fi

# Create safe ls wrapper if ls is aliased or doesn't exist as function
# This ensures ls always shows single-level output by default
if ! type ls >/dev/null 2>&1 || [[ "$(type ls 2>/dev/null)" == *"alias"* ]]; then
  # Store original ls if it exists
  if command -v ls >/dev/null 2>&1; then
    _thegent_original_ls() {
      command ls "$@"
    }
  else
    _thegent_original_ls() {
      /bin/ls "$@"
    }
  fi
  
  # Create safe ls wrapper
  ls() {
    local args=("$@")
    local has_recursive=0
    local has_tree=0
    
    # Check for recursive/tree flags
    for arg in "${args[@]}"; do
      [[ "$arg" == "-R" || "$arg" == "--recursive" || "$arg" == "-r" ]] && has_recursive=1
      [[ "$arg" == "--tree" ]] && has_tree=1
    done
    
    # If recursive/tree not explicitly requested, ensure single-level
    if [[ $has_recursive -eq 0 && $has_tree -eq 0 ]]; then
      # Use original ls with single-level output (bypass aliases)
      _thegent_original_ls "${args[@]}"
    else
      # User explicitly requested recursive/tree, allow it
      _thegent_original_ls "${args[@]}"
    fi
  }
fi

# --- Eval Security Safeguards ---
# Prevent eval from executing file paths accidentally
# This is a safety net in case something tries to eval file listings
# Note: We don't override eval globally as it breaks too many things
# Instead, we provide a safe_eval function and document best practices
_thegent_safe_eval() {
  local args="$*"
  # Check if argument looks like it contains file paths
  if [[ "$args" =~ /.*[\n\r] ]] || [[ "$args" =~ ^[[:space:]]*[^[:space:]]+/ ]]; then
    # Check if it's a variable assignment (safe) vs command execution (risky)
    if [[ ! "$args" =~ ^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*= ]]; then
      echo "thegent safeguard: eval may contain file paths, use _thegent_safe_eval or fix the source" >&2
      return 1
    fi
  fi
  builtin eval "$@"
}

# --- Timeout Safeguards ---
# Ensure commands don't hang indefinitely
# Set default timeout for long-running commands if timeout command exists
if command -v timeout >/dev/null 2>&1 || command -v gtimeout >/dev/null 2>&1; then
  # Use gtimeout on macOS (from coreutils), timeout on Linux
  _thegent_timeout_cmd() {
    if command -v gtimeout >/dev/null 2>&1; then
      command gtimeout "$@"
    else
      command timeout "$@"
    fi
  }
  
  # Wrap common long-running commands with timeout
  # Note: Only wrap if not already wrapped to avoid recursion
  if [[ "$(type find)" != *"thegent"* ]]; then
    find() {
      # For find commands that might hang, add timeout
      if [[ "$*" =~ (-exec|-execdir|-ok|-okdir) ]]; then
        _thegent_timeout_cmd 30 command find "$@"
      else
        command find "$@"
      fi
    }
  fi
fi

# --- Fork Explosion Prevention ---
# Monitor and limit concurrent processes
_thegent_fork_guard() {
  # Skip fork guard during direnv evaluation to prevent hangs
  [[ -n "${DIRENV_IN_ENVRC:-}" ]] && return 0
  
  # Disable extended_glob in this function to avoid "no matches found: (faster)" when
  # trigger vars or comments get misinterpreted as glob patterns
  setopt local_options
  unsetopt extended_glob 2>/dev/null || true
  
  # Use pgrep for pid_count when available, fallback to ps with throttling
  local pid_count=0
  if command -v pgrep >/dev/null 2>&1; then
    pid_count=$(pgrep -u "$USER" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
  else
    pid_count=$(ps -u "$USER" -o pid= 2>/dev/null | wc -l | tr -d ' ' || echo "0")
  fi
  [[ -z "$pid_count" || "$pid_count" == "0" ]] && pid_count=0

  # If too many processes, warn (threshold: 85% of ulimit)
  local max_procs
  max_procs=$(ulimit -u 2>/dev/null || echo 4096)
  [[ -z "$max_procs" || "$max_procs" -lt 1 ]] && max_procs=4096
  local warn_threshold=$((max_procs * 85 / 100))

  if [[ -n "$pid_count" && "$pid_count" -gt $warn_threshold ]]; then
    echo "thegent safeguard: High process count ($pid_count/$max_procs), consider cleanup" >&2
    # If > 95% of limit, be more aggressive
    if [[ $pid_count -gt $((max_procs * 95 / 100)) ]]; then
      echo "thegent safeguard: CRITICAL - Process limit nearly exhausted!" >&2
      # Auto-cleanup: kill background jobs
      if typeset -f _thegent_job_cleanup >/dev/null 2>&1; then
        _thegent_job_cleanup 2>/dev/null || true
      fi
    fi
  fi
}

# Run fork guard periodically (only in interactive shells)
# Use zsh's periodic functions for efficiency - check max once per 180 seconds (increased from 120)
if [[ -n "${PS1:-}" && -z "${DIRENV_IN_ENVRC:-}" ]]; then
  # Track last check time to throttle
  typeset -g _thegent_fork_guard_last_check=0

  _thegent_fork_guard_periodic() {
    # Skip during direnv evaluation
    [[ -n "${DIRENV_IN_ENVRC:-}" ]] && return 0
    
    local current_time
    current_time=$(date +%s 2>/dev/null || echo "0")
    # Only check if > 180 seconds since last check
    if (( current_time - _thegent_fork_guard_last_check > 180 )); then
      _thegent_fork_guard
      _thegent_fork_guard_last_check=$current_time
    fi
  }

  # Add to precmd (runs before each prompt)
  # Use array assignment to avoid duplicates
  if [[ ${precmd_functions[(ie)_thegent_fork_guard_periodic]} -gt ${#precmd_functions} ]]; then
    precmd_functions+=(_thegent_fork_guard_periodic)
  fi
fi

# --- Export Safeguard Status ---
export THEGENT_SHELL_SAFEGUARDS_LOADED=1
