# thegent Protected Processes Governance
# ==========================================
# Strict policy: these processes must NEVER be killed or signaled by
# any automated cleanup, fork guard, or system maintenance script.
#
# Reason: These are the user's primary interactive tools and agent
# infrastructure. Killing them disrupts active work and can corrupt
# agent state machines / conversation sessions.
#
# This file is sourced by:
#   - ~/.zsh_safeguards.zsh (fork guard skip list)
#   - thegent-maintenance scripts (cleanup skip list)
#   - thegent fork-explosion recovery

# === PROTECTED PROCESS NAMES ===
# Match against `ps -o comm` (basename of command)
# Use shell glob patterns; matched with case-glob
THEGENT_PROTECTED_PROCESSES=(
  # === Shell / Terminal ===
  'ghostty*'                # Ghostty terminal emulator
  'login'                   # launchd-spawned login sessions
  'zsh'                     # Interactive zsh
  'bash'                    # Interactive bash
  'fish'                    # Interactive fish
  'tmux*'                   # Terminal multiplexer
  'screen'                  # Terminal multiplexer

  # === Agent / Editor CLIs ===
  'forge*'                  # Forge agent CLI (all variants)
  'forge-dev*'              # Forge dev binary
  'claude*'                 # Claude Code
  'codex*'                  # Codex CLI
  'cursor*'                 # Cursor editor
  'aider*'                  # Aider
  'cline*'                  # Cline
  'continue*'               # Continue.dev
  'windsurf*'               # Windsurf

  # === Editor / IDE ===
  'nvim'                    # Neovim
  'vim'                     # Vim
  'code'                    # VS Code
  'emacs*'                  # Emacs
  'helix'                   # Helix editor

  # === Dev / Build Tools (interactive) ===
  'cargo'                   # cargo (only protected when run from agent)
  'rustc'                   # rust compiler
  'node'                    # Node.js REPL
  'python*'                 # Python REPL
  'ipython*'                # IPython
  'jupyter*'                # Jupyter

  # === Watchman (rebuild-safe) ===
  'watchman*'               # Meta's file watcher
)

# === PROTECTED PPIDS ===
# PIDs of ancestor processes that, if present as a parent, exempt child from cleanup
THEGENT_PROTECTED_PPIDS=(
  # Ghostty-spawned login + zsh
  # LaunchAgents
)

# === PROTECTED CWD PATTERNS ===
# If a process is running in one of these dirs, it's considered agent infrastructure
THEGENT_PROTECTED_CWD_PATTERNS=(
  '/Users/kooshapari/CodeProjects/*'
  '/Users/kooshapari/.forge/*'
  '/Users/kooshapari/.claude/*'
  '/Users/kooshapari/.codex/*'
  '/Users/kooshapari/.local/share/forge/*'
  '/tmp/forge-*'
  '/private/tmp/forge-*'
)

# === PROTECTION API ===

# Returns 0 (protected) or 1 (not protected) for a given PID
_thegent_is_protected() {
  local pid="$1"
  [[ -z "$pid" ]] && return 1

  # Read process command (basename)
  local comm ppid cwd
  comm=$(ps -p "$pid" -o comm= 2>/dev/null | tr -d ' ' || true)
  [[ -z "$comm" ]] && return 1
  ppid=$(ps -p "$pid" -o ppid= 2>/dev/null | tr -d ' ' || true)
  cwd=$(lsof -p "$pid" -d cwd 2>/dev/null | tail -1 | awk '{print $NF}' || true)

  # Check command name patterns
  local pattern
  for pattern in "${THEGENT_PROTECTED_PROCESSES[@]}"; do
    # shellcheck disable=SC2053
    if [[ "$comm" == $~pattern ]]; then
      return 0
    fi
  done

  # Check CWD patterns
  if [[ -n "$cwd" ]]; then
    for pattern in "${THEGENT_PROTECTED_CWD_PATTERNS[@]}"; do
      # shellcheck disable=SC2053
      if [[ "$cwd" == $~pattern ]]; then
        return 0
      fi
    done
  fi

  # Check protected ancestry
  local ancestor="$ppid"
  local depth=0
  while [[ -n "$ancestor" && "$ancestor" != "1" && $depth -lt 20 ]]; do
    local ancestor_comm
    ancestor_comm=$(ps -p "$ancestor" -o comm= 2>/dev/null | tr -d ' ' || true)
    [[ -z "$ancestor_comm" ]] && break
    for pattern in "${THEGENT_PROTECTED_PROCESSES[@]}"; do
      # shellcheck disable=SC2053
      if [[ "$ancestor_comm" == $~pattern ]]; then
        return 0
      fi
    done
    ancestor=$(ps -p "$ancestor" -o ppid= 2>/dev/null | tr -d ' ' || true)
    ((depth++))
  done

  return 1
}

# Filter a list of PIDs to remove protected ones
# Usage: _thegent_filter_protected <pid-list>
_thegent_filter_protected() {
  local pid
  for pid in "$@"; do
    if ! _thegent_is_protected "$pid"; then
      echo "$pid"
    fi
  done
}

# Strict-mode kill that refuses protected processes
# Usage: _thegent_safe_kill <signal> <pid>...
_thegent_safe_kill() {
  local sig="$1"
  shift
  local pid killed=0 skipped=0
  for pid in "$@"; do
    if _thegent_is_protected "$pid"; then
      ((skipped++))
      # Audit DENY
      local comm
      comm=$(ps -p "$pid" -o comm= 2>/dev/null | tr -d ' ')
      if [[ -n "${_thegent_fg_audit:-}" ]]; then
        _thegent_fg_audit "DENY" "pid=$pid" "safe_kill sig=$sig comm=$comm reason=protected"
      else
        # Audit log even if guardian not loaded — fall back to protected audit
        local audit_dir="${THEGENT_PROTECTED_AUDIT_DIR:-$HOME/.local/state/thegent}"
        mkdir -p "$audit_dir" 2>/dev/null
        local ts
        ts=$(date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null || echo "now")
        print -r -- "$ts [DENY] target=pid=$pid detail=\"safe_kill sig=$sig comm=$comm reason=protected\"" \
          >> "$audit_dir/audit.log" 2>/dev/null
      fi
    else
      kill -"$sig" "$pid" 2>/dev/null && ((killed++))
    fi
  done
  [[ $skipped -gt 0 ]] && \
    echo "[thegent] protected $skipped process(es) from kill -$sig" >&2
  return 0
}

# === GOVERNANCE STATUS ===
export THEGENT_PROTECTED_GOVERNANCE_LOADED=1
