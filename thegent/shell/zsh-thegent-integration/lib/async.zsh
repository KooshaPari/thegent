# lib/async.zsh - Async operations for thegent integration

# --- Async job management ---
typeset -gA THEGENT_JOBS
typeset -gA THEGENT_JOB_STATUS
typeset -gA THEGENT_JOB_OUTPUT

# --- tgxa: Async execute ---
# Usage: tgxa <command> [callback]
# Run thegent command asynchronously
tgxa() {
  local cmd="$1"
  local callback="$2"
  local job_id="job_$$_$(date +%s)"

  # Create temp file for output
  local output_file="${TMPDIR:-/tmp}/thegent_async_${job_id}.out"
  local pid_file="${TMPDIR:-/tmp}/thegent_async_${job_id}.pid"

  # Run command in background
  (
    local start_time=$(date +%s)
    echo "$start_time" > "$pid_file"

    if [[ "$cmd" == "thegent"* ]]; then
      eval "$cmd" >"$output_file" 2>&1
    else
      eval "thegent $cmd" >"$output_file" 2>&1
    fi

    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Update job status
    print -r -- "EXIT:$exit_code" >> "$output_file"
    print -r -- "DURATION:${duration}s" >> "$output_file"
  ) &

  local bg_pid=$!
  THEGENT_JOBS[$job_id]=$bg_pid
  THEGENT_JOB_STATUS[$job_id]="running"
  THEGENT_JOB_OUTPUT[$job_id]="$output_file"

  print -r -- "[thegent] Started async job: $job_id (PID: $bg_pid)"
  print -r -- "[thegent] Use 'tgxj $job_id' to check status, 'tgxl $job_id' for logs"

  # Return job ID for tracking
  print $job_id
}

# --- tgxj: Job status ---
# Usage: tgxj [job_id]
# Check status of async job(s)
tgxj() {
  local job_id="${1:-}"

  if [[ -z "$job_id" ]]; then
    # List all jobs
    print -r -- "=== Active Jobs ==="
    for j in "${(@k)THEGENT_JOBS}"; do
      local pid=$THEGENT_JOBS[$j]
      local status=$THEGENT_JOB_STATUS[$j]
      if kill -0 "$pid" 2>/dev/null; then
        print -r -- "$j: $status (PID: $pid)"
      else
        print -r -- "$j: completed (PID: $pid)"
      fi
    done
    return 0
  fi

  # Check specific job
  local pid=$THEGENT_JOBS[$job_id]
  if [[ -z "$pid" ]]; then
    print -r -- "tgxj: unknown job: $job_id" >&2
    return 1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    print -r -- "Job: $job_id"
    print -r -- "PID: $pid"
    print -r -- "Status: ${THEGENT_JOB_STATUS[$job_id]}"
  else
    # Job completed, get exit code
    local output_file=$THEGENT_JOB_OUTPUT[$job_id]
    local exit_line
    exit_line=$(grep "^EXIT:" "$output_file" 2>/dev/null)
    print -r -- "Job: $job_id"
    print -r -- "Status: completed"
    print -r -- "Exit: $exit_line"
  fi
}

# --- tgxl: Job logs ---
# Usage: tgxl <job_id> [lines]
# View async job output
tgxl() {
  local job_id="$1"
  local lines="${2:-50}"

  if [[ -z "$job_id" ]]; then
    print -r -- "Usage: tgxl <job_id> [lines]" >&2
    return 1
  fi

  local output_file=$THEGENT_JOB_OUTPUT[$job_id]
  if [[ -z "$output_file" ]] || [[ ! -f "$output_file" ]]; then
    print -r -- "tgxl: no output file for job: $job_id" >&2
    return 1
  fi

  print -r -- "=== Output: $job_id ==="
  tail -n "$lines" "$output_file"
}

