# thegent Fork Guardian
# =====================
# Proactive fork-bomb detection and response.
#
# NEVER kills processes in THEGENT_PROTECTED_PROCESSES or with ancestry/CWD
# matching the protected governance (.zsh_protected_processes.zsh).
#
# Detection strategies:
#   1. System fork rate (children/sec across all parents)
#   2. Per-parent fork rate (top-N heaviest forkers)
#   3. Crash-loop detection (same comm starts and dies rapidly)
#   4. Runaway process detection (long-running high-CPU)
#   5. Total process count vs. ulimit
#
# Response tiers:
#   T1 (75-85% util): WARN, log only
#   T2 (85-95% util): THROTTLE, refuse non-essential fork sources
#   T3 (95-98% util): AGGRESSIVE, kill non-protected top forkers
#   T4 (98-100% util): EMERGENCY, kill non-protected recent forkers
#   T5 (>100% / fork() failing): KILL_CLEAR_BOMBS, last-resort cleanup
#
# All actions are logged to ~/.local/state/thegent/fork-guardian.log
#
# Sourced by ~/.zshrc and run periodically by the precmd fork guard
# and the launchd daemon at ~/Library/LaunchAgents/com.thegent.fork-guardian.plist

# === CONFIGURATION ===
: ${THEGENT_FG_STATE_DIR:="$HOME/.local/state/thegent"}
: ${THEGENT_FG_LOG_FILE:="$THEGENT_FG_STATE_DIR/fork-guardian.log"}
: ${THEGENT_FG_PID_FILE:="$THEGENT_FG_STATE_DIR/fork-guardian.pid"}
: ${THEGENT_FG_SNAPSHOT_DIR:="$THEGENT_FG_STATE_DIR/snapshots"}
: ${THEGENT_FG_INTERVAL:=30}               # seconds between checks
: ${THEGENT_FG_FORK_RATE_THRESHOLD:=5}     # children/30s to flag a parent
: ${THEGENT_FG_CRASHTIME_WINDOW:=300}      # 5min window for crash-loop detection
: ${THEGENT_FG_CRASH_THRESHOLD:=5}         # 5 restarts in 5min = loop
: ${THEGENT_FG_RUNAWAY_CPU_THRESHOLD:=80}  # %CPU
: ${THEGENT_FG_RUNAWAY_TIME_THRESHOLD:=900} # 15 minutes
: ${THEGENT_FG_MAX_LOG_SIZE:=10485760}     # 10MB log rotation threshold

# === PROTECTION LOAD ===
# The protected governance must be loaded before this
[[ -f "$HOME/.zsh_protected_processes.zsh" ]] && source "$HOME/.zsh_protected_processes.zsh"
[[ -z "${THEGENT_PROTECTED_GOVERNANCE_LOADED:-}" ]] && {
  echo "[thegent-fg] WARNING: protected governance not loaded, refusing to run" >&2
  return 1
}

mkdir -p "$THEGENT_FG_STATE_DIR" "$THEGENT_FG_SNAPSHOT_DIR" 2>/dev/null

# === LOGGING ===
_thegent_fg_log() {
  local level="$1"
  shift
  local msg="$*"
  local ts
  ts=$(date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null || echo "now")
  local line="$ts [$level] $msg"
  print -r -- "$line" >> "$THEGENT_FG_LOG_FILE" 2>/dev/null
  # Rotate log if oversized
  if [[ -f "$THEGENT_FG_LOG_FILE" ]]; then
    local size
    size=$(stat -f %z "$THEGENT_FG_LOG_FILE" 2>/dev/null || echo 0)
    if (( size > THEGENT_FG_MAX_LOG_SIZE )); then
      mv "$THEGENT_FG_LOG_FILE" "${THEGENT_FG_LOG_FILE}.old" 2>/dev/null
    fi
  fi
  # Also print to stderr if in foreground mode
  [[ "${THEGENT_FG_FOREGROUND:-0}" == "1" ]] && print -r -- "$line" >&2
}

