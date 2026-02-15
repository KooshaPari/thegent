#!/usr/bin/env bash
# qa-onchain-contract-gate.sh
# N4: Onchain contract gate - functional when Forge/Foundry is installed.
# When forge available: runs forge test, forge build, cast checks.
# When forge not available: emits advisory message and exits 0 (non-blocking).
set -euo pipefail

# ==============================================================================
# Configuration
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Environment / config defaults
RPC_URL="${RPC_URL:-}"
CHAIN_ID="${CHAIN_ID:-}"
FORGE_PATH="${FORGE_PATH:-forge}"
CAST_PATH="${CAST_PATH:-cast}"

# ==============================================================================
# Argument Parsing
# ==============================================================================
ACTION=""
ADDRESS=""
TX_HASH=""
CONTRACT_NAME=""
PROJECT_DIR=""

usage() {
  cat <<EOF
Usage: qa-onchain-contract-gate.sh [OPTIONS] <ACTION>

Actions:
  --check-deployment --address ADDR    Check if contract is deployed at address
  --validate-tx --tx-hash HASH         Validate transaction receipt
  --verify-contract --address ADDR --contract NAME
                                       Verify contract on block explorer
  --run-tests                          Run forge test suite
  --full-check                         Run all available checks (build + test)
  --gate                               Run as governance gate (reads stdin JSON)

Options:
  --project-dir DIR                    Project directory (default: current)
  --address ADDR                       Contract address
  --tx-hash HASH                       Transaction hash
  --contract NAME                      Contract name for verification
  --rpc-url URL                        RPC endpoint (or RPC_URL env)
  --chain-id ID                        Chain ID (or CHAIN_ID env)
  --forge-path PATH                    Path to forge binary (default: forge)
  --help                               Show this help

Exit Codes:
  0 - Pass or skip (forge not available)
  2 - Fail (contract check failed)
  3 - Error (invalid arguments)
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --check-deployment)
        ACTION="check-deployment"
        shift
        ;;
      --validate-tx)
        ACTION="validate-tx"
        shift
        ;;
      --verify-contract)
        ACTION="verify-contract"
        shift
        ;;
      --run-tests)
        ACTION="run-tests"
        shift
        ;;
      --full-check)
        ACTION="full-check"
        shift
        ;;
      --gate)
        ACTION="gate"
        shift
        ;;
      --address)
        ADDRESS="$2"
        shift 2
        ;;
      --tx-hash)
        TX_HASH="$2"
        shift 2
        ;;
      --contract)
        CONTRACT_NAME="$2"
        shift 2
        ;;
      --project-dir)
        PROJECT_DIR="$2"
        shift 2
        ;;
      --rpc-url)
        RPC_URL="$2"
        shift 2
        ;;
      --chain-id)
        CHAIN_ID="$2"
        shift 2
        ;;
      --forge-path)
        FORGE_PATH="$2"
        shift 2
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage >&2
        exit 3
        ;;
    esac
  done

  # Default project dir
  PROJECT_DIR="${PROJECT_DIR:-$PROJECT_ROOT}"
  PROJECT_DIR="$(cd "$PROJECT_DIR" 2>/dev/null && pwd)" || {
    echo "ERROR: Invalid project directory: $PROJECT_DIR" >&2
    exit 3
  }
}

# ==============================================================================
# Utility Functions
# ==============================================================================

# Check if forge is available
has_forge() {
  command -v "$FORGE_PATH" &>/dev/null
}

# Check if cast is available
has_cast() {
  command -v "$CAST_PATH" &>/dev/null
}

# Check if project has Solidity contracts
has_solidity() {
  local dir="$1"
  [[ -d "$dir/contracts/onchain" ]] && return 0
  find "$dir" -maxdepth 3 -name "*.sol" -type f 2>/dev/null | grep -qv "/lib/" && return 0
  return 1
}

# Check if foundry.toml exists
has_foundry_toml() {
  local dir="$1"
  [[ -f "$dir/foundry.toml" ]]
}

# Emit advisory skip message
emit_skip() {
  local reason="$1"
  echo "ONCHAIN CONTRACT GATE: skip ($reason)"
}

# Emit pass message
emit_pass() {
  local details="$1"
  echo "ONCHAIN CONTRACT GATE: pass - $details"
}

# Emit fail message
emit_fail() {
  local details="$1"
  echo "ONCHAIN CONTRACT GATE: fail - $details" >&2
}

