# thegent Shell Safeguards
# Comprehensive protection against common shell issues:
# - Command aliasing problems (ls tree, etc.)
# - Fork explosions
# - Timeout issues
# - Resource limits
# - Eval security issues

# Only load in interactive shells (not in scripts/agents)
[[ -z "${PS1:-}" || -n "${AGENT_ID:-}" || -n "${heliosShield_AGENT_CONTEXT:-}" ]] && return 0

# --- Resource Limits (Prevent Fork Explosions) ---
# Set reasonable limits to prevent fork bombs and resource exhaustion
if command -v ulimit >/dev/null 2>&1; then
  # Limit number of processes per user (prevent fork explosions)
  ulimit -u 4096 2>/dev/null || true

  # Limit number of open file descriptors
  ulimit -n 1024 2>/dev/null || true

  # Virtual memory: do not cap RLIMIT_AS on Darwin. AppKit-linked CLIs (e.g. forge) map large VM;
  # a 4GB cap reliably produces SIGKILL (137) and `zsh: killed forge`. Subshells inherit this
  # shell's limits, so `zsh -f -c 'forge --version'` still fails when launched from an
  # interactive session that applied the cap. Non-macOS keeps a conservative cap.
  if [[ "$(uname -s)" != "Darwin" ]]; then
    ulimit -v 4194304 2>/dev/null || true  # 4GB
  fi
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

# --- Fork Explosion Prevention (v2: cached, protected-aware) ---
# Monitor and limit concurrent processes
# v2: uses cached state (no pgrep on every prompt) and respects protected process governance
typeset -g _thegent_fork_guard_cached_count=0
typeset -g _thegent_fork_guard_cached_at=0
typeset -gi _thegent_fork_guard_lock_pid=0

# Load protected-process governance if available
[[ -f "$HOME/.zsh_protected_processes.zsh" ]] && source "$HOME/.zsh_protected_processes.zsh"

_thegent_fork_guard() {
  # Skip fork guard during direnv evaluation to prevent hangs
  [[ -n "${DIRENV_IN_ENVRC:-}" ]] && return 0

  # Disable extended_glob in this function to avoid "no matches found: (faster)" when
  # trigger vars or comments get misinterpreted as glob patterns
  setopt local_options
  unsetopt extended_glob 2>/dev/null || true

  # Reentrancy lock — prevent self-recursion when calling from a hook
  if [[ "$_thegent_fork_guard_lock_pid" == "$$" ]]; then
    return 0
  fi
  _thegent_fork_guard_lock_pid=$$

  # Use cached value if <60s old (avoids forking pgrep on every prompt)
  local now
  now=$(date +%s 2>/dev/null || echo "0")
  local pid_count=0
  if (( now - _thegent_fork_guard_cached_at < 60 )) && (( _thegent_fork_guard_cached_at > 0 )); then
    pid_count=$_thegent_fork_guard_cached_count
  else
    if command -v pgrep >/dev/null 2>&1; then
      pid_count=$(pgrep -u "$USER" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    else
      pid_count=$(ps -u "$USER" -o pid= 2>/dev/null | wc -l | tr -d ' ' || echo "0")
    fi
    [[ -z "$pid_count" || "$pid_count" == "0" ]] && pid_count=0
    _thegent_fork_guard_cached_count=$pid_count
    _thegent_fork_guard_cached_at=$now
  fi

  # If too many processes, warn (threshold: 85% of ulimit)
  local max_procs
  max_procs=$(ulimit -u 2>/dev/null || echo 4096)
  [[ -z "$max_procs" || "$max_procs" -lt 1 ]] && max_procs=4096
  local warn_threshold=$((max_procs * 85 / 100))

  if [[ -n "$pid_count" && "$pid_count" -gt $warn_threshold ]]; then
    # Only auto-cleanup non-protected processes
    if typeset -f _thegent_filter_protected >/dev/null 2>&1; then
      local candidate_count
      candidate_count=$(pgrep -u "$USER" 2>/dev/null | while read -r p; do _thegent_is_protected "$p" || echo "$p"; done 2>/dev/null | wc -l | tr -d ' ')
      echo "thegent safeguard: High process count ($pid_count/$max_procs). $candidate_count non-protected candidate(s) for cleanup." >&2
    else
      echo "thegent safeguard: High process count ($pid_count/$max_procs), consider cleanup" >&2
    fi

    # If > 95% of limit, be more aggressive
    if [[ $pid_count -gt $((max_procs * 95 / 100)) ]]; then
      echo "thegent safeguard: CRITICAL - Process limit nearly exhausted!" >&2
      # Auto-cleanup: only kill non-protected background jobs
      if typeset -f _thegent_job_cleanup >/dev/null 2>&1; then
        _thegent_job_cleanup 2>/dev/null || true
      fi
    fi
  fi

  _thegent_fork_guard_lock_pid=0
}

# --- gh Governance Guard ---
_thegent_gh_is_method_get_like() {
  local method="${1:-GET}"
  case "${method:l}" in
    get|head) return 0 ;;
    *) return 1 ;;
  esac
}

