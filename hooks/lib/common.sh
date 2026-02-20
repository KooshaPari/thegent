#!/usr/bin/env zsh
# Shared hook library — sourced by all hooks.
# Provides stdin parsing, path setup, tool detection, and common helpers.
# Usage:
#   HOOK_NAME="MY-HOOK"
#   source "${(%):-%x:h}/lib/common.sh"
#   hook_init  # reads stdin, parses common fields, sets paths

# Guard against double-sourcing
[[ -n "${_HOOK_LIB_LOADED:-}" ]] && return 0
_HOOK_LIB_LOADED=1

# ZSH compatibility: ensure we have bash-like word splitting if needed
# but better to just use proper quoting.
if [ -n "${ZSH_VERSION:-}" ]; then
  # setopt shwordsplit # optional, but better to fix the code
  :
fi

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
THEGENT_TOOL_BIN_PATH="${THEGENT_TOOL_BIN_PATH:-/usr/bin:/opt/homebrew/bin:/bin:/usr/sbin:/sbin:/Users/kooshapari/.cargo/bin}"

# --- Binary Resolution (Rust Runtime) ---
if [[ -z "${THEGENT_HOOKS_BIN:-}" ]]; then
  if [[ -x "${PROJECT_DIR:-.}/crates/target/release/thegent-hooks" ]]; then
    THEGENT_HOOKS_BIN="${PROJECT_DIR:-.}/crates/target/release/thegent-hooks"
  elif [[ -x "${PROJECT_DIR:-.}/crates/target/debug/thegent-hooks" ]]; then
    THEGENT_HOOKS_BIN="${PROJECT_DIR:-.}/crates/target/debug/thegent-hooks"
  elif [[ -x "${PROJECT_DIR:-.}/target/release/thegent-hooks" ]]; then
    THEGENT_HOOKS_BIN="${PROJECT_DIR:-.}/target/release/thegent-hooks"
  elif [[ -x "${PROJECT_DIR:-.}/target/debug/thegent-hooks" ]]; then
    THEGENT_HOOKS_BIN="${PROJECT_DIR:-.}/target/debug/thegent-hooks"
  elif command -v thegent-hooks >/dev/null 2>&1; then
    THEGENT_HOOKS_BIN="$(command -v thegent-hooks)"
  fi
fi

if [[ -z "${THEGENT_SHIMS_BIN:-}" ]]; then
  if [[ -x "${PROJECT_DIR:-.}/crates/target/release/thegent-shims" ]]; then
    THEGENT_SHIMS_BIN="${PROJECT_DIR:-.}/crates/target/release/thegent-shims"
  elif [[ -x "${PROJECT_DIR:-.}/crates/target/debug/thegent-shims" ]]; then
    THEGENT_SHIMS_BIN="${PROJECT_DIR:-.}/crates/target/debug/thegent-shims"
  elif [[ -x "${PROJECT_DIR:-.}/target/release/thegent-shims" ]]; then
    THEGENT_SHIMS_BIN="${PROJECT_DIR:-.}/target/release/thegent-shims"
  elif [[ -x "${PROJECT_DIR:-.}/target/debug/thegent-shims" ]]; then
    THEGENT_SHIMS_BIN="${PROJECT_DIR:-.}/target/debug/thegent-shims"
  elif command -v thegent-shims >/dev/null 2>&1; then
    THEGENT_SHIMS_BIN="$(command -v thegent-shims)"
  fi
fi

# Fallback/Safety: Ensure Rust binaries are found or fail
if [[ -z "${THEGENT_HOOKS_BIN:-}" ]] || [[ -z "${THEGENT_SHIMS_BIN:-}" ]]; then
  echo "CRITICAL: thegent Rust runtime binaries not found. Migration is mandatory." >&2
  # exit 1 # Don't exit here as it might break startup, but let hooks fail
fi