# === SNAPSHOT ===
# Capture full process state. Format: pid ppid comm etime pcpu args
# Output: tab-separated, one PID per line
_thegent_fg_snapshot() {
  local label="${1:-current}"
  local outfile="$THEGENT_FG_SNAPSHOT_DIR/${label}_$$.txt"
  ps -A -o pid=,ppid=,comm=,etime=,pcpu=,args= 2>/dev/null \
    | awk '{
        pid=$1; ppid=$2; comm=$3; etime=$4; pcpu=$5;
        $1=$2=$3=$4=$5=""; sub(/^ /,""); args=$0;
        printf "%s\t%s\t%s\t%s\t%s\t%s\n", pid, ppid, comm, etime, pcpu, args
      }' > "$outfile" 2>/dev/null
  print -r -- "$outfile"
}

# === FORK RATE DETECTION ===
# Compare two snapshots, return parents with >threshold new children
# Args: <prev_snapshot> <curr_snapshot> <threshold>
# Output: parent_pid \t new_children_count
_thegent_fg_fork_rate() {
  local prev="$1" curr="$2" threshold="${3:-5}"
  [[ ! -f "$prev" || ! -f "$curr" ]] && return 0

  # Get current children per PPID
  local curr_children
  curr_children=$(mktemp)
  awk -F'\t' '{print $2}' "$curr" | sort | uniq -c | sort -rn > "$curr_children"

  # Get prev children per PPID
  local prev_children
  prev_children=$(mktemp)
  [[ -f "$prev" ]] && awk -F'\t' '{print $2}' "$prev" | sort | uniq -c | sort -rn > "$prev_children"

  # Compute delta
  join -a 1 -e 0 -o 0,1.2,2.2 -t' ' "$curr_children" "$prev_children" 2>/dev/null \
    | awk -v t="$threshold" '{
        ppid=$1; curr_count=$2; prev_count=$3;
        delta=curr_count - prev_count;
        if (delta >= t) print ppid "\t" delta
      }' | sort -t$'\t' -k2 -rn

  rm -f "$curr_children" "$prev_children" 2>/dev/null
}

# === CRASH-LOOP DETECTION ===
# Count how many times a given comm has started recently
# Uses macOS log show for SIGABRT/exit events
# Args: <comm>
_thegent_fg_crash_count() {
  local comm="$1"
  local window="${2:-$THEGENT_FG_CRASHTIME_WINDOW}"
  # Sum of: crash reports in user diag dir + recent process restarts
  local crash_reports=0
  if [[ -d "$HOME/Library/Logs/DiagnosticReports" ]]; then
    crash_reports=$(find "$HOME/Library/Logs/DiagnosticReports" -name "${comm}-*.ips" \
      -mmin "-$((window/60))" 2>/dev/null | wc -l | tr -d ' ')
  fi
  print -r -- "$crash_reports"
}

# === PROCESS DEEP DIVE ===
# For a PID, return: comm, ppid, etime, pcpu, state, full cmdline, cwd, ancestors
_thegent_fg_inspect() {
  local pid="$1"
  [[ -z "$pid" ]] && return 1
  ps -p "$pid" -o pid=,ppid=,comm=,etime=,pcpu=,state=,command= 2>/dev/null
}

# === TIER EVALUATION ===
# Return tier (1-5) based on current process count vs ulimit
_thegent_fg_tier() {
  local user="${1:-$USER}"
  local pid_count max_procs
  pid_count=$(pgrep -u "$user" 2>/dev/null | wc -l | tr -d ' ')
  max_procs=$(ulimit -u 2>/dev/null || echo 4096)
  [[ -z "$pid_count" || "$pid_count" -lt 1 ]] && pid_count=0
  [[ -z "$max_procs" || "$max_procs" -lt 1 ]] && max_procs=4096

  local pct=$((pid_count * 100 / max_procs))
  if (( pct >= 100 )); then print 5
  elif (( pct >= 98 )); then print 4
  elif (( pct >= 95 )); then print 3
  elif (( pct >= 85 )); then print 2
  elif (( pct >= 75 )); then print 1
  else print 0
  fi
}

# === RESPONSE: TIER 1 (WARN) ===
_thegent_fg_t1_warn() {
  local pid_count=$1 max_procs=$2 pct=$3
  _thegent_fg_log "WARN" "Tier 1: process count ${pid_count}/${max_procs} (${pct}%)"
  print -r -- "[thegent-fg] WARN: process count ${pid_count}/${max_procs} (${pct}%)" >&2
}