# Write report JSON
write_report() {
  local dir="$1"
  local status="$2"
  local pass="$3"
  local error_count="$4"
  local warn_count="$5"
  local checks="$6"
  local msg="${7:-}"

  local verify_dir="$dir/.claude/verification"
  local report="$verify_dir/onchain-contract-gate.json"
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  mkdir -p "$verify_dir"

  if [[ -n "$checks" ]]; then
    jq -n \
      --arg ts "$now" \
      --arg status "$status" \
      --argjson pass "$pass" \
      --argjson error_count "$error_count" \
      --argjson warn_count "$warn_count" \
      --argjson checks "$checks" \
      --arg msg "$msg" \
      '{generated_at:$ts,status:$status,pass:$pass,error_count:$error_count,warn_count:$warn_count,checks:$checks,message:$msg}' \
      > "$report"
  else
    jq -n \
      --arg ts "$now" \
      --arg status "$status" \
      --argjson pass "$pass" \
      --argjson error_count "$error_count" \
      --argjson warn_count "$warn_count" \
      --arg msg "$msg" \
      '{generated_at:$ts,status:$status,pass:$pass,error_count:$error_count,warn_count:$warn_count,checks:[],message:$msg}' \
      > "$report"
  fi

  echo "Report: $report"
}

# ==============================================================================
# Core Actions
# ==============================================================================

# Run forge test
run_forge_test() {
  local dir="$1"
  local errors=0
  local warnings=0
  local checks='[]'

  if ! has_forge; then
    emit_skip "forge not installed"
    return 0
  fi

  if ! has_foundry_toml "$dir"; then
    emit_skip "no foundry.toml"
    return 0
  fi

  echo "Running forge test..."

  # Run forge test with JSON output
  local test_output
  if test_output="$(cd "$dir" && "$FORGE_PATH" test --json 2>&1)"; then
    checks='[{"name":"forge_test","status":"pass"}]'
    echo "  forge test: PASS"
  else
    errors=1
    checks='[{"name":"forge_test","status":"fail","details":"test failures detected"}]'
    echo "  forge test: FAIL" >&2
    echo "  $test_output" >&2
  fi

  write_report "$dir" "evaluated" "$([[ $errors -eq 0 ]] && echo true || echo false)" "$errors" "$warnings" "$checks" "forge test completed"

  return $errors
}

# Run forge build
run_forge_build() {
  local dir="$1"
  local errors=0
  local warnings=0
  local checks='[]'

  if ! has_forge; then
    emit_skip "forge not installed"
    return 0
  fi

  if ! has_foundry_toml "$dir"; then
    emit_skip "no foundry.toml"
    return 0
  fi

  echo "Running forge build..."

  # Run forge build
  local build_output
  if build_output="$(cd "$dir" && "$FORGE_PATH" build 2>&1)"; then
    checks='[{"name":"forge_build","status":"pass"}]'
    echo "  forge build: PASS"
  else
    errors=1
    checks='[{"name":"forge_build","status":"fail","details":"compilation failed"}]'
    echo "  forge build: FAIL" >&2
    echo "  $build_output" >&2
  fi

  write_report "$dir" "evaluated" "$([[ $errors -eq 0 ]] && echo true || echo false)" "$errors" "$warnings" "$checks" "forge build completed"

  return $errors
}

# Full check: build + test
run_full_check() {
  local dir="$1"
  local errors=0
  local warnings=0
  local checks='[]'

  if ! has_forge; then
    emit_skip "forge not installed"
    write_report "$dir" "skip" true 0 0 '[]' "forge not available"
    return 0
  fi

  if ! has_foundry_toml "$dir"; then
    emit_skip "no foundry.toml"
    write_report "$dir" "skip" true 0 0 '[]' "no foundry.toml found"
    return 0
  fi

  echo "Running full onchain contract checks..."

  # Build
  echo "  forge build..."
  local build_status="pass"
  if ! (cd "$dir" && "$FORGE_PATH" build 2>&1) >/dev/null; then
    build_status="fail"
    errors=$((errors + 1))
    echo "    FAILED" >&2
  else
    echo "    OK"
  fi

  # Test
  echo "  forge test..."
  local test_status="pass"
  if ! (cd "$dir" && "$FORGE_PATH" test 2>&1) >/dev/null; then
    test_status="fail"
    errors=$((errors + 1))
    echo "    FAILED" >&2
  else
    echo "    OK"
  fi

  # Build checks array
  checks="[{\"name\":\"forge_build\",\"status\":\"$build_status\"},{\"name\":\"forge_test\",\"status\":\"$test_status\"}]"

  local status="pass"
  [[ $errors -gt 0 ]] && status="fail"

  write_report "$dir" "$status" "$([[ $errors -eq 0 ]] && echo true || echo false)" "$errors" "$warnings" "$checks" "full check completed"

  if [[ $errors -gt 0 ]]; then
    emit_fail "$errors check(s) failed"
    return 2
  fi

  emit_pass "all checks passed"
  return 0
}