# Overrides using thegent-shims
if [[ -n "${THEGENT_SHIMS_BIN:-}" ]]; then
  jq() { "$THEGENT_SHIMS_BIN" jq "$@"; }
  grep() { "$THEGENT_SHIMS_BIN" grep "$@"; }
  find() { "$THEGENT_SHIMS_BIN" find "$@"; }
  pgrep() { "$THEGENT_SHIMS_BIN" pgrep "$@"; }
  wc() { "$THEGENT_SHIMS_BIN" wc "$@"; }
  date() { "$THEGENT_SHIMS_BIN" date "$@"; }
  tr() { "$THEGENT_SHIMS_BIN" tr "$@"; }
  codex() { "$THEGENT_SHIMS_BIN" agent codex "$@"; }
  copilot() { "$THEGENT_SHIMS_BIN" agent copilot "$@"; }
  dex() { "$THEGENT_SHIMS_BIN" agent dex "$@"; }
  claude() { "$THEGENT_SHIMS_BIN" agent claude "$@"; }
  cursor() { "$THEGENT_SHIMS_BIN" agent cursor "$@"; }
  git() { "$THEGENT_HOOKS_BIN" git "$@"; }
  uv() { "$THEGENT_HOOKS_BIN" uv "$@"; }
  npm() { "$THEGENT_HOOKS_BIN" npm "$@"; }
  pnpm() { "$THEGENT_HOOKS_BIN" pnpm "$@"; }
  bun() { "$THEGENT_HOOKS_BIN" bun "$@"; }
  yarn() { "$THEGENT_HOOKS_BIN" yarn "$@"; }
  pip() { "$THEGENT_HOOKS_BIN" pip "$@"; }
  poetry() { "$THEGENT_HOOKS_BIN" poetry "$@"; }
  cargo() { "$THEGENT_HOOKS_BIN" cargo "$@"; }
  go() { "$THEGENT_HOOKS_BIN" go "$@"; }
  ruff() { "$THEGENT_HOOKS_BIN" ruff "$@"; }
  pytest() { "$THEGENT_HOOKS_BIN" pytest "$@"; }
  sed() { "$THEGENT_HOOKS_BIN" sed "$@"; }
  cp() { "$THEGENT_HOOKS_BIN" cp "$@"; }
  mv() { "$THEGENT_HOOKS_BIN" mv "$@"; }
  rm() { "$THEGENT_HOOKS_BIN" rm "$@"; }
fi

# Get script path in a cross-shell compatible way
if [ -n "${ZSH_VERSION:-}" ]; then
  _SCRIPT_PATH="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
  _SCRIPT_PATH="${BASH_SOURCE[0]}"
else
  _SCRIPT_PATH="$0"
fi
_SCRIPT_DIR="${_SCRIPT_PATH%/*}"

# Migration complete: Rust runtime enabled by default.


# --- EXIT trap: ensures stderr on unexpected failures ---
_hook_exit_trap() {
  local rc=$?
  if [[ $rc -ne 0 && $rc -ne 2 ]]; then
    echo "${HOOK_NAME:-HOOK}: unexpected exit $rc" >&2
  fi
  local pids; pids=$(jobs -p 2>/dev/null)
  if [[ -n "$pids" ]]; then
    pids=$(jobs -p 2>/dev/null)
    [[ -n "$pids" ]] && kill $pids 2>/dev/null || true
  fi
}
trap _hook_exit_trap EXIT

# --- Resource limits ---
if [[ "${OSTYPE}" == "darwin"* ]]; then
  ulimit -v 16777216 2>/dev/null || true
  ulimit -m 8388608 2>/dev/null || true
else
  ulimit -v 8388608 2>/dev/null || true
  ulimit -m 4194304 2>/dev/null || true
fi

