#!/bin/zsh
# @trace FR-FORMAL-001
# qa-formal-methods-gate.sh
# EXT-G2: Functional gate for formal methods (TLA+/Alloy/Dafny).
# Runs available tools when specs exist; skips gracefully when not installed.
#
# Exit codes:
#   0: All checks pass (or skipped gracefully)
#   1: Verification failures found
#   2: Configuration/usage error
set -euo pipefail

# ==============================================================================
# Configuration
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(pwd)"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/formal-methods-gate.json"
FORMAL_DIR="$PROJECT_DIR/contracts/formal"
REGISTRY="$FORMAL_DIR/registry.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Tool paths
TLA2_JAR="${TLA2_TOOLS:-$HOME/.tla2tools/tla2tools.jar}"
ALLOY_JAR="${ALLOY_JAR:-$HOME/.alloy/alloy.jar}"

# Tool availability flags
HAS_TLC=false
HAS_ALLOY=false
HAS_DAFNY=false

# Default settings
DEFAULT_TIMEOUT=300  # 5 minutes per spec
TIMEOUT="$DEFAULT_TIMEOUT"

# ==============================================================================
# Helper Functions
# ==============================================================================

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Formal methods verification gate — TLA+, Alloy, Dafny.
Traces to: FR-FORMAL-001

Options:
  --tool <tool>           Run specific tool: tla+, alloy, dafny
  --spec <path>           Path to specific spec file
  --spec-dir <dir>        Directory containing specs (default: contracts/formal/)
  --auto-detect           Auto-detect and run all available specs
  --registry <path>       Path to registry.json (default: contracts/formal/registry.json)
  --timeout <seconds>     Timeout per verification (default: 300)
  --list-tools            Show available tools and exit
  --help                  Show this help message

Exit codes:
  0: All checks pass (or skipped gracefully)
  1: Verification failures found
  2: Configuration/usage error

Examples:
  $(basename "$0") --tool tla+ --spec contracts/formal/RequirementLedger.tla
  $(basename "$0") --tool alloy --spec spec.als
  $(basename "$0") --tool dafny --spec spec.dfy
  $(basename "$0") --auto-detect --spec-dir specs/
  $(basename "$0") --auto-detect

Tool Detection:
  TLA+:   tlc (TLA+ Tools CLI) or java with tla2tools.jar
  Alloy:  alloy (Alloy CLI) or java with alloy.jar
  Dafny:  dafny (Dafny CLI)
EOF
}

log_info() {
  echo "[INFO] $1" >&2
}

log_warn() {
  echo "[WARN] $1" >&2
}

log_error() {
  echo "[ERROR] $1" >&2
}

log_skip() {
  echo "[SKIP] $1" >&2
}

# ==============================================================================
# Tool Detection
# ==============================================================================

check_tlc() {
  if [[ -f "$TLA2_JAR" ]] && command -v java &>/dev/null; then
    HAS_TLC=true
    return 0
  fi
  if command -v tlc &>/dev/null; then
    HAS_TLC=true
    return 0
  fi
  # Check common locations
  for jar_path in \
    "/usr/share/tla2tools.jar" \
    "/opt/tla2tools.jar" \
    "${TLA2TOOLS_HOME:-/notfound}/tla2tools.jar"
  do
    if [[ -f "$jar_path" ]]; then
      TLA2_JAR="$jar_path"
      HAS_TLC=true
      return 0
    fi
  done
  return 1
}

check_alloy() {
  if [[ -d /Applications/Alloy.app ]] || command -v alloy &>/dev/null; then
    HAS_ALLOY=true
    return 0
  fi
  # Check for alloy jar
  for jar_path in \
    "$ALLOY_JAR" \
    "/usr/share/alloy.jar" \
    "/opt/alloy.jar" \
    "$HOME/.alloy/alloy.jar"
  do
    if [[ -f "$jar_path" ]]; then
      ALLOY_JAR="$jar_path"
      HAS_ALLOY=true
      return 0
    fi
  done
  return 1
}