# Check contract deployment
check_deployment() {
  local dir="$1"
  local addr="$2"

  if ! has_cast; then
    emit_skip "cast not installed"
    return 0
  fi

  if [[ -z "$RPC_URL" ]]; then
    emit_skip "RPC_URL not configured"
    return 0
  fi

  if [[ -z "$addr" ]]; then
    emit_fail "--address required for deployment check"
    return 3
  fi

  echo "Checking deployment at $addr..."

  local code
  if code="$("$CAST_PATH" code "$addr" --rpc-url "$RPC_URL" 2>&1)"; then
    if [[ "$code" == "0x" || -z "$code" ]]; then
      emit_fail "no contract deployed at $addr"
      return 2
    fi
    emit_pass "contract found at $addr"
    return 0
  else
    emit_fail "failed to check deployment: $code"
    return 2
  fi
}

# Validate transaction
validate_tx() {
  local dir="$1"
  local tx_hash="$2"

  if ! has_cast; then
    emit_skip "cast not installed"
    return 0
  fi

  if [[ -z "$RPC_URL" ]]; then
    emit_skip "RPC_URL not configured"
    return 0
  fi

  if [[ -z "$tx_hash" ]]; then
    emit_fail "--tx-hash required for tx validation"
    return 3
  fi

  echo "Validating transaction $tx_hash..."

  local receipt
  if receipt="$("$CAST_PATH" tx "$tx_hash" --rpc-url "$RPC_URL" 2>&1)"; then
    # Check for success (status 0x1)
    if echo "$receipt" | grep -qi "status.*0x1\|status.*true"; then
      emit_pass "transaction $tx_hash successful"
      return 0
    else
      emit_fail "transaction $tx_hash failed or reverted"
      return 2
    fi
  else
    emit_fail "failed to fetch transaction: $receipt"
    return 2
  fi
}

# Verify contract on explorer
verify_contract() {
  local dir="$1"
  local addr="$2"
  local contract="$3"

  if ! has_forge; then
    emit_skip "forge not installed"
    return 0
  fi

  if [[ -z "$addr" || -z "$contract" ]]; then
    emit_fail "--address and --contract required for verification"
    return 3
  fi

  if [[ -z "$CHAIN_ID" ]]; then
    emit_fail "--chain-id or CHAIN_ID env required for verification"
    return 3
  fi

  echo "Verifying contract $contract at $addr (chain: $CHAIN_ID)..."

  local verify_output
  if verify_output="$(cd "$dir" && "$FORGE_PATH" verify-contract --chain-id "$CHAIN_ID" "$addr" "$contract" 2>&1)"; then
    emit_pass "contract verification submitted"
    echo "$verify_output"
    return 0
  else
    # Verification may fail if already verified - check output
    if echo "$verify_output" | grep -qi "already verified"; then
      emit_pass "contract already verified"
      return 0
    fi
    emit_fail "verification failed: $verify_output"
    return 2
  fi
}