# === RESPONSE: TIER 2 (THROTTLE) ===
# Mark a "throttle mode" flag — non-essential agents should pause
# Also: list top 10 non-protected forkers for visibility
_thegent_fg_t2_throttle() {
  local pid_count=$1 max_procs=$2 pct=$3
  _thegent_fg_log "THROTTLE" "Tier 2: ${pid_count}/${max_procs} (${pct}%) — entering throttle mode"

  # Write a throttle marker that other scripts can check
  local throttle_file="$THEGENT_FG_STATE_DIR/throttle"
  print -r -- "$(date +%s)" > "$throttle_file"

  # Audit the throttle entry
  _thegent_fg_audit "THROTTLE" "-" "tier=2 count=$pid_count max=$max_procs pct=$pct marker=$throttle_file"

  print -r -- "[thegent-fg] THROTTLE mode active. Check $THEGENT_FG_LOG_FILE for details." >&2
}

# === RESPONSE: TIER 3 (AGGRESSIVE) ===
# Identify and kill top non-protected fork-bombing processes
# Strategy: find PIDs whose parent has been spawning children rapidly
_thegent_fg_t3_aggressive() {
  local pid_count=$1 max_procs=$2 pct=$3
  _thegent_fg_log "AGGRESSIVE" "Tier 3: ${pid_count}/${max_procs} (${pct}%)"

  # Snapshot now and 30s ago
  local prev_snap
  prev_snap=$(ls -t "$THEGENT_FG_SNAPSHOT_DIR"/*.txt 2>/dev/null | grep -v "_$$\.txt" | head -1)
  local curr_snap
  curr_snap=$(_thegent_fg_snapshot "t3_$$")

  # Find parents with high fork rate
  local top_forkers
  top_forkers=$(_thegent_fg_fork_rate "$prev_snap" "$curr_snap" 10 2>/dev/null | head -20)

  if [[ -z "$top_forkers" ]]; then
    _thegent_fg_log "AGGRESSIVE" "No top forkers found, escalating to tier 4"
    return 1
  fi

  # For each top forker, find its children and kill non-protected ones
  local killed=0 skipped=0
  while IFS=$'\t' read -r ppid fork_count; do
    [[ -z "$ppid" || "$ppid" == "0" || "$ppid" == "1" ]] && continue

    # Get the parent's info
    local parent_info
    parent_info=$(_thegent_fg_inspect "$ppid" 2>/dev/null)
    [[ -z "$parent_info" ]] && continue

    # Check if parent itself is protected
    if _thegent_is_protected "$ppid" 2>/dev/null; then
      ((skipped++))
      local parent_comm
      parent_comm=$(ps -p "$ppid" -o comm= 2>/dev/null | tr -d ' ')
      _thegent_fg_log "AGGRESSIVE" "Skip parent $ppid ($parent_comm, protected)"
      _thegent_fg_audit "SKIP" "ppid=$ppid" "tier=3 parent_protected comm=$parent_comm fork_count=$fork_count"
      continue
    fi

    # Get children of this parent
    local children
    children=$(awk -F'\t' -v p="$ppid" '$2 == p {print $1}' "$curr_snap" 2>/dev/null)
    for child in ${(f)children}; do
      [[ -z "$child" ]] && continue
      if _thegent_is_protected "$child" 2>/dev/null; then
        ((skipped++))
        local child_comm
        child_comm=$(ps -p "$child" -o comm= 2>/dev/null | tr -d ' ')
        _thegent_fg_audit "SKIP" "pid=$child" "tier=3 child_protected comm=$child_comm parent=$ppid"
      else
        # SIGTERM first, then SIGKILL after 5s
        kill -TERM "$child" 2>/dev/null
        local child_comm
        child_comm=$(ps -p "$child" -o comm= 2>/dev/null | tr -d ' ')
        _thegent_fg_log "AGGRESSIVE" "SIGTERM $child ($child_comm, parent=$ppid fork_count=$fork_count)"
        _thegent_fg_audit "KILL" "pid=$child" "tier=3 sig=TERM comm=$child_comm parent=$ppid"
        ((killed++))
      fi
    done
  done <<< "$top_forkers"

  _thegent_fg_log "AGGRESSIVE" "Killed $killed non-protected children, skipped $skipped protected"
  _thegent_fg_audit "TIER3_DONE" "-" "killed=$killed skipped=$skipped"
  print -r -- "[thegent-fg] AGGRESSIVE: killed $killed, skipped $skipped protected" >&2
  return 0
}

# === RESPONSE: TIER 4 (EMERGENCY) ===
# Last-resort: kill all recent non-protected processes that look like bombs
_thegent_fg_t4_emergency() {
  local pid_count=$1 max_procs=$2 pct=$3
  _thegent_fg_log "EMERGENCY" "Tier 4: ${pid_count}/${max_procs} (${pct}%)"

  # Get all PIDs that are not protected and have been alive <5min
  # (assume recent spawns are the bomb)
  local candidates
  candidates=$(ps -A -o pid=,etime=,comm= 2>/dev/null \
    | awk '{
        # etime format: [[dd-]hh:]mm:ss
        etime=$2;
        # Parse seconds — rough heuristic
        if (etime ~ /^[0-9]+-[0-9]+:[0-9]+:[0-9]+$/) {
          split(etime, p, /[-:]/);
          secs = p[1]*86400 + p[2]*3600 + p[3]*60 + p[4];
        } else if (etime ~ /^[0-9]+:[0-9]+:[0-9]+$/) {
          split(etime, p, /[:]/);
          secs = p[1]*3600 + p[2]*60 + p[3];
        } else if (etime ~ /^[0-9]+:[0-9]+$/) {
          split(etime, p, /[:]/);
          secs = p[1]*60 + p[2];
        } else {
          secs = etime + 0;
        }
        if (secs <= 300) print $1 "\t" secs "\t" $3;
      }' | head -200)

  local killed=0 skipped=0
  while IFS=$'\t' read -r pid age comm; do
    [[ -z "$pid" ]] && continue
    if _thegent_is_protected "$pid" 2>/dev/null; then
      ((skipped++))
      _thegent_fg_audit "SKIP" "pid=$pid" "tier=4 protected comm=$comm age=${age}s"
    else
      # Skip kernel/system processes (low PID)
      if (( pid < 100 )); then
        continue
      fi
      kill -TERM "$pid" 2>/dev/null
      _thegent_fg_log "EMERGENCY" "SIGTERM pid=$pid comm=$comm age=${age}s"
      _thegent_fg_audit "KILL" "pid=$pid" "tier=4 sig=TERM comm=$comm age=${age}s"
      ((killed++))
    fi
  done <<< "$candidates"

  _thegent_fg_log "EMERGENCY" "Killed $killed recent non-protected, skipped $skipped protected"
  _thegent_fg_audit "TIER4_DONE" "-" "killed=$killed skipped=$skipped"
  print -r -- "[thegent-fg] EMERGENCY: killed $killed, skipped $skipped protected" >&2
}

# === RESPONSE: TIER 5 (KILL_CLEAR_BOMBS) ===
# When fork() itself is failing — kill only obvious bombs
# (multiple PIDs of the same comm name = clearly a fork loop)
_thegent_fg_t5_clear_bombs() {
  local pid_count=$1 max_procs=$2 pct=$3
  _thegent_fg_log "CRITICAL" "Tier 5: ${pid_count}/${max_procs} (${pct}%) — fork() failing"

  # Find comms with >10 PIDs that are NOT protected
  local bomb_comms
  bomb_comms=$(ps -A -o comm= 2>/dev/null | sort | uniq -c | sort -rn \
    | awk '$1 > 10 {print $0}' \
    | while read -r count comm; do
        [[ -z "$comm" ]] && continue
        # Skip protected
        local protected=0
        local pattern
        for pattern in "${THEGENT_PROTECTED_PROCESSES[@]}"; do
          # shellcheck disable=SC2053
          if [[ "$comm" == $~pattern ]]; then
            protected=1
            break
          fi
        done
        if [[ $protected -eq 0 ]]; then
          echo "$count $comm"
        fi
      done)

  if [[ -z "$bomb_comms" ]]; then
    _thegent_fg_log "CRITICAL" "No clear bombs detected — system may need manual intervention"
    return 1
  fi

  local killed=0 skipped=0
  while read -r count comm; do
    [[ -z "$comm" ]] && continue
    # Kill the most-recent of this comm (likely the bomb spawner)
    local victims
    victims=$(ps -A -o pid=,comm=,etime= 2>/dev/null \
      | awk -v c="$comm" '$2 == c {print $1 "\t" $3}' \
      | sort -t$'\t' -k2 -r | head -20)

    while IFS=$'\t' read -r pid etime; do
      [[ -z "$pid" ]] && continue
      if _thegent_is_protected "$pid" 2>/dev/null; then
        ((skipped++))
        _thegent_fg_audit "SKIP" "pid=$pid" "tier=5 protected comm=$comm count=$count"
      else
        kill -KILL "$pid" 2>/dev/null
        _thegent_fg_log "CRITICAL" "SIGKILL pid=$pid comm=$comm count=$count etime=$etime"
        _thegent_fg_audit "KILL" "pid=$pid" "tier=5 sig=KILL comm=$comm count=$count etime=$etime"
        ((killed++))
      fi
    done <<< "$victims"
  done <<< "$bomb_comms"

  _thegent_fg_log "CRITICAL" "Killed $killed bomb candidates, skipped $skipped protected"
  _thegent_fg_audit "TIER5_DONE" "-" "killed=$killed skipped=$skipped"
  print -r -- "[thegent-fg] CRITICAL: killed $killed, skipped $skipped protected" >&2
}

# === MAIN CHECK ===
# Run one full detection + response cycle
_thegent_fg_check() {
  local user="${1:-$USER}"
  local pid_count max_procs pct tier
  pid_count=$(pgrep -u "$user" 2>/dev/null | wc -l | tr -d ' ')
  max_procs=$(ulimit -u 2>/dev/null || echo 4096)
  [[ -z "$pid_count" || "$pid_count" -lt 1 ]] && pid_count=0
  [[ -z "$max_procs" || "$max_procs" -lt 1 ]] && max_procs=4096
  pct=$((pid_count * 100 / max_procs))
  tier=$(_thegent_fg_tier "$user")

  _thegent_fg_log "CHECK" "tier=$tier count=$pid_count/$max_procs (${pct}%)"

  case $tier in
    0) ;;  # healthy, no-op
    1) _thegent_fg_t1_warn "$pid_count" "$max_procs" "$pct" ;;
    2)   _thegent_fg_t2_throttle "$pid_count" "$max_procs" "$pct" ;;
    3)   _thegent_fg_t3_aggressive "$pid_count" "$max_procs" "$pct" ;;
    4)   _thegent_fg_t4_emergency "$pid_count" "$max_procs" "$pct" ;;
    5)   _thegent_fg_t5_clear_bombs "$pid_count" "$max_procs" "$pct" ;;
  esac

  # Always save a snapshot for next delta
  _thegent_fg_snapshot "auto" >/dev/null

  # Cleanup old snapshots (keep last 10)
  ls -t "$THEGENT_FG_SNAPSHOT_DIR"/*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

  return $tier
}

# === STATUS ===
_thegent_fg_status() {
  local pid_count max_procs pct tier
  pid_count=$(pgrep -u "$USER" 2>/dev/null | wc -l | tr -d ' ')
  max_procs=$(ulimit -u 2>/dev/null || echo 4096)
  pct=$((pid_count * 100 / max_procs))
  tier=$(_thegent_fg_tier "$USER")

  print -r -- "=== FORK GUARDIAN STATUS ==="
  print -r -- "Process count: $pid_count / $max_procs (${pct}%)"
  print -r -- "Tier: $tier"
  case $tier in
    0)  print -r -- "Status: OK" ;;
    1)  print -r -- "Status: WARN" ;;
    2)  print -r -- "Status: THROTTLE" ;;
    3)  print -r -- "Status: AGGRESSIVE" ;;
    4)  print -r -- "Status: EMERGENCY" ;;
    5)  print -r -- "Status: CRITICAL (fork() failing)" ;;
  esac
  print -r -- "Log: $THEGENT_FG_LOG_FILE"
  print -r -- "Snapshots: $THEGENT_FG_SNAPSHOT_DIR"

  # Show recent log entries
  if [[ -f "$THEGENT_FG_LOG_FILE" ]]; then
    print -r -- ""
    print -r -- "--- Last 5 log entries ---"
    tail -5 "$THEGENT_FG_LOG_FILE" 2>/dev/null
  fi
}

# === ALIASES ===
alias forkguard='_thegent_fg_check'
alias fork-guardian='_thegent_fg_status'
alias forkstatus='_thegent_fg_status'

# === HELP ===
_thegent_fg_help() {
  cat <<'EOF'
thegent Fork Guardian
=====================

Proactive fork-bomb detection and tiered response.

USAGE
  thegent-fork-guardian <command>     # CLI wrapper (see ~/bin/thegent-fork-guardian)
  forkguard                            # alias: run one check cycle
  forkstatus                           # alias: show status
  forkdiag                             # alias: diagnostic report (see .zsh_fork_diagnostic.zsh)

PROTECTED PROCESSES (NEVER killed)
  forge*, forge-dev*, ghostty*, claude*, codex*, cursor*, aider*, cline*,
  continue*, windsurf*, nvim, vim, code, emacs*, helix,
  login, zsh, bash, fish, tmux*, screen,
  cargo, rustc, node, python*, ipython*, jupyter*, watchman*

  Governance: ~/.zsh_protected_processes.zsh
  Helper API: _thegent_is_protected <pid> / _thegent_filter_protected <pids> /
              _thegent_safe_kill <sig> <pids>...

RESPONSE TIERS
  T0  < 75%   silent (no log) — healthy
  T1  75-85%  WARN log only
  T2  85-95%  THROTTLE — sets ~/.local/state/thegent/throttle marker
  T3  95-98%  AGGRESSIVE — SIGTERM non-protected children of top forkers
  T4  98-100% EMERGENCY — SIGTERM all non-protected procs alive <5min
  T5  >100%   CRITICAL — SIGKILL any comm with >10 PIDs not protected

DETECTION
  1. ulimit -u vs pgrep -u $USER count (primary)
  2. Per-parent fork rate (snapshot diff, ≥10 new children/30s)
  3. Crash-loop count in ~/Library/Logs/DiagnosticReports/
  4. Runaway CPU (TBI — planned)
  5. Ancestry walk — protected ancestor = protected child

FILES
  Config:         ~/.zsh_fork_guardian.zsh
  Protected list: ~/.zsh_protected_processes.zsh
  CLI:            ~/bin/thegent-fork-guardian
  LaunchAgent:    ~/Library/LaunchAgents/com.thegent.fork-guardian.plist
  State:          ~/.local/state/thegent/
    - fork-guardian.log     (rotated at 10MB)
    - fork-guardian.pid     (current daemon PID)
    - snapshots/            (10 most recent ps snapshots)
    - throttle              (epoch seconds when T2+ active)
    - audit.log             (every protected-skip + every kill)
  Diagnostic:     ~/.zsh_fork_diagnostic.zsh

INTERVAL
  30s between checks (configurable via THEGENT_FG_INTERVAL)

TUNING
  Edit these env vars in your .zshrc.local before sourcing:
    THEGENT_FG_INTERVAL              seconds between checks (default 30)
    THEGENT_FG_FORK_RATE_THRESHOLD   new children per parent per cycle (default 5)
    THEGENT_FG_CRASHTIME_WINDOW      seconds to look back for crash reports (default 300)
    THEGENT_FG_CRASH_THRESHOLD       crashes in window to flag a comm (default 5)
    THEGENT_FG_MAX_LOG_SIZE          log rotation threshold in bytes (default 10MB)

SEE ALSO
  forkdiag(1)              one-glance diagnostic
  thegent-fork-guardian(1) CLI with start/stop/restart/status/check/cleanup
  _thegent_is_protected(3) strict PID-level protected check
  _thegent_safe_kill(3)    refuse-to-kill-protected wrapper
EOF
}
alias forkhelp='_thegent_fg_help'

# === AUDIT ===
# Every protected-skip and every kill MUST be recorded to a separate audit log.
# This is the legal/forensic record. Distinct from the operational log.
_thegent_fg_audit() {
  local action="$1"  # SKIP|KILL|DENY|THROTTLE|RESET
  shift
  local target="$1"  # pid, comm, or "-"
  shift
  local detail="$*"
  local ts
  ts=$(date '+%Y-%m-%dT%H:%M:%S%z' 2>/dev/null || echo "now")
  local audit_file="$THEGENT_FG_STATE_DIR/audit.log"
  local line="$ts [$action] target=$target detail=\"$detail\""
  print -r -- "$line" >> "$audit_file" 2>/dev/null
  # Also mirror to operational log for correlation
  _thegent_fg_log "AUDIT" "$line"
}

# Export for use by other scripts
typeset -f _thegent_fg_audit >/dev/null 2>&1 && \
  autoload -Uz _thegent_fg_audit 2>/dev/null

# Mark loaded
export THEGENT_FORK_GUARDIAN_LOADED=1