# Hash for cache keys (Rust blake3)
hash_for_cache() {
  if [[ $# -eq 0 ]]; then
    local tmp; tmp="$(mktemp)"
    cat > "$tmp"
    hook_rust_runtime_invoke file-hash "$tmp" 2>/dev/null
    rm -f "$tmp"
  else
    hook_rust_runtime_invoke file-hash "$1" 2>/dev/null
  fi
}

# sort_unique: always sort and unique.
sort_unique() {
  sort -u
}

# --- JS execution helper (Bun > Node) ---
_js_exec() {
  if command -v bun >/dev/null 2>&1; then
    bun x "$@"
  else
    npx -y --no-install "$@"
  fi
}
export -f _js_exec

# --- Timestamp ---
if ! printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1 2>/dev/null; then
  now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# --- Rust runtime invocation ---
hook_rust_runtime_enabled() { return 0; }

hook_rust_runtime_path() {
  echo "${THEGENT_HOOKS_BIN:-thegent-hooks}"
}

hook_rust_runtime_invoke() {
  local runtime
  runtime="$(hook_rust_runtime_path)"
  "$runtime" "$@"
}

_hook_runtime_apply_exports() {
  local payload="$1"
  [[ -n "$payload" ]] || return 1

  local line key value
  while IFS= read -r line; do
    [[ -n "$line" && "$line" == *=* ]] || continue
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in
      INPUT|CWD|SESSION_ID|TOOL_NAME|FILE_PATH|STOP_ACTIVE|PROJECT_DIR|VERIFY_DIR|QA_STATE|QUALITY_CONFIG|CHANGE_LOG|TOOL_CONTENT|TOOL_NEW_STRING|TOOL_OLD_STRING)
        printf -v "$key" '%s' "$value"
        export "$key"
        ;;
    esac
  done <<< "$payload"

  [[ -n "${PROJECT_DIR:-}" ]] || return 1
  [[ -n "${VERIFY_DIR:-}" ]] || VERIFY_DIR="${PROJECT_DIR}/.claude/verification"
  [[ -d "$VERIFY_DIR" ]] || mkdir -p "$VERIFY_DIR" 2>/dev/null || true
  export VERIFY_DIR
  return 0
}

_hook_runtime_init_from_input() {
  local input_json="$1"
  local payload
  payload="$(hook_rust_runtime_invoke init <<< "$input_json" 2>/dev/null || true)"
  [[ -n "$payload" ]] || return 1
  _hook_runtime_apply_exports "$payload"
}

# --- Core init function ---
# Reads stdin, parses common fields via Rust binary, sets paths.
hook_init() {
  # If dispatcher already parsed input, skip re-parsing
  if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
    return 0
  fi

  # Read stdin once
  INPUT="$(cat)"
  INPUT="${INPUT:-{\}}"

  local payload
  payload="$(hook_rust_runtime_invoke init <<< "$INPUT" 2>/dev/null)"
  if [[ -n "$payload" ]]; then
    _hook_runtime_apply_exports "$payload"
    return 0
  fi
  
  echo "HOOK_INIT: Rust runtime failed and fallbacks are disabled" >&2
  return 1
}

# --- Content extraction for Write/Edit hooks ---
hook_extract_content() {
  # Not strictly needed if hook_init_full is used, but for compatibility:
  hook_rust_runtime_invoke extract-content <<< "$INPUT" 2>/dev/null
}

# --- Combined init + content extraction ---
hook_init_full() {
  # If dispatcher already parsed input, skip re-parsing
  if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
    return 0
  fi

  # Read stdin once
  INPUT="$(cat)"
  INPUT="${INPUT:-{\}}"

  local payload
  payload="$(hook_rust_runtime_invoke init <<< "$INPUT" 2>/dev/null)"
  if [[ -n "$payload" ]]; then
    _hook_runtime_apply_exports "$payload"
    return 0
  fi

  echo "HOOK_INIT_FULL: Rust runtime failed and fallbacks are disabled" >&2
  return 1
}

# --- Tool availability cache ---
declare -A _TOOL_CACHE 2>/dev/null || true
_QA_STATE_TOOLS_LOADED=false

# Pre-load all tool states from qa-state.json (once).
_load_qa_state_tools() {
  if [[ "$_QA_STATE_TOOLS_LOADED" == "true" ]]; then
    return
  fi
  _QA_STATE_TOOLS_LOADED=true
  if [[ -f "${QA_STATE:-}" ]]; then
    local _tool_name _tool_val
    while IFS=$'\t' read -r _tool_name _tool_val; do
      [[ -z "$_tool_name" ]] && continue
      _TOOL_CACHE[$_tool_name]="$_tool_val"
    done < <(jq -r '.tools // {} | to_entries[] | "\(.key)\t\(.value)"' "$QA_STATE" 2>/dev/null || true)
  fi
}

tool_available() {
  local tool="$1"
  # Check cache first
  if [[ -n "${_TOOL_CACHE[$tool]+x}" ]]; then
    echo "${_TOOL_CACHE[$tool]}"
    return
  fi
  # Lazy-load all tools from qa-state.json on first cache miss
  _load_qa_state_tools
  if [[ -n "${_TOOL_CACHE[$tool]+x}" ]]; then
    echo "${_TOOL_CACHE[$tool]}"
    return
  fi
  
  # Use Rust runtime for robust existence check
  local result
  result=$(hook_rust_runtime_invoke pkg exists "$tool" 2>/dev/null)
  if [[ "$result" != "true" && "$result" != "false" ]]; then
    # Fallback to command -v if Rust call fails
    if command -v "$tool" >/dev/null 2>&1; then
      result="true"
    else
      result="false"
    fi
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
  timeout "$secs" "$@" 2>&1 || true
}

# Get changed files list (one per line) from Rust.
get_changed_files() {
  hook_rust_runtime_invoke changed-files 2>/dev/null | jq -r '.[]' 2>/dev/null
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
  _qparsed="$(jq -r '[
    (.governance.delivery_model // "auto"),
    (.criticality_tier // "established"),
    (.governance // {} | tojson)
  ] | @tsv' "$qfile" 2>/dev/null || echo "auto	established	{}")"
  IFS=$'\t' read -r DELIVERY_MODEL CRITICALITY_TIER GOVERNANCE_CONFIG <<< "$_qparsed"
  export DELIVERY_MODEL CRITICALITY_TIER GOVERNANCE_CONFIG
}

# --- Report writing helpers ---
# Rust-based report generation.

# Write a simple pass report
write_pass_report() {
  hook_rust_runtime_invoke report-pass "$@" 2>/dev/null
}

# Write a not_applicable report (for stub gates)
write_na_report() {
  hook_rust_runtime_invoke report-na "$@" 2>/dev/null
}

# Write a failure report
write_fail_report() {
  hook_rust_runtime_invoke report-fail "$@" 2>/dev/null
}

# --- Feedback & Nudging ---
# Rust-based feedback helpers.
emit_feedback() {
  hook_rust_runtime_invoke feedback "$@" 2>/dev/null
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

# String extraction helpers (Rust-based)
file_ext() { hook_rust_runtime_invoke file-ext "$1" 2>/dev/null; }
file_basename() { hook_rust_runtime_invoke file-basename "$1" 2>/dev/null; }

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
    if [[ -n "${_GIT_HEAD_SHA:-}" ]]; then
      head_sha="$_GIT_HEAD_SHA"
    else
      head_sha="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}"
    fi
    changed_files="${CHANGED_FILES_SORTED:-$(git diff --name-only HEAD 2>/dev/null | sort)}"

    hook_rust_runtime_invoke cache-key "$hook_name" "$head_sha" "$changed_files" 2>/dev/null
}

# Check if cached result exists and is fresh (within TTL seconds)
hook_cache_check() {
    local key="$1" ttl="${2:-60}"
    hook_rust_runtime_invoke cache-check "$key" "$ttl" >/dev/null 2>&1
}

# Read cached result (stdout + exit code)
hook_cache_read() {
    local key="$1"
    hook_rust_runtime_invoke cache-read "$key" 2>/dev/null
}

# Write result to cache
hook_cache_write() {
    local key="$1" rc="$2" output="$3"
    hook_rust_runtime_invoke cache-write "$key" "$rc" "$output" >/dev/null 2>&1
}

# --- 2. Cross-Hook Shared Results (Changed Files Index) ---
# Build the changed files list ONCE and share across all Stop hooks.

HOOK_SHARED_DIR="${HOOK_CACHE_DIR}/shared"

# Get or build the shared changed files list
hook_shared_changed_files() {
    hook_rust_runtime_invoke changed-files 2>/dev/null
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
    hook_rust_runtime_invoke breaker-check "$tool" >/dev/null 2>&1
}

# Record a tool failure
hook_breaker_record_failure() {
    local tool="$1"
    hook_rust_runtime_invoke breaker-record "$tool" >/dev/null 2>&1
}

# Reset breaker on success
hook_breaker_reset() {
    local tool="$1"
    hook_rust_runtime_invoke breaker-reset "$tool" >/dev/null 2>&1
}

# --- 4. Debounce Helper for PostToolUse Hooks ---
# Allows PostToolUse hooks to batch rapid-fire edits. The first caller becomes
# the "leader" and waits for the debounce window; followers skip immediately.

HOOK_DEBOUNCE_DIR="${HOOK_CACHE_DIR}/debounce"

# Record a file for debounced processing. Returns 0 if this call should proceed
# (i.e., it's the leader after the debounce window), 1 if it should skip (follower).
hook_debounce_file() {
    local hook_name="$1" file="$2" window_ms="${3:-200}"
    hook_rust_runtime_invoke debounce "$hook_name" "$file" "$window_ms" 2>/dev/null
}

# --- 5. Incremental Validation for PreToolUse ---
# Track what files a hook inspected via SHA-256 manifests. Skip re-validation
# when all inputs are unchanged since the last run.

HOOK_MANIFEST_DIR="${HOOK_CACHE_DIR}/manifests"

# Check if hook inputs are unchanged since last run
hook_incremental_check() {
    local hook_name="$1"; shift
    local files=("$@")
    hook_rust_runtime_invoke incremental-check "$hook_name" "${files[@]}" >/dev/null 2>&1
}

# Record current input state
hook_incremental_record() {
    local hook_name="$1"; shift
    local files=("$@")
    hook_rust_runtime_invoke incremental-record "$hook_name" "${files[@]}" >/dev/null 2>&1
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
    hook_rust_runtime_invoke file-hash "$@" 2>/dev/null
}

# --- 8. Shared FR IDs ---
# Parse FR IDs from FUNCTIONAL_REQUIREMENTS.md once, share across hooks.
hook_shared_fr_ids() {
    hook_rust_runtime_invoke fr-ids 2>/dev/null
}

# --- 9. Shared FR Index (file:FR pairs) ---
# Pre-build index of all FR references across test directories.
# Format: filepath:FR-XXX-NNN (one per line), same as grep -rHoE output.
# Used by spec-verifier.sh to skip expensive recursive grep.
hook_shared_fr_index() {
    hook_rust_runtime_invoke fr-index 2>/dev/null
}

# ============================================================================
# Hook Config Reader
# ============================================================================
hook_config_get() {
  hook_rust_runtime_invoke config-get "$1" 2>/dev/null
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
hook_should_run() {
    local hook_name="${1:-unknown}" pattern="${2:-}"
    local changed_files
    
    # Get changed files from Rust runtime (JSON format)
    changed_files="$(hook_rust_runtime_invoke changed-files 2>/dev/null)"
    
    # If no changes detected or error, run hook for safety
    [[ -z "$changed_files" || "$changed_files" == "[]" ]] && return 0
    
    # If no pattern specified, run for any change
    [[ -z "$pattern" ]] && return 0
    
    # Check if any changed file matches the pattern
    # Extract strings from JSON array and grep
    echo "$changed_files" | tr -d '[]"' | tr ',' '\n' | grep -qE "$pattern"
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

# Get affected tests from Rust.
get_affected_tests() {
  hook_rust_runtime_invoke affected-tests "$@" 2>/dev/null
}

# ============================================================================
# Pre-warm Cache Functions
# ============================================================================
# Warm caches at session start for faster subsequent hooks.

# Run all pre-warms in parallel (non-blocking)
hook_prewarm_all() {
    hook_rust_runtime_invoke prewarm "${PROJECT_DIR:-.}" >/dev/null 2>&1 &
}

# ============================================================================
# Progress Output for Long-Running Hooks
# ============================================================================
# Print periodic progress to prevent idle timeout.

# Print progress message with timestamp
hook_progress() {
    hook_rust_runtime_invoke progress "$@" >/dev/null 2>&1
}

# Start background progress reporter
hook_progress_start() {
    local msg="${1:-Working...}" interval="${2:-30}"
    (
        while true; do
            sleep "$interval"
            echo "PROGRESS: $msg" >&2
        done
    ) &
    echo $!
}

# Stop background progress reporter
hook_progress_stop() {
    local pid="$1"
    if [[ -n "$pid" ]]; then
        kill "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    fi
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
  hook_rust_runtime_invoke learning-record "$hook_name" "$pattern" "$passed" >/dev/null 2>&1
}

# Check if hook should be skipped based on learning (consistently passes for this pattern)
# Returns 0 if should skip, 1 if should run
hook_learning_should_skip() {
  local hook_name="$1" pattern="$2"
  hook_rust_runtime_invoke learning-should-skip "$hook_name" "$pattern" >/dev/null 2>&1
}

# Migration complete: Rust runtime enabled by default.