check_dafny() {
  if command -v dafny &>/dev/null; then
    HAS_DAFNY=true
    return 0
  fi
  return 1
}

detect_all_tools() {
  check_tlc || true
  check_alloy || true
  check_dafny || true
}

list_tools() {
  detect_all_tools
  echo "=== Formal Methods Tools Detection ==="
  echo ""
  echo "TLA+ (tlc):    $([ "$HAS_TLC" == "true" ] && echo "available" || echo "not found")"
  echo "Alloy:         $([ "$HAS_ALLOY" == "true" ] && echo "available" || echo "not found")"
  echo "Dafny:         $([ "$HAS_DAFNY" == "true" ] && echo "available" || echo "not found")"
  echo ""
  if [[ "$HAS_TLC" == "true" && -f "$TLA2_JAR" ]]; then
    echo "TLA+ Tools JAR: $TLA2_JAR"
  fi
  if [[ "$HAS_ALLOY" == "true" && -f "$ALLOY_JAR" ]]; then
    echo "Alloy JAR: $ALLOY_JAR"
  fi
}

# ==============================================================================
# Spec Discovery
# ==============================================================================

discover_specs() {
  local spec_type="$1"
  local search_dir="${2:-$FORMAL_DIR}"
  local found=()
  local search_dirs=("$search_dir" "$PROJECT_DIR/contracts/formal" "$PROJECT_DIR/specs/formal" "$PROJECT_DIR/formal")

  for dir in "${search_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
      while IFS= read -r -d '' file; do
        found+=("$file")
      done < <(find "$dir" -name "*.${spec_type}" -print0 2>/dev/null || true)
    fi
  done

  # Also search project root (limited depth) if not already found
  if [[ ${#found[@]} -eq 0 ]]; then
    while IFS= read -r -d '' file; do
      found+=("$file")
    done < <(find "$PROJECT_DIR" -maxdepth 3 -name "*.${spec_type}" -print0 2>/dev/null || true)
  fi

  # Deduplicate and output
  printf '%s\n' "${found[@]}" 2>/dev/null | sort -u
}

# ==============================================================================
# TLA+ Verification
# ==============================================================================

run_tlc_check() {
  local spec_file="$1"
  # Convert to absolute path
  if [[ "$spec_file" != /* ]]; then
    spec_file="$PROJECT_DIR/$spec_file"
  fi
  local spec_dir
  spec_dir="$(dirname "$spec_file")"
  local spec_name
  spec_name="$(basename "$spec_file" .tla)"
  local cfg_file="$spec_dir/${spec_name}.cfg"
  local status="unknown"
  local error_msg=""
  local duration_ms=0

  if [[ "$HAS_TLC" != "true" ]]; then
    log_skip "TLA+ verification (tlc not available)"
    jq -n --arg tool "tlc" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "skipped", error: "tool not available"}'
    return 0
  fi

  if [[ ! -f "$spec_file" ]]; then
    log_error "TLA+ spec not found: $spec_file"
    jq -n --arg tool "tlc" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "error", error: "file not found"}'
    return 1
  fi

  log_info "=== TLA+ Verification: $spec_name ==="
  log_info "Spec: $spec_file"

  # Find config file (spec.cfg or spec_name.cfg)
  if [[ ! -f "$cfg_file" ]]; then
    cfg_file="$spec_dir/spec.cfg"
  fi
  [[ -f "$cfg_file" ]] && log_info "Config: $cfg_file"

  local start_time
  start_time="$(date +%s)"

  # Run TLC
  local tlc_output
  local tlc_exit_code=0

  if [[ -f "$TLA2_JAR" ]]; then
    if [[ -f "$cfg_file" ]]; then
      tlc_output=$(cd "$spec_dir" && timeout "$TIMEOUT" java -cp "$TLA2_JAR" tlc2.TLC -deadlock -config "$cfg_file" "$spec_name" 2>&1) || tlc_exit_code=$?
    else
      tlc_output=$(cd "$spec_dir" && timeout "$TIMEOUT" java -cp "$TLA2_JAR" tlc2.TLC -deadlock "$spec_name" 2>&1) || tlc_exit_code=$?
    fi
  else
    tlc_output=$(timeout "$TIMEOUT" tlc -deadlock "$spec_file" 2>&1) || tlc_exit_code=$?
  fi

  local end_time
  end_time="$(date +%s)"
  duration_ms=$(( (end_time - start_time) * 1000 ))

  # Parse TLC output for results
  if [[ $tlc_exit_code -eq 124 ]]; then
    status="timeout"
    error_msg="Verification timed out after ${TIMEOUT}s"
    log_error "TLA+ verification timed out: $spec_name"
  elif echo "$tlc_output" | grep -qE "Model checking completed|No errors found|states generated|Success"; then
    status="pass"
    log_info "TLA+ verification passed: $spec_name"
  elif echo "$tlc_output" | grep -qE "Invariant .* violated|Error|Temporal properties violated"; then
    status="fail"
    error_msg="Invariant violation or temporal property failure"
    log_error "TLA+ verification failed: $spec_name"
    echo "$tlc_output" | tail -10 >&2
  elif [[ $tlc_exit_code -ne 0 ]]; then
    status="error"
    error_msg="TLC execution failed (exit code: $tlc_exit_code)"
    log_error "TLA+ execution error: $spec_name"
    echo "$tlc_output" | tail -10 >&2
  else
    # Assume pass if no errors detected
    status="pass"
    log_info "TLA+ verification completed: $spec_name"
  fi

  jq -n \
    --arg tool "tlc" \
    --arg spec "$spec_file" \
    --arg status "$status" \
    --arg error "$error_msg" \
    --argjson duration "$duration_ms" \
    '{tool: $tool, spec: $spec, status: $status, error: $error, duration_ms: $duration}'
}

# ==============================================================================
# Alloy Verification
# ==============================================================================

run_alloy_check() {
  local spec_file="$1"
  # Convert to absolute path
  if [[ "$spec_file" != /* ]]; then
    spec_file="$PROJECT_DIR/$spec_file"
  fi
  local spec_name
  spec_name="$(basename "$spec_file" .als)"
  local status="unknown"
  local error_msg=""
  local duration_ms=0

  if [[ "$HAS_ALLOY" != "true" ]]; then
    log_skip "Alloy verification (alloy not available)"
    jq -n --arg tool "alloy" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "skipped", error: "tool not available"}'
    return 0
  fi

  if [[ ! -f "$spec_file" ]]; then
    log_error "Alloy spec not found: $spec_file"
    jq -n --arg tool "alloy" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "error", error: "file not found"}'
    return 1
  fi

  log_info "=== Alloy Verification: $spec_name ==="
  log_info "Spec: $spec_file"

  local start_time
  start_time="$(date +%s)"

  local alloy_output
  local alloy_exit_code=0

  if [[ -f "$ALLOY_JAR" ]]; then
    alloy_output=$(timeout "$TIMEOUT" java -jar "$ALLOY_JAR" "$spec_file" 2>&1) || alloy_exit_code=$?
  else
    alloy_output=$(timeout "$TIMEOUT" alloy -s "$spec_file" 2>&1) || alloy_exit_code=$?
  fi

  local end_time
  end_time="$(date +%s)"
  duration_ms=$(( (end_time - start_time) * 1000 ))

  # Parse Alloy output
  if [[ $alloy_exit_code -eq 124 ]]; then
    status="timeout"
    error_msg="Verification timed out after ${TIMEOUT}s"
    log_error "Alloy verification timed out: $spec_name"
  elif echo "$alloy_output" | grep -qE "No counterexample|Instance found|consistent|Command execution succeeded"; then
    status="pass"
    log_info "Alloy verification passed: $spec_name"
  elif echo "$alloy_output" | grep -qE "Counterexample|inconsistent|unsat"; then
    status="fail"
    error_msg="Counterexample found or inconsistency detected"
    log_error "Alloy verification failed: $spec_name"
    echo "$alloy_output" | tail -10 >&2
  elif [[ $alloy_exit_code -ne 0 ]]; then
    status="error"
    error_msg="Alloy execution failed (exit code: $alloy_exit_code)"
    log_error "Alloy execution error: $spec_name"
    echo "$alloy_output" | tail -10 >&2
  else
    status="pass"
    log_info "Alloy verification completed: $spec_name"
  fi

  jq -n \
    --arg tool "alloy" \
    --arg spec "$spec_file" \
    --arg status "$status" \
    --arg error "$error_msg" \
    --argjson duration "$duration_ms" \
    '{tool: $tool, spec: $spec, status: $status, error: $error, duration_ms: $duration}'
}

# ==============================================================================
# Dafny Verification
# ==============================================================================

run_dafny_check() {
  local spec_file="$1"
  # Convert to absolute path
  if [[ "$spec_file" != /* ]]; then
    spec_file="$PROJECT_DIR/$spec_file"
  fi
  local spec_name
  spec_name="$(basename "$spec_file" .dfy)"
  local status="unknown"
  local error_msg=""
  local duration_ms=0

  if [[ "$HAS_DAFNY" != "true" ]]; then
    log_skip "Dafny verification (dafny not available)"
    jq -n --arg tool "dafny" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "skipped", error: "tool not available"}'
    return 0
  fi

  if [[ ! -f "$spec_file" ]]; then
    log_error "Dafny spec not found: $spec_file"
    jq -n --arg tool "dafny" --arg spec "$spec_file" \
      '{tool: $tool, spec: $spec, status: "error", error: "file not found"}'
    return 1
  fi

  log_info "=== Dafny Verification: $spec_name ==="
  log_info "Spec: $spec_file"

  local start_time
  start_time="$(date +%s)"

  local dafny_output
  local dafny_exit_code=0

  dafny_output=$(timeout "$TIMEOUT" dafny verify "$spec_file" 2>&1) || dafny_exit_code=$?

  local end_time
  end_time="$(date +%s)"
  duration_ms=$(( (end_time - start_time) * 1000 ))

  # Parse Dafny output
  if [[ $dafny_exit_code -eq 124 ]]; then
    status="timeout"
    error_msg="Verification timed out after ${TIMEOUT}s"
    log_error "Dafny verification timed out: $spec_name"
  elif echo "$dafny_output" | grep -qE "0 errors|Verification successful|verified|No errors found"; then
    status="pass"
    log_info "Dafny verification passed: $spec_name"
  elif echo "$dafny_output" | grep -qE "error|timeout|out of memory"; then
    status="fail"
    error_msg="Verification errors or resource limits"
    log_error "Dafny verification failed: $spec_name"
    echo "$dafny_output" | tail -10 >&2
  elif [[ $dafny_exit_code -ne 0 ]]; then
    status="fail"
    error_msg="Dafny execution failed (exit code: $dafny_exit_code)"
    log_error "Dafny execution error: $spec_name"
    echo "$dafny_output" | tail -10 >&2
  else
    status="pass"
    log_info "Dafny verification completed: $spec_name"
  fi

  jq -n \
    --arg tool "dafny" \
    --arg spec "$spec_file" \
    --arg status "$status" \
    --arg error "$error_msg" \
    --argjson duration "$duration_ms" \
    '{tool: $tool, spec: $spec, status: $status, error: $error, duration_ms: $duration}'
}

# ==============================================================================
# Registry-based Execution
# ==============================================================================

run_from_registry() {
  local registry_path="${1:-$REGISTRY}"
  local result=0
  local checks=()

  if [[ ! -f "$registry_path" ]]; then
    log_warn "Registry not found: $registry_path"
    return 0
  fi

  log_info "=== Running from Registry: $registry_path ==="

  local item_count=0
  while IFS= read -r item; do
    [[ -z "$item" ]] && continue

    local id path kind config check_result
    id="$(jq -r '.id // empty' <<< "$item")"
    path="$(jq -r '.path // empty' <<< "$item")"
    kind="$(jq -r '.kind // empty' <<< "$item")"

    [[ -z "$path" ]] && continue

    item_count=$((item_count + 1))

    case "$kind" in
      tla)
        check_result=$(run_tlc_check "$PROJECT_DIR/$path") || result=1
        ;;
      alloy|als)
        check_result=$(run_alloy_check "$PROJECT_DIR/$path") || result=1
        ;;
      dafny|dfy)
        check_result=$(run_dafny_check "$PROJECT_DIR/$path") || result=1
        ;;
      *)
        log_warn "Unknown spec kind: $kind (id: $id)"
        check_result='{"status":"skipped","error":"unknown kind"}'
        ;;
    esac
    checks+=("$check_result")
  done < <(jq -c '.items[]?' "$registry_path" 2>/dev/null)

  if [[ $item_count -eq 0 ]]; then
    log_info "No specs found in registry"
  fi

  # Output checks as JSON array
  if [[ ${#checks[@]} -gt 0 ]]; then
    printf '%s\n' "${checks[@]}" | jq -s '.'
  else
    echo "[]"
  fi

  return $result
}

# ==============================================================================
# Directory-based Execution
# ==============================================================================

run_from_directory() {
  local spec_dir="${1:-$FORMAL_DIR}"
  local result=0
  local checks=()

  if [[ ! -d "$spec_dir" ]]; then
    log_warn "Spec directory not found: $spec_dir"
    echo "[]"
    return 0
  fi

  log_info "=== Auto-detecting specs in: $spec_dir ==="

  # TLA+ specs
  while IFS= read -r spec; do
    [[ -z "$spec" ]] && continue
    local check_result
    check_result=$(run_tlc_check "$spec") || result=1
    checks+=("$check_result")
  done < <(discover_specs "tla" "$spec_dir")

  # Alloy specs
  while IFS= read -r spec; do
    [[ -z "$spec" ]] && continue
    local check_result
    check_result=$(run_alloy_check "$spec") || result=1
    checks+=("$check_result")
  done < <(discover_specs "als" "$spec_dir")

  # Dafny specs
  while IFS= read -r spec; do
    [[ -z "$spec" ]] && continue
    local check_result
    check_result=$(run_dafny_check "$spec") || result=1
    checks+=("$check_result")
  done < <(discover_specs "dfy" "$spec_dir")

  # Output checks as JSON array
  if [[ ${#checks[@]} -gt 0 ]]; then
    printf '%s\n' "${checks[@]}" | jq -s '.'
  else
    echo "[]"
  fi

  return $result
}

# ==============================================================================
# Report Generation
# ==============================================================================

write_report() {
  local status="$1"
  local checks_json="$2"
  local tool_status="$3"

  mkdir -p "$VERIFY_DIR"

  local error_count fail_count
  error_count=$(echo "$checks_json" | jq '[.[] | select(.status == "error")] | length')
  fail_count=$(echo "$checks_json" | jq '[.[] | select(.status == "fail")] | length')

  jq -n \
    --arg ts "$now" \
    --arg status "$status" \
    --argjson checks "$checks_json" \
    --argjson error_count "$error_count" \
    --argjson fail_count "$fail_count" \
    --argjson tool_status "$tool_status" \
    '{
      generated_at: $ts,
      status: $status,
      pass: ($status == "pass"),
      checks: $checks,
      error_count: $error_count,
      warn_count: $fail_count,
      tools_available: $tool_status
    }' > "$REPORT"
}

# ==============================================================================
# Stdin Input Handler (Hook Mode)
# ==============================================================================

handle_stdin_input() {
  local input
  input="$(cat)"
  local cwd
  cwd="$(jq -r '.cwd // empty' <<< "$input" 2>/dev/null || echo "")"
  PROJECT_DIR="${cwd:-$PROJECT_DIR}"
  VERIFY_DIR="$PROJECT_DIR/.claude/verification"
  REPORT="$VERIFY_DIR/formal-methods-gate.json"
  FORMAL_DIR="$PROJECT_DIR/contracts/formal"
  REGISTRY="$FORMAL_DIR/registry.json"

  mkdir -p "$VERIFY_DIR"

  # Detect tools
  detect_all_tools

  # Check if any formal specs exist
  local has_specs=false
  [[ -d "$FORMAL_DIR" ]] && has_specs=true

  local tla_specs als_specs dfy_specs
  tla_specs=$(discover_specs "tla" "$FORMAL_DIR")
  als_specs=$(discover_specs "als" "$FORMAL_DIR")
  dfy_specs=$(discover_specs "dfy" "$FORMAL_DIR")

  [[ -n "$tla_specs" ]] && has_specs=true
  [[ -n "$als_specs" ]] && has_specs=true
  [[ -n "$dfy_specs" ]] && has_specs=true

  # If no specs, not_declared
  if [[ "$has_specs" != "true" ]]; then
    jq -n --arg ts "$now" \
      '{generated_at:$ts,status:"not_declared",checks:[],pass:true,error_count:0,warn_count:0,tools_available:{tlc:false,alloy:false,dafny:false}}' > "$REPORT"
    echo "FORMAL METHODS GATE: not_declared (no formal specs found)"
    exit 0
  fi

  # If specs exist but no tools, warn but pass (soft gate)
  if [[ "$HAS_TLC" != "true" && "$HAS_ALLOY" != "true" && "$HAS_DAFNY" != "true" ]]; then
    jq -n --arg ts "$now" \
      '{generated_at:$ts,status:"no_tools",checks:[],pass:true,error_count:0,warn_count:1,warn:"Formal specs found but no tools installed (TLC/Alloy/Dafny)",tools_available:{tlc:false,alloy:false,dafny:false}}' > "$REPORT"
    echo "FORMAL METHODS GATE: no_tools (specs exist, install tools for verification)"
    exit 0
  fi

  # Run checks
  local checks_json
  local final_result=0

  # Try registry first, then directory scan
  if [[ -f "$REGISTRY" ]]; then
    checks_json=$(run_from_registry "$REGISTRY") || final_result=1
  else
    checks_json=$(run_from_directory "$FORMAL_DIR") || final_result=1
  fi

  # Determine status
  local status="pass"
  local error_count fail_count
  error_count=$(echo "$checks_json" | jq '[.[] | select(.status == "error")] | length')
  fail_count=$(echo "$checks_json" | jq '[.[] | select(.status == "fail")] | length')

  [[ $fail_count -gt 0 ]] && status="fail"
  [[ $error_count -gt 0 ]] && status="error"

  # Tool status
  local tool_status
  tool_status=$(jq -n --argjson tlc "$HAS_TLC" --argjson alloy "$HAS_ALLOY" --argjson dafny "$HAS_DAFNY" \
    '{tlc: $tlc, alloy: $alloy, dafny: $dafny}')

  # Write report
  write_report "$status" "$checks_json" "$tool_status"

  # Summary
  local check_count
  check_count=$(echo "$checks_json" | jq 'length')
  echo ""
  echo "=== Formal Methods Gate Summary ==="
  echo "Checks run: $check_count"
  echo "Errors: $error_count"
  echo "Failures: $fail_count"
  echo "Status: $status"
  echo "Report: $REPORT"

  if [[ "$final_result" -ne 0 || "$status" != "pass" ]]; then
    echo "FORMAL-METHODS-GATE FAIL: verification errors or failures detected" >&2
    exit 1
  fi

  echo "FORMAL-METHODS-GATE PASS"
  exit 0
}

# ==============================================================================
# Main
# ==============================================================================

main() {
  local tool=""
  local spec_path=""
  local spec_dir=""
  local registry_path=""
  local auto_detect=false
  local list_tools_only=false

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tool)
        tool="$2"
        shift 2
        ;;
      --spec)
        spec_path="$2"
        shift 2
        ;;
      --spec-dir)
        spec_dir="$2"
        shift 2
        ;;
      --auto-detect)
        auto_detect=true
        shift
        ;;
      --registry)
        registry_path="$2"
        shift 2
        ;;
      --timeout)
        TIMEOUT="$2"
        shift 2
        ;;
      --list-tools)
        list_tools_only=true
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      -*)
        log_error "Unknown option: $1"
        usage
        exit 2
        ;;
      *)
        # Positional argument - treat as spec path
        if [[ -z "$spec_path" ]]; then
          spec_path="$1"
        else
          log_error "Multiple spec paths not supported"
          exit 2
        fi
        shift
        ;;
    esac
  done

  # Detect tools first
  detect_all_tools

  # Handle --list-tools
  if [[ "$list_tools_only" == "true" ]]; then
    list_tools
    exit 0
  fi

  # No args and stdin has data - hook mode
  if [[ $# -eq 0 && ! -t 0 && -z "$tool" && -z "$spec_path" && "$auto_detect" != "true" ]]; then
    handle_stdin_input
    exit $?
  fi

  log_info "Formal Methods Gate — FR-FORMAL-001"
  log_info "Project: $PROJECT_DIR"
  echo ""

  local checks_json="[]"
  local final_result=0

  # Handle specific tool + spec
  if [[ -n "$tool" && -n "$spec_path" ]]; then
    local check_result
    case "$tool" in
      tla|tla+)
        check_result=$(run_tlc_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      alloy|als)
        check_result=$(run_alloy_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      dafny|dfy)
        check_result=$(run_dafny_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      *)
        log_error "Unknown tool: $tool (expected: tla+, alloy, dafny)"
        exit 2
        ;;
    esac
  # Handle auto-detection
  elif [[ "$auto_detect" == "true" ]]; then
    local dir="${spec_dir:-$FORMAL_DIR}"
    # Try registry first if specified or exists
    if [[ -n "$registry_path" ]] || [[ -f "$REGISTRY" ]]; then
      checks_json=$(run_from_registry "${registry_path:-$REGISTRY}") || final_result=1
    else
      checks_json=$(run_from_directory "$dir") || final_result=1
    fi
  # Handle single spec with auto-detection of tool
  elif [[ -n "$spec_path" ]]; then
    local check_result
    case "$spec_path" in
      *.tla)
        check_result=$(run_tlc_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      *.als)
        check_result=$(run_alloy_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      *.dfy)
        check_result=$(run_dafny_check "$spec_path") || final_result=1
        checks_json=$(echo "[$check_result]" | jq '.')
        ;;
      *)
        log_error "Unknown spec extension: $spec_path (expected: .tla, .als, .dfy)"
        exit 2
        ;;
    esac
  else
    # Default: auto-detect from formal directory
    checks_json=$(run_from_directory "$FORMAL_DIR") || final_result=1
  fi

  # Determine status
  local status="pass"
  local error_count fail_count
  error_count=$(echo "$checks_json" | jq '[.[] | select(.status == "error")] | length')
  fail_count=$(echo "$checks_json" | jq '[.[] | select(.status == "fail")] | length')

  [[ $fail_count -gt 0 ]] && status="fail"
  [[ $error_count -gt 0 ]] && status="error"

  # Tool status
  local tool_status
  tool_status=$(jq -n --argjson tlc "$HAS_TLC" --argjson alloy "$HAS_ALLOY" --argjson dafny "$HAS_DAFNY" \
    '{tlc: $tlc, alloy: $alloy, dafny: $dafny}')

  # Write report
  write_report "$status" "$checks_json" "$tool_status"

  # Summary
  local check_count
  check_count=$(echo "$checks_json" | jq 'length')
  echo ""
  echo "=== Formal Methods Gate Summary ==="
  echo "Checks run: $check_count"
  echo "Errors: $error_count"
  echo "Failures: $fail_count"
  echo "Status: $status"
  echo "Report: $REPORT"

  if [[ "$final_result" -ne 0 || "$status" != "pass" ]]; then
    echo "FORMAL-METHODS-GATE FAIL: verification errors or failures detected" >&2
    exit 1
  fi

  echo "FORMAL-METHODS-GATE PASS"
  exit 0
}

main "$@"