_thegent_gh_repo_owner() {
  local -a args=("$@")
  local i token repo

  for ((i = 1; i <= ${#args[@]}; i++)); do
    token="${args[$i]}"
    case "$token" in
      -R|--repo)
        ((i += 1))
        repo="${args[$i]}"
        ;;
      -R=*|--repo=*)
        repo="${token#*=}"
        ;;
    esac
    [[ -n "$repo" ]] && break
  done

  if [[ -z "$repo" ]] && command git -C . rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    local remote_url
    remote_url="$(command git -C . remote get-url origin 2>/dev/null || true)"
    if [[ -n "$remote_url" ]]; then
      case "$remote_url" in
        github.com:*) repo="${remote_url#github.com:}" ;;
        https://github.com/*|http://github.com/*|git@github.com:*)
          repo="${remote_url#*github.com/}"
          ;;
      esac
      repo="${repo%.git}"
    fi
  fi

  print "${repo%%/*}"
}

_thegent_gh_is_comment_payload() {
  local -a args=("$@")
  local i token next_is_body next_is_file body candidate
  next_is_body=0
  next_is_file=0

  for ((i = 1; i <= ${#args[@]}; i++)); do
    token="${args[$i]}"
    if ((next_is_body)); then
      body="$token"
      next_is_body=0
      continue
    fi
    if ((next_is_file)); then
      if [[ "$token" == "-" ]]; then
        return 1
      fi
      if [[ -f "$token" ]]; then
        candidate="$(command cat "$token" 2>/dev/null)"
        body="${body:+$body$'\n'}$candidate"
      else
        body="${body:+$body$'\n'}$token"
      fi
      next_is_file=0
      continue
    fi

    case "$token" in
      --body|--comment)
        next_is_body=1
        ;;
      --body=?*|--comment=?*)
        candidate="${token#*=}"
        body="${body:+$body$'\n'}$candidate"
        ;;
      -b)
        next_is_body=1
        ;;
      --body-file|-F)
        next_is_file=1
        ;;
      -b*|--body-file=?*)
        candidate="${token#*=}"
        if [[ "$token" == -b* && "$token" != -b ]]; then
          candidate="${token#-b}"
        fi
        if [[ "$candidate" == "-" ]]; then
          return 1
        fi
        if [[ -f "$candidate" ]]; then
          body="${body:+$body$'\n'}$(command cat "$candidate" 2>/dev/null)"
        else
          body="${body:+$body$'\n'}$candidate"
        fi
        ;;
      --body-file=*)
        candidate="${token#*=}"
        if [[ "$candidate" == "-" ]]; then
          return 1
        fi
        if [[ -f "$candidate" ]]; then
          body="${body:+$body$'\n'}$(command cat "$candidate" 2>/dev/null)"
        else
          body="${body:+$body$'\n'}$candidate"
        fi
        ;;
    esac
  done

  [[ "${body:l}" == *"@kooshapari"* ]]
}

