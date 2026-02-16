#!/usr/bin/env bash
# Shared hook library — sourced by all hooks.
# Provides stdin parsing, path setup, tool detection, and common helpers.
# Usage:
#   HOOK_NAME="MY-HOOK"
#   source "${BASH_SOURCE[0]%/*}/lib/common.sh"
#   hook_init  # reads stdin, parses common fields, sets paths

# Guard against double-sourcing
[[ -n "${_HOOK_LIB_LOADED:-}" ]] && return 0
_HOOK_LIB_LOADED=1

# Initialize variables to avoid 'unbound variable' errors with set -u
INPUT="${INPUT:-}"
CWD="${CWD:-}"
SESSION_ID="${SESSION_ID:-}"
TOOL_NAME="${TOOL_NAME:-}"
FILE_PATH="${FILE_PATH:-}"
STOP_ACTIVE="${STOP_ACTIVE:-false}"
PROJECT_DIR="${PROJECT_DIR:-}"
VERIFY_DIR="${VERIFY_DIR:-}"
QA_STATE="${QA_STATE:-}"
QUALITY_CONFIG="${QUALITY_CONFIG:-}"
CHANGE_LOG="${CHANGE_LOG:-}"
TOOL_CONTENT="${TOOL_CONTENT:-}"
TOOL_NEW_STRING="${TOOL_NEW_STRING:-}"
TOOL_OLD_STRING="${TOOL_OLD_STRING:-}"
HEAD_SHA="${HEAD_SHA:-}"
export INPUT CWD SESSION_ID TOOL_NAME FILE_PATH STOP_ACTIVE
export PROJECT_DIR VERIFY_DIR QA_STATE QUALITY_CONFIG CHANGE_LOG
export TOOL_CONTENT TOOL_NEW_STRING TOOL_OLD_STRING HEAD_SHA

# If dispatched and only lite functions needed, source lite version
if [[ -n "${_HOOK_DISPATCHED:-}" && -n "${_HOOK_LITE_ONLY:-}" ]]; then
  source "${BASH_SOURCE[0]%/*}/common-lite.sh"
  return 0
fi

# --- EXIT trap: ensures stderr on unexpected failures ---
_hook_exit_trap() {
  local rc=$?
  if [[ $rc -ne 0 && $rc -ne 2 ]]; then
    echo "${HOOK_NAME:-HOOK}: unexpected exit $rc" >&2
  fi
  # Clean up background jobs
  local pids; pids=$(jobs -p 2>/dev/null)
  if [[ -n "$pids" ]]; then
    # Give jobs a moment to finish gracefully
    sleep 0.1
    pids=$(jobs -p 2>/dev/null)
    [[ -n "$pids" ]] && kill $pids 2>/dev/null || true
  fi
}
trap _hook_exit_trap EXIT

# --- Resource limits (P5: prevent memory ballooning) ---
# Limit virtual memory (address space) to 8GB per hook process tree
# This prevents a single tool (like trivy or ruff) from consuming 32GB+ VSZ
if [[ "${OSTYPE}" == "darwin"* ]]; then
  # On macOS, ulimit -v is often ignored or causes issues with memory-mapped files.
  # We use ulimit -m (RSS) if possible, but it is also often restricted.
  # Best effort: set virtual memory limit to 16GB if machine has 16GB RAM.
  ulimit -v 16777216 2>/dev/null || true
  ulimit -m 8388608 2>/dev/null || true # RSS 8GB
else
  ulimit -v 8388608 2>/dev/null || true
  ulimit -m 4194304 2>/dev/null || true # RSS 4GB
fi

# --- Session-level tool cache ---
# Tool paths are stable within a session. Cache them in a file so subsequent
# hook invocations skip ~60ms of command -v subprocess spawns.
_TOOL_CACHE_FILE="/tmp/claude-hook-tools-${EUID:-$(id -u)}.cache"
if [[ -n "${JQ_CMD:-}" && -n "${TIMEOUT_CMD+set}" ]]; then
  # Already set (e.g. by dispatcher export) — skip detection entirely
  :