# --- tgxk: Kill job ---
# Usage: tgxk <job_id>
# Kill async job
tgxk() {
  local job_id="$1"

  if [[ -z "$job_id" ]]; then
    print -r -- "Usage: tgxk <job_id>" >&2
    return 1
  fi

  local pid=$THEGENT_JOBS[$job_id]
  if [[ -z "$pid" ]]; then
    print -r -- "tgxk: unknown job: $job_id" >&2
    return 1
  fi

  if kill "$pid" 2>/dev/null; then
    THEGENT_JOB_STATUS[$job_id]="killed"
    print -r -- "Killed job: $job_id (PID: $pid)"
  else
    print -r -- "tgxk: failed to kill job: $job_id" >&2
    return 1
  fi
}

# --- tgxw: Wait for job ---
# Usage: tgxw <job_id>
# Wait for async job to complete
tgxw() {
  local job_id="$1"
  local timeout="${2:-300}"

  if [[ -z "$job_id" ]]; then
    print -r -- "Usage: tgxw <job_id> [timeout]" >&2
    return 1
  fi

  local pid=$THEGENT_JOBS[$job_id]
  if [[ -z "$pid" ]]; then
    print -r -- "tgxw: unknown job: $job_id" >&2
    return 1
  fi

  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 1
    ((waited++))
    if ((waited >= timeout)); then
      print -r -- "tgxw: timeout waiting for job: $job_id" >&2
      return 1
    fi
  done

  # Job done, show output
  tgxl "$job_id"
  return 0
}

# --- tgxclean: Clean up completed jobs ---
# Usage: tgxclean
# Clean up old job data
tgxclean() {
  local cleaned=0

  for j in "${(@k)THEGENT_JOBS}"; do
    local pid=$THEGENT_JOBS[$j]
    if ! kill -0 "$pid" 2>/dev/null; then
      # Job completed, clean up
      local output_file=$THEGENT_JOB_OUTPUT[$j]
      rm -f "$output_file"
      unset "THEGENT_JOBS[$j]"
      unset "THEGENT_JOB_STATUS[$j]"
      unset "THEGENT_JOB_OUTPUT[$j]"
      ((cleaned++))
    fi
  done

  print -r -- "Cleaned up $cleaned completed job(s)"
}

# --- Background session management ---
_tg_bg_poll() {
  local session_id="$1"
  local poll_interval="${2:-5}"

  while true; do
    local status
    status=$(thegent ps 2>/dev/null | grep "$session_id")

    if [[ -z "$status" ]]; then
      print -r -- "[thegent] Session $session_id completed"
      break
    fi

    print -r -- "[thegent] Session $session_id: running..."
    sleep "$poll_interval"
  done
}

# --- tgbg: Background thegent with polling ---
# Usage: tgbg <prompt>
# Run thegent in background with status polling
tgbg() {
  local prompt="$*"

  if [[ -z "$prompt" ]]; then
    print -r -- "Usage: tgbg <prompt>" >&2
    return 1
  fi

  # Start in background
  local output
  output=$(thegent run "$prompt" -b 2>&1)

  # Extract session ID
  local session_id
  session_id=$(echo "$output" | grep -oE '[a-f0-9-]{36}' | head -1)

  if [[ -n "$session_id" ]]; then
    print -r -- "[thegent] Started session: $session_id"
    print -r -- "[thegent] Use 'thegent status $session_id' to check progress"

    # Optional: start polling in background
    if [[ "$THEGENT_ASYNC_ENABLE" == "1" ]]; then
      (_tg_bg_poll "$session_id" 10) &
      print -r -- "[thegent] Polling started in background"
    fi
  else
    print -r -- "Failed to extract session ID from output"
    print -r -- "$output"
    return 1
  fi
}

# --- tgsessions: List all sessions ---
tgsessions() {
  if command -v thegent >/dev/null 2>&1; then
    thegent ps "$@"
  else
    print -r -- "thegent command not found" >&2
    return 1
  fi
}

# Auto-cleanup on exit
_tg_async_cleanup() {
  tgxclean 2>/dev/null
}
typeset -ga precmd_functions
precmd_functions+=_tg_async_cleanup

# Initialize async if enabled
if [[ "$THEGENT_ASYNC_ENABLE" == "1" ]]; then
  # Pre-create job tracking arrays
  typeset -gA THEGENT_JOBS
  typeset -gA THEGENT_JOB_STATUS
  typeset -gA THEGENT_JOB_OUTPUT
fi