_thegent_gh_write_command() {
  local -a args=("$@")
  local i token top_cmd sub_cmd method="GET"
  local skip_next=0

  top_cmd=""
  sub_cmd=""
  for ((i = 1; i <= ${#args[@]}; i++)); do
    token="${args[$i]}"
    if ((skip_next)); then
      skip_next=0
      continue
    fi

    case "$token" in
      --method|--method=*)
        if [[ "$token" == "--method" ]]; then
          ((i += 1))
          method="${args[$i]:-GET}"
        else
          method="${token#*=}"
        fi
        ;;
      -X)
        ((i += 1))
        method="${args[$i]:-GET}"
        ;;
      -X*)
        method="${token#-X}"
        ;;
      -R|--repo|--repo=*|-R=*)
        if [[ "$token" == "-R" || "$token" == "--repo" ]]; then
          ((skip_next=1))
        fi
        continue
        ;;
      --*)
        continue
        ;;
      -*)
        case "$token" in
          -b|-F|--body|--comment|--body-file|--method)
            skip_next=1
            ;;
        esac
        continue
        ;;
      *)
        if [[ -z "$top_cmd" ]]; then
          top_cmd="$token"
          continue
        fi
        if [[ -z "$sub_cmd" ]]; then
          sub_cmd="$token"
          continue
        fi
        ;;
    esac
  done

  [[ -z "$top_cmd" ]] && return 1
  if [[ "$top_cmd" == "help" || "$top_cmd" == "alias" || "$top_cmd" == "completion" || "$top_cmd" == "version" ]]; then
    return 1
  fi

  if [[ "$top_cmd" == "api" ]]; then
    _thegent_gh_is_method_get_like "$method" && return 1
    return 0
  fi

  if [[ "$top_cmd" == "repo" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "edit" || "$sub_cmd" == "delete" || "$sub_cmd" == "archive" || "$sub_cmd" == "unarchive" || "$sub_cmd" == "rename" || "$sub_cmd" == "transfer" ]]
  elif [[ "$top_cmd" == "issue" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "edit" || "$sub_cmd" == "close" || "$sub_cmd" == "reopen" || "$sub_cmd" == "comment" || "$sub_cmd" == "lock" || "$sub_cmd" == "unlock" || "$sub_cmd" == "delete" || "$sub_cmd" == "pin" || "$sub_cmd" == "unpin" ]]
  elif [[ "$top_cmd" == "pr" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "close" || "$sub_cmd" == "reopen" || "$sub_cmd" == "edit" || "$sub_cmd" == "comment" || "$sub_cmd" == "review" || "$sub_cmd" == "merge" || "$sub_cmd" == "ready" || "$sub_cmd" == "unready" || "$sub_cmd" == "approve" || "$sub_cmd" == "request-changes" || "$sub_cmd" == "close" ]]
  elif [[ "$top_cmd" == "release" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "edit" || "$sub_cmd" == "delete" ]]
  elif [[ "$top_cmd" == "run" ]]; then
    [[ "$sub_cmd" == "cancel" || "$sub_cmd" == "delete" || "$sub_cmd" == "rerun" ]]
  elif [[ "$top_cmd" == "secret" ]]; then
    [[ "$sub_cmd" == "set" || "$sub_cmd" == "set-org" || "$sub_cmd" == "set-repo" || "$sub_cmd" == "delete" || "$sub_cmd" == "remove" ]]
  elif [[ "$top_cmd" == "label" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "edit" || "$sub_cmd" == "delete" ]]
  elif [[ "$top_cmd" == "milestone" ]]; then
    [[ "$sub_cmd" == "create" || "$sub_cmd" == "edit" || "$sub_cmd" == "close" || "$sub_cmd" == "delete" ]]
  else
    return 1
  fi
}