elif [[ -f "$_TOOL_CACHE_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$_TOOL_CACHE_FILE"
else
  # First invocation this session — detect tools and cache
  JQ_CMD="$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo jq)"
  HUNIQ_CMD="$(command -v huniq 2>/dev/null || true)"
  RG_CMD="$(command -v rg 2>/dev/null || true)"
  if command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD=gtimeout
  elif command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD=timeout
  else
    TIMEOUT_CMD=""
  fi
  # WP-B: Hash utility for cache keys (b3sum 2-5x faster; fallback sha256sum/shasum)
  if command -v b3sum >/dev/null 2>&1; then
    HASH_CMD="b3sum"
    HASH_ARGS=()
  elif command -v sha256sum >/dev/null 2>&1; then
    HASH_CMD="sha256sum"
    HASH_ARGS=()
  else
    HASH_CMD="shasum"
    HASH_ARGS=(-a 256)
  fi
  # Write cache atomically
  printf 'JQ_CMD=%q\nHUNIQ_CMD=%q\nRG_CMD=%q\nTIMEOUT_CMD=%q\nHASH_CMD=%q\nHASH_ARGS=(%s)\n' \
    "$JQ_CMD" "$HUNIQ_CMD" "$RG_CMD" "$TIMEOUT_CMD" "$HASH_CMD" \
    "${HASH_ARGS[*]}" > "$_TOOL_CACHE_FILE.$$"
  mv "$_TOOL_CACHE_FILE.$$" "$_TOOL_CACHE_FILE" 2>/dev/null || true
fi
# Set HASH_ARGS when loaded from cache (HASH_CMD set but HASH_ARGS may be empty)
if [[ -z "${HASH_ARGS+set}" && -n "${HASH_CMD:-}" ]]; then
  [[ "${HASH_CMD}" == *shasum ]] && HASH_ARGS=(-a 256) || HASH_ARGS=()
fi

# WP-B: Hash for cache keys (stdin or file). Do NOT use for attestation/SLSA — those stay SHA-256.
hash_for_cache() {
  local cmd="${HASH_CMD:-shasum}" args=()
  [[ "$cmd" == *shasum ]] && args=(-a 256)
  [[ -n "${HASH_ARGS+set}" && ${#HASH_ARGS[@]} -gt 0 ]] && args=("${HASH_ARGS[@]}")
  if [[ $# -eq 0 ]]; then
    $cmd "${args[@]}" | cut -d' ' -f1
  else
    $cmd "${args[@]}" "$1" | cut -d' ' -f1
  fi
}

# --- Git caching with gitoxide support (Phase 3.5) ---
# Source git cache functions - provides git_cached() for 5-20x git speedup
if [[ -f "${BASH_SOURCE[0]%/*}/git-cache.sh" ]]; then
  # shellcheck disable=SC1090
  source "${BASH_SOURCE[0]%/*}/git-cache.sh"
fi

# --- fd integration (Phase 3.5) ---
# Source fd wrapper - provides fd-based find acceleration (3-5x faster)
if [[ -f "${BASH_SOURCE[0]%/*}/fd-wrapper.sh" ]]; then
  # shellcheck disable=SC1090
  source "${BASH_SOURCE[0]%/*}/fd-wrapper.sh"
fi

# find() override for transparent fd acceleration
# Intercepts all find calls and routes to fd when possible (3-5x faster)
find() {
  # Try fd first if available, fallback to system find
  if command -v fd &>/dev/null; then
    fd_find "$@"
  else
    # Fallback to system find with timeout
    if command -v timeout &>/dev/null; then
      timeout 5 /usr/bin/find "$@"
    else
      /usr/bin/find "$@"
    fi
  fi
}
export -f find

# --- grep/rg integration (Rust tool swap) ---
# Source grep wrapper - routes grep -r and common patterns to ripgrep (2-10x faster)
if [[ -f "${BASH_SOURCE[0]%/*}/grep-wrapper.sh" ]]; then
  # shellcheck disable=SC1090
  source "${BASH_SOURCE[0]%/*}/grep-wrapper.sh"
fi

# --- procs integration (Phase 3.5) ---
# Source procs wrapper - provides process lookup acceleration (2-3x faster)
if [[ -f "${BASH_SOURCE[0]%/*}/procs-wrapper.sh" ]]; then
  # shellcheck disable=SC1090
  source "${BASH_SOURCE[0]%/*}/procs-wrapper.sh"
fi

# sort_unique: always sort and unique. Use huniq for unique if available, but must sort for comm compatibility.
sort_unique() {
  if [[ -n "${HUNIQ_CMD:-}" ]]; then
    "$HUNIQ_CMD" | sort
  else
    sort -u
  fi
}

# --- JS execution helper (Bun > Node) ---
# Prefers Bun for faster execution of JS tools/LSPs.
_js_exec() {
  if command -v bun >/dev/null 2>&1; then
    # Bun x is significantly faster than npx for one-off tool runs
    bun x "$@"
  else
    # Fallback to npx with non-interactive and no-install flags
    npx -y --no-install "$@"
  fi
}
export -f _js_exec

# --- Timestamp (bash builtin, no subprocess) ---
printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1

# --- Core init function ---
# Reads stdin, parses common fields in a single jq call, sets paths.
hook_init() {
  # If dispatcher already parsed input, skip re-parsing
  if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
    return 0
  fi

  # Read stdin once
  INPUT="$(cat)"
  INPUT="${INPUT:-{\}}"

  # Parse all common fields in ONE jq invocation (eliminates ~90 jq spawns across hooks)
  local -a _fields
  # Use read instead of mapfile for bash 3.x compatibility
  _fields=()
  while IFS= read -r line; do
    _fields+=("$line")
  done < <($JQ_CMD -r '
    (.cwd // ""),
    (.session_id // ""),
    (.tool_name // ""),
    (.tool_input.file_path // ""),
    (.stop_hook_active // "false")
  ' <<< "$INPUT" 2>/dev/null || printf '\n\n\n\n\n')

  CWD="${_fields[0]:-}"
  SESSION_ID="${_fields[1]:-}"
  TOOL_NAME="${_fields[2]:-}"
  FILE_PATH="${_fields[3]:-}"
  STOP_ACTIVE="${_fields[4]:-false}"

  # Derive PROJECT_DIR (respect pre-set from stop-dispatcher)
  if [[ -z "${PROJECT_DIR:-}" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="${CWD:-}"
  fi
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    # Cache git rev-parse --show-toplevel result to avoid repeated calls
    PROJECT_DIR="${_CACHED_GIT_TOPLEVEL:-}"
    if [[ -z "$PROJECT_DIR" ]]; then
      PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
      readonly _CACHED_GIT_TOPLEVEL="$PROJECT_DIR"
    fi
  fi
  # If empty/root and we are in the hooks dir, check symlink vs real path
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    if [[ "${BASH_SOURCE[0]}" == *".claude/hooks"* ]]; then
      # Check if this is a symlink to an external project
      local hook_path="${BASH_SOURCE[0]}"
      local resolved_path
      resolved_path="$(readlink -f "$hook_path" 2>/dev/null || echo "$hook_path")"
      # If resolved path is NOT in ~/.claude, use HOME/.claude
      if [[ "$resolved_path" != "$HOME/.claude"* && "$resolved_path" != "$HOME"/.claude* ]]; then
        # External project (thegent) - use HOME/.claude
        PROJECT_DIR="$HOME"
      else
        PROJECT_DIR="${hook_path%/.claude/hooks/*}"
      fi
    fi
  fi
  # Final fallback: pwd, then HOME, never "/" or empty
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="$(pwd)"
  fi
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="${HOME:-.}"
  fi

  # Standard paths — project-specific; use HOME when PROJECT_DIR is root or empty (avoid /.claude)
  local _base="$PROJECT_DIR/.claude"
  [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]] && _base="$HOME/.claude"
  VERIFY_DIR="$_base/verification"
  QA_STATE="$_base/qa-state.json"
  QUALITY_CONFIG="$_base/quality.json"
  CHANGE_LOG="$_base/session-changes.log"

  # Ensure verification directory exists (skip mkdir if already there)
  [[ -d "$VERIFY_DIR" ]] || mkdir -p "$VERIFY_DIR" 2>/dev/null || true

  # Export for subshells
  export INPUT CWD SESSION_ID TOOL_NAME FILE_PATH STOP_ACTIVE
  export PROJECT_DIR VERIFY_DIR QA_STATE QUALITY_CONFIG CHANGE_LOG
}

# --- Content extraction for Write/Edit hooks ---
# Extracts tool_input.content, tool_input.new_string, and tool_input.old_string
# in a single jq call using base64 encoding to handle multiline content safely.
# Sets: TOOL_CONTENT, TOOL_NEW_STRING, TOOL_OLD_STRING
# Must be called AFTER hook_init (uses $INPUT).
hook_extract_content() {
  # If dispatcher already extracted content, skip re-parsing
  if [[ -n "${_HOOK_DISPATCHED:-}" && -n "${TOOL_CONTENT+set}" ]]; then
    return 0
  fi
  # Output one base64-encoded field per line (base64 is newline-free, safe for line reading)
  local -a _b64_lines
  _b64_lines=()
  while IFS= read -r _b64_line; do
    _b64_lines+=("$_b64_line")
  done < <($JQ_CMD -r '
    (.tool_input.content // "" | @base64),
    (.tool_input.new_string // "" | @base64),
    (.tool_input.old_string // "" | @base64)
  ' <<< "$INPUT" 2>/dev/null || printf '\n\n\n')
  TOOL_CONTENT="$(base64 -d <<< "${_b64_lines[0]:-}" 2>/dev/null)" || TOOL_CONTENT=""
  TOOL_NEW_STRING="$(base64 -d <<< "${_b64_lines[1]:-}" 2>/dev/null)" || TOOL_NEW_STRING=""
  TOOL_OLD_STRING="$(base64 -d <<< "${_b64_lines[2]:-}" 2>/dev/null)" || TOOL_OLD_STRING=""
  export TOOL_CONTENT TOOL_NEW_STRING TOOL_OLD_STRING
}

# --- Combined init + content extraction (single jq call, zero base64) ---
# Merges hook_init() and hook_extract_content() into ONE jq invocation.
# Uses NUL-delimited output (\0 cannot appear in JSON strings).
# Saves ~24ms by eliminating the second jq call and 3 base64 decodes.
# Used by pretool-dispatcher.sh and posttool-dispatcher.sh.
# Sets ALL variables that hook_init + hook_extract_content would set.
hook_init_full() {
  # If dispatcher already parsed input, skip re-parsing
  if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
    return 0
  fi

  # Read stdin once
  INPUT="$(cat)"
  INPUT="${INPUT:-{\}}"

  # Single jq call: extract all 8 fields, NUL-delimited.
  # Pipe directly into read (not $()) because bash command substitution strips NUL bytes.
  local _f1 _f2 _f3 _f4 _f5 _f6 _f7 _f8
  {
    IFS= read -r -d '' _f1 || true
    IFS= read -r -d '' _f2 || true
    IFS= read -r -d '' _f3 || true
    IFS= read -r -d '' _f4 || true
    IFS= read -r -d '' _f5 || true
    IFS= read -r -d '' _f6 || true
    IFS= read -r -d '' _f7 || true
    IFS= read -r -d '' _f8 || true
  } < <("$JQ_CMD" -j '
    (.tool_name // ""),
    "\u0000",
    (.tool_input.file_path // ""),
    "\u0000",
    (.session_id // ""),
    "\u0000",
    (.cwd // ""),
    "\u0000",
    (.stop_hook_active // "false"),
    "\u0000",
    (.tool_input.content // ""),
    "\u0000",
    (.tool_input.new_string // ""),
    "\u0000",
    (.tool_input.old_string // "")
  ' <<< "$INPUT" 2>/dev/null)

  TOOL_NAME="$_f1"
  FILE_PATH="$_f2"
  SESSION_ID="$_f3"
  CWD="$_f4"
  STOP_ACTIVE="${_f5:-false}"
  TOOL_CONTENT="$_f6"
  TOOL_NEW_STRING="$_f7"
  TOOL_OLD_STRING="$_f8"

  # Derive PROJECT_DIR (respect pre-set from stop-dispatcher)
  if [[ -z "${PROJECT_DIR:-}" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="${CWD:-}"
  fi
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    # Cache git rev-parse --show-toplevel result to avoid repeated calls
    PROJECT_DIR="${_CACHED_GIT_TOPLEVEL:-}"
    if [[ -z "$PROJECT_DIR" ]]; then
      PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
      readonly _CACHED_GIT_TOPLEVEL="$PROJECT_DIR"
    fi
  fi
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    if [[ "${BASH_SOURCE[0]}" == *".claude/hooks"* ]]; then
      PROJECT_DIR="${BASH_SOURCE[0]%/.claude/hooks/*}"
    fi
  fi
  # Final fallback: pwd, then HOME, never "/" or empty
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="$(pwd)"
  fi
  if [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]]; then
    PROJECT_DIR="${HOME:-.}"
  fi

  # Standard paths — project-specific; use HOME when PROJECT_DIR is root or empty (avoid /.claude)
  local _base="$PROJECT_DIR/.claude"
  [[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]] && _base="$HOME/.claude"
  VERIFY_DIR="$_base/verification"
  QA_STATE="$_base/qa-state.json"
  QUALITY_CONFIG="$_base/quality.json"
  CHANGE_LOG="$_base/session-changes.log"

  # Ensure verification directory exists (skip mkdir if already there)
  [[ -d "$VERIFY_DIR" ]] || mkdir -p "$VERIFY_DIR" 2>/dev/null || true

  # Export for subshells
  export INPUT CWD SESSION_ID TOOL_NAME FILE_PATH STOP_ACTIVE
  export PROJECT_DIR VERIFY_DIR QA_STATE QUALITY_CONFIG CHANGE_LOG
  export TOOL_CONTENT TOOL_NEW_STRING TOOL_OLD_STRING
}

# --- Tool availability cache ---
declare -A _TOOL_CACHE 2>/dev/null || true
_QA_STATE_TOOLS_LOADED=false

# Pre-load all tool states from qa-state.json (once) to avoid per-tool jq spawns.
_load_qa_state_tools() {
  if [[ "$_QA_STATE_TOOLS_LOADED" == "true" ]]; then
    return
  fi
  _QA_STATE_TOOLS_LOADED=true
  if [[ -f "${QA_STATE:-}" ]]; then
    # Single jq call extracts all tool entries; populate cache in bash loop
    local _tool_name _tool_val
    while IFS=$'\t' read -r _tool_name _tool_val; do
      [[ -z "$_tool_name" ]] && continue
      _TOOL_CACHE[$_tool_name]="$_tool_val"
    done < <($JQ_CMD -r '.tools // {} | to_entries[] | "\(.key)\t\(.value)"' "$QA_STATE" 2>/dev/null || true)
  fi
}

tool_available() {
  local tool="$1"
  # Check cache first (handles both pre-loaded and manually cached)
  if [[ -n "${_TOOL_CACHE[$tool]+x}" ]]; then
    echo "${_TOOL_CACHE[$tool]}"
    return
  fi
  # Lazy-load all tools from qa-state.json on first cache miss
  _load_qa_state_tools
  # Re-check cache after bulk load
  if [[ -n "${_TOOL_CACHE[$tool]+x}" ]]; then
    echo "${_TOOL_CACHE[$tool]}"
    return
  fi
  # Fallback to command -v (tool not listed in qa-state.json)
  local result="false"
  if command -v "$tool" >/dev/null 2>&1; then
    result="true"
  fi
  _TOOL_CACHE[$tool]="$result"
  echo "$result"
}

# Alias for tool_available (used by security-pipeline.sh)
_has_tool() {
  tool_available "$1"
}

# --- Run with timeout ---
run_with_timeout() {
  local secs="$1"; shift
  if [[ -n "$TIMEOUT_CMD" ]]; then
    "$TIMEOUT_CMD" "$secs" "$@" 2>&1 || true
  else
    "$@" 2>&1 || true
  fi
}

# --- Lazy: parse changed files from session-changes.log ---
declare -a _CHANGED_FILES=()
_CHANGED_FILES_LOADED=false

parse_changed_files() {
  if [[ "$_CHANGED_FILES_LOADED" == "true" ]]; then
    return
  fi
  _CHANGED_FILES_LOADED=true
  _CHANGED_FILES=()
  [[ ! -f "${CHANGE_LOG:-}" ]] && return
  local _ts _tool fpath
  while IFS='|' read -r _ts _tool fpath; do
    [[ -z "$fpath" ]] && continue
    fpath="${fpath%%[[:space:]]}"
    [[ ! -f "$fpath" ]] && continue
    _CHANGED_FILES+=("$fpath")
  done < "$CHANGE_LOG"
}

# Get changed files array (call parse_changed_files first or this does it)
get_changed_files() {
  parse_changed_files
  if [[ ${#_CHANGED_FILES[@]} -gt 0 ]]; then
    printf '%s\n' "${_CHANGED_FILES[@]}"
  fi
}

# --- Lazy: read quality.json config ---
_QUALITY_CONFIG_LOADED=false
DELIVERY_MODEL=""
CRITICALITY_TIER=""
GOVERNANCE_CONFIG=""

read_quality_config() {
  if [[ "$_QUALITY_CONFIG_LOADED" == "true" ]]; then
    return
  fi
  _QUALITY_CONFIG_LOADED=true
  local qfile="${QUALITY_CONFIG:-}"
  [[ ! -f "$qfile" ]] && return
  local _qparsed
  _qparsed="$($JQ_CMD -r '[
    (.governance.delivery_model // "auto"),
    (.criticality_tier // "established"),
    (.governance // {} | tojson)
  ] | @tsv' "$qfile" 2>/dev/null || echo "auto	established	{}")"
  IFS=$'\t' read -r DELIVERY_MODEL CRITICALITY_TIER GOVERNANCE_CONFIG <<< "$_qparsed"
  export DELIVERY_MODEL CRITICALITY_TIER GOVERNANCE_CONFIG
}

# --- Report writing helpers ---
# All use printf for JSON generation — zero jq spawns.

# Escape a string for JSON embedding (handles \, ", control chars)
_json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"    # backslash
  s="${s//\"/\\\"}"    # double quote
  s="${s//$'\n'/\\n}"  # newline
  s="${s//$'\r'/\\r}"  # carriage return
  s="${s//$'\t'/\\t}"  # tab
  printf '%s' "$s"
}

# Write a simple pass report
write_pass_report() {
  local report_path="$1"
  local gate_name="${2:-${HOOK_NAME:-unknown}}"
  local g; g="$(_json_escape "$gate_name")"
  printf '{"generated_at":"%s","gate":"%s","status":"pass","pass":true,"error_count":0}\n' \
    "$now" "$g" > "$report_path"
}

# Write a not_applicable report (for stub gates)
write_na_report() {
  local report_path="$1"
  local gate_name="${2:-${HOOK_NAME:-unknown}}"
  local g; g="$(_json_escape "$gate_name")"
  printf '{"generated_at":"%s","gate":"%s","status":"not_applicable","pass":true,"error_count":0}\n' \
    "$now" "$g" > "$report_path"
}

# Write a failure report
write_fail_report() {
  local report_path="$1"
  local gate_name="${2:-${HOOK_NAME:-unknown}}"
  local error_count="${3:-1}"
  shift 3
  local errors_json='[]'
  if [[ $# -gt 0 ]]; then
    local items="" e
    for e in "$@"; do
      local escaped; escaped="$(_json_escape "$e")"
      if [[ -z "$items" ]]; then
        items="\"$escaped\""
      else
        items="$items,\"$escaped\""
      fi
    done
    errors_json="[$items]"
  fi
  local g; g="$(_json_escape "$gate_name")"
  printf '{"generated_at":"%s","gate":"%s","status":"fail","pass":false,"error_count":%d,"errors":%s}\n' \
    "$now" "$g" "$error_count" "$errors_json" > "$report_path"
}

# --- Feedback & Nudging ---
# Emits a structured feedback JSON block that thegent output parser can detect.
# Usage: emit_feedback <level> <scope> <message> [code] [suggestion]
# Levels: success, info, suggestion, warning, error
emit_feedback() {
  local level="$1" scope="$2" msg="$3" code="${4:-}" suggest="${5:-}"
  local l; l="$(_json_escape "$level")"
  local s; s="$(_json_escape "$scope")"
  local m; m="$(_json_escape "$msg")"
  local c; c="$(_json_escape "$code")"
  local sug; sug="$(_json_escape "$suggest")"
  
  printf '\n{"type":"feedback","level":"%s","scope":"%s","message":"%s","code":"%s","suggestion":"%s"}\n' \
    "$l" "$s" "$m" "$c" "$sug"
}

# --- State helpers ---

# Check if a state string represents "done"
is_done_state() {
  local s="${1:-}"
  [[ -z "$s" ]] && return 1
  case "$s" in
    released|accepted|verified|done|completed) return 0 ;;
    *) return 1 ;;
  esac
}

# File extension extraction (bash builtin, no external commands)
file_ext() { echo "${1##*.}"; }
file_basename() { echo "${1##*/}"; }

# =============================================================================
# Hook Infrastructure: Caching, Sharing, Circuit Breaker, Debounce, Incremental
# =============================================================================

# --- 1. Git-Aware Cache for Stop Hooks ---
# Cache hook results keyed on git state. If nothing changed since last run,
# skip entirely. Session-scoped, auto-cleaned by OS tmpdir policy.

HOOK_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"

# Generate cache key from hook name + git state
hook_cache_key() {
    local hook_name="$1"
    local changed_files head_sha
    # Use dispatcher-precomputed values if available (saves ~63ms per hook)
    # Use cached git HEAD value if available to avoid repeated git calls
    if [[ -n "${_GIT_HEAD_SHA:-}" ]]; then
      head_sha="$_GIT_HEAD_SHA"
    else
      head_sha="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}"
    fi
    changed_files="${CHANGED_FILES_SORTED:-$(git diff --name-only HEAD 2>/dev/null | sort)}"
    printf '%s\0%s\0%s' "$hook_name" "$head_sha" "$changed_files" | hash_for_cache
}

# Check if cached result exists and is fresh (within TTL seconds)
hook_cache_check() {
    local key="$1" ttl="${2:-60}"
    local rc_file="${HOOK_CACHE_DIR}/${key}.rc"
    [[ -f "$rc_file" ]] || return 1
    local mtime age
    mtime=$(stat -f '%m' "$rc_file" 2>/dev/null || stat -c '%Y' "$rc_file" 2>/dev/null) || return 1
    age=$(( $(date +%s) - mtime ))
    (( age < ttl ))
}

# Read cached result (stdout + exit code)
hook_cache_read() {
    local key="$1"
    [[ -f "${HOOK_CACHE_DIR}/${key}.out" ]] && cat "${HOOK_CACHE_DIR}/${key}.out"
    return "$(cat "${HOOK_CACHE_DIR}/${key}.rc" 2>/dev/null || echo 1)"
}

# Write result to cache
hook_cache_write() {
    local key="$1" rc="$2" output="$3"
    mkdir -p "$HOOK_CACHE_DIR"
    echo "$output" > "${HOOK_CACHE_DIR}/${key}.out"
    echo "$rc" > "${HOOK_CACHE_DIR}/${key}.rc"
}

# --- 2. Cross-Hook Shared Results (Changed Files Index) ---
# Build the changed files list ONCE and share across all Stop hooks.

HOOK_SHARED_DIR="${HOOK_CACHE_DIR}/shared"

# Get or build the shared changed files list
hook_shared_changed_files() {
    local shared_file="${HOOK_SHARED_DIR}/changed_files"
    mkdir -p "$HOOK_SHARED_DIR"

    if [[ -f "$shared_file" ]]; then
        cat "$shared_file"
        return 0
    fi

    # Build once: git diff + untracked, excluding build dirs
    # Use dispatcher-precomputed CHANGED_FILES if available (saves ~52ms)
    {
        if [[ -n "${CHANGED_FILES+set}" ]]; then
            echo "$CHANGED_FILES"
        else
            git diff --name-only HEAD 2>/dev/null
        fi
        git ls-files --others --exclude-standard 2>/dev/null
    } | sort -u | grep -v -E '^(node_modules|vendor|\.git|target|out|dist|build|coverage|__pycache__)/' > "$shared_file"

    cat "$shared_file"
}

# Store arbitrary shared results (e.g., file tree, FR list)
hook_share_result() {
    local name="$1"
    mkdir -p "$HOOK_SHARED_DIR"
    cat > "${HOOK_SHARED_DIR}/${name}"
}

# Get a shared result (returns 1 if not available)
hook_get_shared() {
    local name="$1"
    [[ -f "${HOOK_SHARED_DIR}/${name}" ]] && cat "${HOOK_SHARED_DIR}/${name}" && return 0
    return 1
}

# --- 3. Circuit Breaker for External Tools ---
# Fast-fail when tools are consistently broken. Tracks failure count per tool
# and opens the circuit after threshold failures. Cooldown allows periodic probes.

HOOK_BREAKER_DIR="${HOOK_CACHE_DIR}/breakers"
HOOK_BREAKER_THRESHOLD=3
HOOK_BREAKER_COOLDOWN=300  # 5 min

# Check if tool is circuit-broken
# Returns 0 if circuit is open (tool broken), 1 if closed (tool ok to try)
hook_breaker_check() {
    local tool="$1"
    local state_file="${HOOK_BREAKER_DIR}/${tool}.state"
    [[ -f "$state_file" ]] || return 1  # not broken

    local count ts
    read -r count ts < "$state_file"
    local age=$(( $(date +%s) - ts ))

    # If cooldown expired, allow probe (half-open)
    (( age >= HOOK_BREAKER_COOLDOWN )) && return 1
    # If threshold exceeded, circuit is open (broken)
    (( count >= HOOK_BREAKER_THRESHOLD ))
}

# Record a tool failure
hook_breaker_record_failure() {
    local tool="$1"
    mkdir -p "$HOOK_BREAKER_DIR"
    local state_file="${HOOK_BREAKER_DIR}/${tool}.state"
    local count=0
    [[ -f "$state_file" ]] && read -r count _ < "$state_file"
    echo "$(( count + 1 )) $(date +%s)" > "$state_file"
}

# Reset breaker on success
hook_breaker_reset() {
    local tool="$1"
    rm -f "${HOOK_BREAKER_DIR}/${tool}.state" 2>/dev/null
}

# --- 4. Debounce Helper for PostToolUse Hooks ---
# Allows PostToolUse hooks to batch rapid-fire edits. The first caller becomes
# the "leader" and waits for the debounce window; followers skip immediately.

HOOK_DEBOUNCE_DIR="${HOOK_CACHE_DIR}/debounce"

# Record a file for debounced processing. Returns 0 if this call should proceed
# (i.e., it's the leader after the debounce window), 1 if it should skip (follower).
hook_debounce_file() {
    local hook_name="$1" file="$2" window_ms="${3:-200}"
    mkdir -p "$HOOK_DEBOUNCE_DIR"
    local pending="${HOOK_DEBOUNCE_DIR}/${hook_name}.pending"
    local lock="${HOOK_DEBOUNCE_DIR}/${hook_name}.lock"

    # Append file to pending batch
    echo "$file" >> "$pending"

    # Try to become the debounce leader
    exec 200>"$lock"
    if flock -n 200 2>/dev/null; then
        # Leader: wait for debounce window
        sleep "$(awk "BEGIN{printf \"%.3f\", ${window_ms}/1000}")"
        # Consume pending batch
        local batch
        batch="$(sort -u "$pending" 2>/dev/null)"
        : > "$pending"
        flock -u 200
        exec 200>&-
        echo "$batch"
        return 0  # proceed with batch
    fi
    exec 200>&-
    return 1  # follower, skip
}

# --- 5. Incremental Validation for PreToolUse ---
# Track what files a hook inspected via SHA-256 manifests. Skip re-validation
# when all inputs are unchanged since the last run.

HOOK_MANIFEST_DIR="${HOOK_CACHE_DIR}/manifests"

# Check if hook inputs are unchanged since last run
hook_incremental_check() {
    local hook_name="$1"; shift
    local manifest="${HOOK_MANIFEST_DIR}/${hook_name}.manifest"
    [[ -f "$manifest" ]] || return 1

    while IFS=':' read -r file expected_sha; do
        [[ -f "$file" ]] || return 1
        local actual_sha
        actual_sha="$(hash_for_cache "$file")"
        [[ "$actual_sha" == "$expected_sha" ]] || return 1
    done < "$manifest"
    return 0  # all inputs unchanged
}

# Record current input state
hook_incremental_record() {
    local hook_name="$1"; shift
    local files=("$@")
    mkdir -p "$HOOK_MANIFEST_DIR"
    local manifest="${HOOK_MANIFEST_DIR}/${hook_name}.manifest"
    : > "${manifest}.tmp"
    for f in "${files[@]}"; do
        [[ -f "$f" ]] || continue
        echo "${f}:$(hash_for_cache "$f")" >> "${manifest}.tmp"
    done
    mv -f "${manifest}.tmp" "$manifest"
}

# --- 6. Cache Wrap Convenience ---
# Full cache-or-run wrapper: check cache → if miss, run callback → write result.
# Usage: hook_cache_wrap "hook-name" 120 "extra-key-data" my_main_function
# The callback function's stdout is captured and cached.
hook_cache_wrap() {
    local hook_name="$1" ttl="${2:-120}" extra="$3" callback="$4"
    local key
    key=$(hook_cache_key "$hook_name")
    # Incorporate extra key material if provided
    if [[ -n "$extra" ]]; then
        key=$(printf '%s\0%s' "$key" "$extra" | hash_for_cache)
    fi
    if hook_cache_check "$key" "$ttl"; then
        hook_cache_read "$key"
        return $?
    fi
    # Run callback, capture output and exit code
    local output rc=0
    output="$($callback 2>&1)" || rc=$?
    hook_cache_write "$key" "$rc" "$output"
    [[ -n "$output" ]] && echo "$output"
    return $rc
}

# --- 7. Content-Addressable File Hashing ---
# Hash file contents for cache keys. Caches per-file hashes with mtime check.
HOOK_FILEHASH_DIR="${HOOK_CACHE_DIR}/filehash"

hook_file_hash_cache() {
    mkdir -p "$HOOK_FILEHASH_DIR" 2>/dev/null
    local combined=""
    local f
    for f in "$@"; do
        [[ -f "$f" ]] || continue
        local cache_key hash_file
        cache_key=$(printf '%s' "$f" | hash_for_cache)
        hash_file="${HOOK_FILEHASH_DIR}/${cache_key}"
        # Check if cached hash is still valid (mtime match)
        if [[ -f "$hash_file" ]]; then
            local cached_mtime cached_hash
            IFS=$'\t' read -r cached_mtime cached_hash < "$hash_file"
            local current_mtime
            current_mtime=$(stat -f '%m' "$f" 2>/dev/null || stat -c '%Y' "$f" 2>/dev/null)
            if [[ "$cached_mtime" == "$current_mtime" ]]; then
                combined="${combined}${cached_hash}"
                continue
            fi
        fi
        # Compute and cache
        local file_hash current_mtime
        file_hash=$(hash_for_cache "$f")
        current_mtime=$(stat -f '%m' "$f" 2>/dev/null || stat -c '%Y' "$f" 2>/dev/null)
        printf '%s\t%s' "$current_mtime" "$file_hash" > "$hash_file"
        combined="${combined}${file_hash}"
    done
    # Return combined hash
    printf '%s' "$combined" | hash_for_cache
}

# --- 8. Shared FR IDs ---
# Parse FR IDs from FUNCTIONAL_REQUIREMENTS.md once, share across hooks.
hook_shared_fr_ids() {
    local shared_file="${HOOK_SHARED_DIR}/fr_ids"
    mkdir -p "$HOOK_SHARED_DIR" 2>/dev/null
    if [[ -f "$shared_file" ]]; then
        cat "$shared_file"
        return 0
    fi
    local fr_file="${PROJECT_DIR}/FUNCTIONAL_REQUIREMENTS.md"
    if [[ -f "$fr_file" ]]; then
        grep -oE 'FR-[A-Z]+-[0-9]+' "$fr_file" | sort_unique > "$shared_file"
    else
        touch "$shared_file"
    fi
    cat "$shared_file"
}

# --- 9. Shared FR Index (file:FR pairs) ---
# Pre-build index of all FR references across test directories.
# Format: filepath:FR-XXX-NNN (one per line), same as grep -rHoE output.
# Used by spec-verifier.sh to skip expensive recursive grep.
hook_shared_fr_index() {
    local shared_file="${HOOK_SHARED_DIR}/fr_index"
    mkdir -p "$HOOK_SHARED_DIR" 2>/dev/null
    if [[ -f "$shared_file" ]]; then
        cat "$shared_file"
        return 0
    fi
    local test_dirs=""
    for d in test tests spec specs; do
        [[ -d "${PROJECT_DIR}/${d}" ]] && test_dirs="${test_dirs} ${PROJECT_DIR}/${d}"
    done
    [[ -z "$test_dirs" ]] && { touch "$shared_file"; return 0; }
    local _rg_cmd="${RG_CMD:-$(command -v rg 2>/dev/null || true)}"
    if [[ -n "$_rg_cmd" ]]; then
        # shellcheck disable=SC2086
        "$_rg_cmd" -oN --no-heading \
            -g '!node_modules' -g '!vendor' -g '!.git' -g '!target' \
            -g '!out' -g '!dist' -g '!build' -g '!coverage' \
            -g '!__pycache__' -g '!.process-compose' \
            'FR-[A-Z]+-[0-9]+' $test_dirs > "$shared_file" 2>/dev/null || true
    else
        # shellcheck disable=SC2086
        grep -rHoE \
            --exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git \
            --exclude-dir=target --exclude-dir=out --exclude-dir=dist \
            --exclude-dir=build --exclude-dir=coverage --exclude-dir=__pycache__ \
            --exclude-dir=.process-compose \
            'FR-[A-Z]+-[0-9]+' $test_dirs > "$shared_file" 2>/dev/null || true
    fi
    cat "$shared_file"
}

# ============================================================================
# Hook Config Reader
# ============================================================================
# Read settings from hook-config.yaml (simple grep, no yq dependency).
# Usage: hook_config_get "prewarm_on_session_start" -> "true" or ""
_hook_config_path() {
  local base="${BASH_SOURCE[0]%/*}"
  [[ -f "${base}/../hook-config.yaml" ]] && echo "${base}/../hook-config.yaml"
  [[ -f "${PROJECT_DIR:-.}/.claude/hooks/hook-config.yaml" ]] && echo "${PROJECT_DIR}/.claude/hooks/hook-config.yaml"
  return 0
}

hook_config_get() {
  local key="$1"
  local cfg
  cfg="$(_hook_config_path | head -1)"
  [[ -z "$cfg" || ! -f "$cfg" ]] && return 1
  grep -E "^\s*${key}:" "$cfg" 2>/dev/null | sed -E 's/^[^:]*:[[:space:]]*//' | tr -d '\r\n ' | head -1
}

# Check if a boolean config is true
hook_config_true() {
  local val
  val="$(hook_config_get "$1" 2>/dev/null)"
  [[ "$val" == "true" || "$val" == "yes" ]]
}

# ============================================================================
# Skip Hooks Logic
# ============================================================================
# Allow skipping hooks via SKIP_HOOKS env var (comma-separated, e.g., "test-maturity,security-pipeline")
# Also reads from .claude/qa-local.json if exists.

# Read skip hooks from .claude/qa-local.json if not already loaded
_hook_load_skip_hooks() {
    [[ -n "${_SKIP_HOOKS_LOADED:-}" ]] && return 0
    _SKIP_HOOKS_LOADED=1

    local qa_local="${PROJECT_DIR}/.claude/qa-local.json"
    if [[ -f "$qa_local" ]] && command -v jq >/dev/null 2>&1; then
        local skip_json
        skip_json=$(jq -r '.hooks.skip[]?' "$qa_local" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
        if [[ -n "$skip_json" ]]; then
            export SKIP_HOOKS="${SKIP_HOOKS:-$skip_json}"
        fi
    fi
}

# Check if a hook should be skipped
# Usage: hook_should_skip "hook-name" (without .sh extension)
hook_should_skip() {
    local hook_name="$1"
    local skip_list="${SKIP_HOOKS:-}"
    [[ -z "$skip_list" ]] && return 1
    # Match with or without .sh suffix
    local hook_base="${hook_name%.sh}"
    # Convert comma-separated list to pattern for matching
    [[ ",${skip_list}," == *",${hook_base},"* ]] && return 0
    return 1
}

# ============================================================================
# Hook Execution Control: Smart File-Based Execution
# ============================================================================

# Increased cache TTL: 600s (10 min) instead of 120s (2 min)
# This reduces redundant work across hook invocations
export HOOK_CACHE_TTL="${HOOK_CACHE_TTL:-600}"

# Check if hook should run based on file changes
# Usage: hook_should_run "hook-name" "file-pattern"
# Returns 0 (success) if hook should run, 1 (failure) if should skip
# If no files changed, returns 0 (run for safety)
# Phase 3.5: Uses git_cached() for gitoxide + caching (5-20x speedup)
hook_should_run() {
    local hook_name="${1:-unknown}" pattern="${2:-}"

    # Get changed files - prefer CHANGED_FILES from dispatcher, fallback to git with caching
    local changed_files=""

    # Priority 1: Use dispatcher-provided CHANGED_FILES (already computed, no git needed)
    if [[ -n "${CHANGED_FILES:-}" ]]; then
        changed_files="${CHANGED_FILES}"
    # Priority 2: Only call git if dispatcher didn't provide CHANGED_FILES
    # AND we're in a git repo. Uses git_cached() for gitoxide + caching support.
    elif in_git_repo >/dev/null 2>&1; then
        # CRITICAL: Git command must timeout to avoid hanging for 180s
        # Use git_cached() for:
        #   - gitoxide (gix) support: 5-20x faster than canonical git
        #   - File-based caching: 60s TTL + FS event invalidation
        #   - Graceful fallback to canonical git if gitoxide unavailable
        if type git_cached &>/dev/null; then
            changed_files="$(git_cached diff --name-only HEAD 2>/dev/null || true)"
        elif command -v timeout >/dev/null 2>&1; then
            # Fallback: use original timeout-based git (for systems without git-cache.sh sourced)
            changed_files="$(timeout 5 git diff --name-only HEAD 2>/dev/null || true)"
        else
            # Last resort: try git without timeout (shouldn't happen with dispatcher)
            changed_files="$(git diff --name-only HEAD 2>/dev/null || true)"
        fi
    fi

    # If no changes detected, run hook (safer default - assume first run)
    [[ -z "$changed_files" ]] && return 0

    # If no pattern specified, run for any change
    [[ -z "$pattern" ]] && return 0

    # Check if any changed file matches the pattern
    echo "$changed_files" | grep -qE "$pattern"
}

# Quick check if ANY source files changed (for expensive hooks)
# Usage: any_source_changed && run_expensive_hook
any_source_changed() {
    hook_should_run "check" '\.(py|rs|go|ts|js|tsx|jsx|sh|bash)$'
}

# Check if test files specifically changed
# Usage: test_files_changed && run_test_maturity
test_files_changed() {
    hook_should_run "check" '(test|spec|tests|.*_test\.|.*\.test\.)'
}

# Check if docs specifically changed
# Usage: docs_changed && run_docs_hooks
docs_changed() {
    hook_should_run "check" '\.(md|txt|rst)$'
}

# ============================================================================
# Timeout Configuration
# ============================================================================
# Activity timeout: kill hook if no output for this many seconds
# Max timeout: absolute maximum time before killing regardless of output
export HOOK_IDLE_TIMEOUT="${HOOK_IDLE_TIMEOUT:-180}"
export HOOK_MAX_TIMEOUT="${HOOK_MAX_TIMEOUT:-600}"

# ============================================================================
# Affected Test Selection
# ============================================================================
# Determine which tests to run based on changed files.
# Uses file pattern matching to find related test files.

# Find tests affected by changed source file
# Usage: affected_tests_for_file "src/module.py" -> returns test file paths
affected_tests_for_file() {
    local src="$1"
    local base ext name dir
    base="${src##*/}"
    ext="${base##*.}"
    name="${base%.*}"
    dir="${src%/*}"

    case "$ext" in
        py)
            # Python: test_*.py in same dir, tests/ subdir, or project root
            for candidate in \
                "${dir}/test_${name}.py" \
                "${dir}/tests/test_${name}.py" \
                "${PROJECT_DIR:-.}/tests/test_${name}.py" \
                "${PROJECT_DIR:-.}/test/test_${name}.py" \
                "${PROJECT_DIR:-.}/test_${name}.py"; do
                [[ -f "$candidate" ]] && echo "$candidate"
            done
            ;;
        ts|tsx|js|jsx)
            # TypeScript: *.test.ts, *.spec.ts in same dir or __tests__/
            for candidate in \
                "${dir}/${name}.test.${ext}" \
                "${dir}/${name}.spec.${ext}" \
                "${dir}/__tests__/${name}.test.${ext}" \
                "${dir}/__tests__/${name}.${ext}"; do
                [[ -f "$candidate" ]] && echo "$candidate"
            done
            ;;
        sh|bash)
            # Bash: *.bats files
            for candidate in \
                "${PROJECT_DIR:-.}/test/${name}.bats" \
                "${PROJECT_DIR:-.}/test/unit/${name}.bats" \
                "${PROJECT_DIR:-.}/tests/${name}.bats"; do
                [[ -f "$candidate" ]] && echo "$candidate"
            done
            ;;
        rs)
            # Rust: tests in tests/ or #[test] in same file
            candidate="${PROJECT_DIR:-.}/tests/${name}.rs"
            if [[ -f "$candidate" ]]; then
                echo "$candidate"
            fi
            ;;
    esac
}

# WP-DX1/P7: Find tests from coverage index
# Usage: affected_tests_from_coverage_index "src/thegent/cli.py"
# Build index with: pytest --cov=src --cov-context=test && python scripts/build_coverage_affected_map.py
affected_tests_from_coverage_index() {
    local src="$1"
    [[ "${src##*.}" != "py" ]] && return 0
    
    local index_file
    # Try cache dir first (preferred for P7)
    index_file="${HOOK_CACHE_DIR:-/tmp/claude-hook-cache-$(id -u)}/coverage_affected_map.json"
    if [[ ! -f "$index_file" ]]; then
        # Fallback to root index (WP-DX1 legacy)
        index_file="${PROJECT_DIR:-.}/coverage-index.json"
    fi
    [[ ! -f "$index_file" ]] && return 0

    local project_dir="${PROJECT_DIR:-.}"
    # Normalize to project-relative path
    local rel="${src#"$project_dir"/}"
    rel="${rel#./}"
    rel="${rel//\\//}"
    
    local tests
    tests=$(${JQ_CMD:-jq} -r --arg f "$rel" 'if .[$f] then .[$f][] else empty end' "$index_file" 2>/dev/null)
    [[ -n "$tests" ]] && printf '%s\n' $tests
}

# P7: Find Python tests that import the changed module (import-based selection)
# More accurate than file-pattern for projects with non-standard test layout.
# Usage: affected_tests_from_imports "src/thegent/cli.py"
affected_tests_from_imports() {
    local src="$1"
    [[ "${src##*.}" != "py" ]] && return 0
    local project_dir="${PROJECT_DIR:-.}"
    # Convert path to module: src/thegent/cli.py -> thegent.cli (strip src/, .py)
    local rel="${src#"$project_dir"/}"
    rel="${rel#src/}"
    rel="${rel%.py}"
    local module="${rel//\//.}"
    [[ -z "$module" ]] && return 0
    # Escape dots for regex
    local module_re="${module//./\\.}"
    local module_alt="src.${rel//\//.}"
    local module_alt_re="${module_alt//./\\.}"
    local test_dirs=""
    for d in test tests; do
        [[ -d "${project_dir}/${d}" ]] && test_dirs="${test_dirs} ${project_dir}/${d}"
    done
    [[ -z "$test_dirs" ]] && return 0
    local _rg_cmd
    _rg_cmd=$(command -v rg 2>/dev/null || true)
    if [[ -n "$_rg_cmd" ]]; then
        # Match: from X import, import X (X = module or module_alt)
        "$_rg_cmd" -l --no-heading \
            -g '*.py' -g '!__pycache__' -g '!*.pyc' \
            -e "(from ${module_re}|import ${module_re}|from ${module_alt_re}|import ${module_alt_re})" \
            $test_dirs 2>/dev/null || true
    else
        grep -rEl "(from ${module_re}|import ${module_re}|from ${module_alt_re}|import ${module_alt_re})" \
            $test_dirs 2>/dev/null || true
    fi
}

# P6: Check if Python file can be skipped (tracked + no git diff)
# Returns 0 if skip, 1 if must analyze. Used by quality-gate to filter PY_FILES.
incremental_skip_py_file() {
    local file="$1"
    [[ "${file##*.}" != "py" ]] && return 1
    hook_config_true "incremental_analysis" 2>/dev/null || return 1
    local script_dir="${BASH_SOURCE[0]%/*}"
    [[ -z "$script_dir" ]] && script_dir="."
    local parser="${script_dir}/incremental_parser.py"
    [[ -f "$parser" ]] || return 1
    local project_dir="${PROJECT_DIR:-.}"
    local result
    result=$(python3 "$parser" --check "$file" "$project_dir" 2>/dev/null) || return 1
    [[ "$result" == "skip" ]]
}

# Get all affected tests for a list of changed files
# P7/WP-DX1: When coverage_based_selection, merges file-pattern + coverage-index + import-based for Python
# Usage: get_affected_tests file1.py file2.ts
get_affected_tests() {
    local tests=()
    for file in "$@"; do
        while IFS= read -r test; do
            [[ -n "$test" ]] && tests+=("$test")
        done < <(affected_tests_for_file "$file")
        # P7/WP-DX1: Add coverage-index and import-based for Python when enabled
        if [[ "${file##*.}" == "py" ]] && hook_config_true "coverage_based_selection" 2>/dev/null; then
            while IFS= read -r test; do
                [[ -n "$test" ]] && tests+=("$test")
            done < <(affected_tests_from_coverage_index "$file")
            while IFS= read -r test; do
                [[ -n "$test" ]] && tests+=("$test")
            done < <(affected_tests_from_imports "$file")
        fi
    done
    # Dedupe and return
    printf '%s\n' "${tests[@]}" | sort -u
}

# ============================================================================
# Pre-warm Cache Functions
# ============================================================================
# Warm caches at session start for faster subsequent hooks.

# Pre-warm ruff cache for unchanged files
prewarm_ruff_cache() {
    local project_dir="${PROJECT_DIR:-.}"
    [[ -f "$project_dir/pyproject.toml" ]] || [[ -f "$project_dir/ruff.toml" ]] || return 0

    # Check if ruff cache exists, if not, run once to create
    local cache_dir="${project_dir}/.ruff_cache"
    if [[ ! -d "$cache_dir" ]]; then
        command -v ruff >/dev/null 2>&1 || return 0
        # Warm by running on a small subset first
        ruff check --select=I "$project_dir" 2>/dev/null &
    fi
}

# Pre-warm shellcheck cache
prewarm_shellcheck_cache() {
    local project_dir="${PROJECT_DIR:-.}"
    local cache_dir="${TMPDIR}/shellcheck-cache-$(id -u)"
    [[ -d "$cache_dir" ]] && return 0

    command -v shellcheck >/dev/null 2>&1 || return 0
    mkdir -p "$cache_dir"
    # Pre-scan for shell scripts
    find "$project_dir" -name "*.sh" -type f -exec dirname {} \; 2>/dev/null | sort -u > "$cache_dir/dirs.scan"
}

# Pre-warm the common shared data (changed files, FR list)
prewarm_shared_data() {
    local shared_dir="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)/shared"
    mkdir -p "$shared_dir"

    # Pre-compute changed files if not exists
    if [[ ! -f "${shared_dir}/changed_files" ]]; then
        (
            git diff --name-only HEAD 2>/dev/null
            git ls-files --others --exclude-standard 2>/dev/null
        ) | grep -v -E '^(node_modules|vendor|\.git|target|out|dist|build|coverage)/' \
          | sort -u > "${shared_dir}/changed_files" &
    fi
}

# Run all pre-warms in parallel (non-blocking)
hook_prewarm_all() {
    prewarm_shared_data &
    prewarm_ruff_cache &
    prewarm_shellcheck_cache &
    wait  # Wait for all to complete or fail silently
}

# ============================================================================
# Progress Output for Long-Running Hooks
# ============================================================================
# Print periodic progress to prevent idle timeout.

# Print progress message with timestamp
hook_progress() {
    echo "[$(date +%H:%M:%S)] HOOK_PROGRESS: $1" >&2
}

# Start a background progress reporter
hook_progress_start() {
    local interval="${2:-30}"
    (
        while true; do
            sleep "$interval"
            hook_progress "$1"
        done
    ) &
    echo $!
}

# Kill the progress reporter
hook_progress_stop() {
    local pid="$1"
    [[ -n "$pid" ]] && kill "$pid" 2>/dev/null
}

# ============================================================================
# P5: Learning-Based Skip
# ============================================================================
# Track which hooks pass/fail for file patterns. Skip hooks that consistently
# pass for certain change types. Adaptive based on project history.
# Config: learning_skip in hook-config.yaml (default: false, opt-in).

HOOK_LEARNING_DIR="${HOOK_CACHE_DIR}/learning"
HOOK_LEARNING_MIN_SAMPLES=5
HOOK_LEARNING_PASS_RATE=0.95

# Record hook outcome for a pattern (extension or "all")
# Usage: hook_learning_record "quality-gate" ".py" 0  (0=pass, 1=fail)
hook_learning_record() {
  local hook_name="$1" pattern="$2" passed="${3:-0}"
  [[ -z "$hook_name" || -z "$pattern" ]] && return 0
  mkdir -p "$HOOK_LEARNING_DIR"
  echo "$(date +%s)|$hook_name|$pattern|$passed" >> "${HOOK_LEARNING_DIR}/history.log"
  # Trim to last 1000 entries
  tail -1000 "${HOOK_LEARNING_DIR}/history.log" > "${HOOK_LEARNING_DIR}/history.log.tmp"
  mv "${HOOK_LEARNING_DIR}/history.log.tmp" "${HOOK_LEARNING_DIR}/history.log" 2>/dev/null || true
}

# Check if hook should be skipped based on learning (consistently passes for this pattern)
# Returns 0 if should skip, 1 if should run
hook_learning_should_skip() {
  local hook_name="$1" pattern="$2"
  hook_config_true "learning_skip" 2>/dev/null || return 1
  [[ -f "${HOOK_LEARNING_DIR}/history.log" ]] || return 1
  local samples pass_count total
  samples=$(grep "|${hook_name}|${pattern}|" "${HOOK_LEARNING_DIR}/history.log" 2>/dev/null | tail -100)
  total=$(echo "$samples" | grep -c . 2>/dev/null || echo 0)
  (( total < HOOK_LEARNING_MIN_SAMPLES )) && return 1
  pass_count=$(echo "$samples" | grep "|0$" | grep -c . 2>/dev/null || echo 0)
  local rate=0
  (( total > 0 )) && rate=$(( pass_count * 100 / total ))
  (( rate >= 95 ))  # Skip if 95%+ pass rate (return 0)
}