# Gate mode - reads stdin JSON (from hook system)
run_gate_mode() {
  local input
  input="$(cat)"

  local cwd
  cwd="$(jq -r '.cwd // empty' <<< "$input" 2>/dev/null || echo "")"
  PROJECT_DIR="${cwd:-$PROJECT_ROOT}"

  local verify_dir="$PROJECT_DIR/.claude/verification"
  local report="$verify_dir/onchain-contract-gate.json"
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  mkdir -p "$verify_dir"

  # Check for Solidity contracts
  local has_sol=false
  [[ -d "$PROJECT_DIR/contracts/onchain" ]] && has_sol=true
  find "$PROJECT_DIR" -maxdepth 3 -name "*.sol" -type f 2>/dev/null | grep -qv "/lib/" && has_sol=true

  if [[ "$has_sol" != "true" ]]; then
    jq -n --arg ts "$now" \
      '{generated_at:$ts,status:"no_contracts",pass:true,error_count:0,warn_count:0,checks:[],message:"No Solidity contracts found"}' \
      > "$report"
    emit_skip "no Solidity contracts"
    exit 0
  fi

  # Has Solidity - check if forge available
  if ! has_forge; then
    jq -n --arg ts "$now" \
      '{generated_at:$ts,status:"skip_forge_unavailable",pass:true,error_count:0,warn_count:0,checks:[],message:"Forge not installed - skipping onchain checks"}' \
      > "$report"
    emit_skip "forge not installed"
    exit 0
  fi

  # Has forge - check if foundry.toml exists
  if ! has_foundry_toml "$PROJECT_DIR"; then
    jq -n --arg ts "$now" \
      '{generated_at:$ts,status:"skip_no_foundry",pass:true,error_count:0,warn_count:0,checks:[],message:"No foundry.toml found"}' \
      > "$report"
    emit_skip "no foundry.toml"
    exit 0
  fi

  # Run actual checks
  local errors=0
  local warnings=0
  local checks='[]'

  echo "ONCHAIN CONTRACT GATE: evaluating..."

  # Build check
  echo "  Checking forge build..."
  local build_status="pass"
  local build_msg=""
  if ! (cd "$PROJECT_DIR" && "$FORGE_PATH" build 2>&1) >/dev/null; then
    build_status="fail"
    errors=$((errors + 1))
    build_msg="compilation failed"
    echo "    FAILED" >&2
  else
    echo "    OK"
  fi
  checks="$(echo "$checks" | jq --arg status "$build_status" --arg msg "$build_msg" '. + [{"name":"forge_build","status":$status,"message":$msg}]')"

  # Test check
  echo "  Checking forge test..."
  local test_status="pass"
  local test_msg=""
  local test_output
  if ! test_output="$(cd "$PROJECT_DIR" && "$FORGE_PATH" test 2>&1)"; then
    test_status="fail"
    errors=$((errors + 1))
    test_msg="test failures detected"
    echo "    FAILED" >&2
  else
    # Count tests from output (use head -1 to get first match only)
    local passed failed
    passed="$(echo "$test_output" | grep -oE '[0-9]+ passed' | head -1 | grep -oE '[0-9]+' || echo "0")"
    failed="$(echo "$test_output" | grep -oE '[0-9]+ failed' | head -1 | grep -oE '[0-9]+' || echo "0")"
    test_msg="$passed passed, $failed failed"
    echo "    OK ($test_msg)"
  fi
  checks="$(echo "$checks" | jq --arg status "$test_status" --arg msg "$test_msg" '. + [{"name":"forge_test","status":$status,"message":$msg}]')"

  # Write final report
  local status="pass"
  [[ $errors -gt 0 ]] && status="fail"

  jq -n \
    --arg ts "$now" \
    --arg status "$status" \
    --argjson pass "$([[ $errors -eq 0 ]] && echo true || echo false)" \
    --argjson error_count "$errors" \
    --argjson warn_count "$warnings" \
    --argjson checks "$checks" \
    '{generated_at:$ts,status:$status,pass:$pass,error_count:$error_count,warn_count:$warn_count,checks:$checks}' \
    > "$report"

  if [[ $errors -gt 0 ]]; then
    emit_fail "$errors check(s) failed"
    echo "Report: $report"
    exit 2
  fi

  emit_pass "all checks passed"
  echo "Report: $report"
  exit 0
}

# ==============================================================================
# Main
# ==============================================================================

main() {
  parse_args "$@"

  # Gate mode (stdin) takes precedence
  if [[ "$ACTION" == "gate" ]]; then
    run_gate_mode
    exit $?
  fi

  # Default to gate mode if no action specified
  if [[ -z "$ACTION" ]]; then
    # Check if stdin has data (hook mode)
    if [[ ! -t 0 ]]; then
      run_gate_mode
      exit $?
    fi
    usage
    exit 3
  fi

  case "$ACTION" in
    check-deployment)
      check_deployment "$PROJECT_DIR" "$ADDRESS"
      ;;
    validate-tx)
      validate_tx "$PROJECT_DIR" "$TX_HASH"
      ;;
    verify-contract)
      verify_contract "$PROJECT_DIR" "$ADDRESS" "$CONTRACT_NAME"
      ;;
    run-tests)
      run_forge_test "$PROJECT_DIR"
      ;;
    full-check)
      run_full_check "$PROJECT_DIR"
      ;;
    *)
      echo "Unknown action: $ACTION" >&2
      usage >&2
      exit 3
      ;;
  esac
}

main "$@"