_thegent_gh_is_reply_command() {
  local -a args=("$@")
  local i token top_cmd sub_cmd skip_next=0
  top_cmd=""
  sub_cmd=""

  for ((i = 1; i <= ${#args[@]}; i++)); do
    token="${args[$i]}"
    if ((skip_next)); then
      skip_next=0
      continue
    fi
    case "$token" in
      -R|--repo|--repo=*|-R=*|--body|--body=*|--comment|--comment=*|-b|-F|--body-file|--body-file=*)
        if [[ "$token" == "-R" || "$token" == "--repo" || "$token" == "--body" || "$token" == "--comment" || "$token" == "-b" || "$token" == "--body-file" ]]; then
          skip_next=1
        fi
        continue
        ;;
      -*) continue ;;
      *)
        if [[ -z "$top_cmd" ]]; then
          top_cmd="$token"
        elif [[ -z "$sub_cmd" ]]; then
          sub_cmd="$token"
          break
        fi
        ;;
    esac
  done

  [[ "$top_cmd/$sub_cmd" == "issue/comment" || "$top_cmd/$sub_cmd" == "pr/comment" || "$top_cmd/$sub_cmd" == "pr/review" ]]
}

  gh() {
  if [[ "${THEGENT_DISABLE_GH_GOVERNANCE:-0}" == "1" ]]; then
    command gh "$@"
    return $?
  fi

  if _thegent_gh_write_command "$@"; then
    local owner
    owner="$(_thegent_gh_repo_owner "$@")"
    if [[ "${owner:l}" != "kooshapari" ]]; then
      if ! _thegent_gh_is_reply_command "$@"; then
        echo "[thegent] blocked: read-only governance mode for gh outside KooshaPari namespace: ${1:-gh} ${2:-}" >&2
        echo "[thegent] outside KooshaPari namespace, only allowed writes are explicit @kooshapari replies on issue/pr comment/review." >&2
        echo "[thegent] include --repo KooshaPari/<repo> to bypass, or include '@kooshapari' in payload for reply exceptions." >&2
        return 1
      fi

      if ! _thegent_gh_is_comment_payload "$@"; then
        echo "[thegent] blocked: write reply requires explicit @kooshapari mention in the provided body." >&2
        return 1
      fi
    fi
  fi

  command gh "$@"
}

# Run fork guard periodically (only in interactive shells)
# Use zsh's periodic functions for efficiency - check max once per 180 seconds (increased from 120)
if [[ -n "${PS1:-}" && -z "${DIRENV_IN_ENVRC:-}" ]]; then
  # Track last check time to throttle
  typeset -g _thegent_fork_guard_last_check=0
  typeset -g _thegent_fork_guardian_last_check=0

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

    # If fork guardian is loaded AND daemon isn't running, run an inline check
    # every 5 minutes. This is a backstop if the launchd daemon is dead.
    if (( current_time - _thegent_fork_guardian_last_check > 300 )); then
      if typeset -f _thegent_fg_check >/dev/null 2>&1; then
        # Only run if no daemon is running
        local pid_file="${THEGENT_FG_PID_FILE:-$HOME/.local/state/thegent/fork-guardian.pid}"
        local daemon_alive=0
        if [[ -f "$pid_file" ]]; then
          local dp
          dp=$(cat "$pid_file" 2>/dev/null)
          if [[ -n "$dp" ]] && kill -0 "$dp" 2>/dev/null; then
            daemon_alive=1
          fi
        fi
        if [[ $daemon_alive -eq 0 ]]; then
          # Inline check, skip tier 3-5 to avoid killing from interactive shell
          local tier
          tier=$(_thegent_fg_check 2>/dev/null)
          if (( tier >= 3 )); then
            print -r -- "[thegent-fg] TIER $tier detected. Consider running: thegent-fork-guardian check" >&2
          fi
        fi
        _thegent_fork_guardian_last_check=$current_time
      fi
    fi
  }

  # Add to precmd (runs before each prompt)
  # Use array assignment to avoid duplicates
  if (( ${+precmd_functions} )) && (( ${precmd_functions[(ie)_thegent_fork_guard_periodic]} > ${#precmd_functions} )); then
    precmd_functions+=(_thegent_fork_guard_periodic)
  fi
fi

# --- Export Safeguard Status ---
export THEGENT_SHELL_SAFEGUARDS_LOADED=1
