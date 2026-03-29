#!/usr/bin/env bats
# test_rust_dispatch.bats — BATS tests for Phase 2 hook-rust opt-in dispatch.
# Covers:
#   - rust_dispatch.sh: enable/disable logic, binary resolution, dispatch
#   - hooks/debounce.sh: Rust opt-in and shell fallback
#   - hooks/incremental-check.sh: Rust opt-in and shell fallback
#   - hooks/circuit-breaker.sh: Rust opt-in and shell fallback
#
# Run: bats tests/test_rust_dispatch.bats
# Traces to: FR-HOOKS-001, FR-HOOKS-002, FR-HOOKS-003, FR-HOOKS-004

HOOKS_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)/hooks"
LIB_DIR="${HOOKS_DIR}/lib"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_write_stub_binary() {
  local dest="$1"
  local fail_cmd="${2:-__none__}"
  cat > "${dest}" << STUBEOF
#!/usr/bin/env bash
set -euo pipefail
cmd="\${1:-}"; shift || true
[[ "\$cmd" == "${fail_cmd}" ]] && { echo "STUB_FAIL: \$cmd" >&2; exit 5; }
case "\$cmd" in
  debounce)          echo '["stub_file.py"]'; exit 0 ;;
  incremental-check) exit 0 ;;
  incremental-record) exit 0 ;;
  breaker-check)     echo "closed"; exit 0 ;;
  breaker-record)    exit 0 ;;
  breaker-reset)     exit 0 ;;
  breaker-success)   exit 0 ;;
  *) echo "STUB: unknown \$cmd" >&2; exit 2 ;;
esac
STUBEOF
  chmod +x "${dest}"
}

_env_rust_on() {
  export THGENT_HOOKS_RUST=1
  export HOOK_CACHE_DIR="${BATS_TEST_TMPDIR}/hook-cache"
  mkdir -p "${HOOK_CACHE_DIR}"
}

_env_rust_off() {
  export THGENT_HOOKS_RUST=0
  export HOOK_CACHE_DIR="${BATS_TEST_TMPDIR}/hook-cache"
  mkdir -p "${HOOK_CACHE_DIR}"
}

setup() {
  mkdir -p "${BATS_TEST_TMPDIR}"
  unset THGENT_HOOKS_BIN THGENT_HOOKS_RUST_BIN
}

teardown() {
  rm -rf "${BATS_TEST_TMPDIR}" 2>/dev/null || true
}

# ===========================================================================
# rust_dispatch.sh — FR-HOOKS-003
# ===========================================================================

@test "rust_dispatch: disabled when THGENT_HOOKS_RUST=0" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  export THGENT_HOOKS_RUST=0
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash -c "source '${LIB_DIR}/rust_dispatch.sh'; hook_rust_dispatch debounce test && echo DISPATCHED || echo FALLBACK"
  [[ "${output}" == *"FALLBACK"* ]]
}

@test "rust_dispatch: enabled when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  export THGENT_HOOKS_RUST=1
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash -c "source '${LIB_DIR}/rust_dispatch.sh'; hook_rust_dispatch debounce test"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"stub_file.py"* ]]
}

@test "rust_dispatch: uses THGENT_HOOKS_RUST_BIN path override" {
  stub="${BATS_TEST_TMPDIR}/custom-hooks"
  _write_stub_binary "${stub}"
  export THGENT_HOOKS_RUST=1
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash -c "source '${LIB_DIR}/rust_dispatch.sh'; hook_rust_dispatch breaker-check test"
  [ "${status}" -eq 0 ]
  [ "${output}" = "closed" ]
}

@test "rust_dispatch: falls back gracefully when binary not found" {
  export THGENT_HOOKS_RUST=1
  export THGENT_HOOKS_RUST_BIN="/nonexistent/thegent-hooks"
  unset THGENT_HOOKS_BIN
  run bash -c "source '${LIB_DIR}/rust_dispatch.sh'; hook_rust_dispatch debounce test && echo DISPATCHED || echo FALLBACK"
  [[ "${output}" == *"FALLBACK"* ]]
}

@test "rust_dispatch: forwards non-zero exit code from binary" {
  stub="${BATS_TEST_TMPDIR}/fail-stub"
  _write_stub_binary "${stub}" "debounce"
  export THGENT_HOOKS_RUST=1
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash -c "source '${LIB_DIR}/rust_dispatch.sh'; hook_rust_dispatch debounce test"
  [ "${status}" -eq 5 ]
}

# ===========================================================================
# debounce.sh — FR-HOOKS-001, FR-HOOKS-003
# ===========================================================================

@test "debounce.sh: delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  export HOOK_NAME="test-debounce"
  export FILE_PATH="${BATS_TEST_TMPDIR}/sample.py"
  touch "${FILE_PATH}"
  run bash "${HOOKS_DIR}/debounce.sh"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"stub_file.py"* ]]
}

@test "debounce.sh: shell fallback used when THGENT_HOOKS_RUST=0" {
  _env_rust_off
  export HOOK_NAME="test-debounce-shell"
  export FILE_PATH="${BATS_TEST_TMPDIR}/sample.py"
  export DEBOUNCE_TIMEOUT=0
  run bash "${HOOKS_DIR}/debounce.sh"
  [ "${status}" -eq 0 ]
}

@test "debounce.sh: exits 1 within debounce window (shell fallback)" {
  _env_rust_off
  export HOOK_NAME="test-debounce-window"
  export FILE_PATH="${BATS_TEST_TMPDIR}/sample.py"
  export DEBOUNCE_TIMEOUT=9999
  bash "${HOOKS_DIR}/debounce.sh" || true
  run bash "${HOOKS_DIR}/debounce.sh"
  [ "${status}" -eq 1 ]
}

@test "debounce.sh: exits 0 after window elapses (shell fallback)" {
  _env_rust_off
  export HOOK_NAME="test-debounce-elapsed"
  export FILE_PATH="${BATS_TEST_TMPDIR}/sample.py"
  export DEBOUNCE_TIMEOUT=0
  run bash "${HOOKS_DIR}/debounce.sh"
  [ "${status}" -eq 0 ]
}

# ===========================================================================
# incremental-check.sh — FR-HOOKS-002, FR-HOOKS-003
# ===========================================================================

@test "incremental-check.sh: check delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash "${HOOKS_DIR}/incremental-check.sh" "test-hook" "${BATS_TEST_TMPDIR}/a.py"
  [ "${status}" -eq 0 ]
}

@test "incremental-check.sh: --record delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash "${HOOKS_DIR}/incremental-check.sh" "--record" "test-hook" "${BATS_TEST_TMPDIR}/a.py"
  [ "${status}" -eq 0 ]
}

@test "incremental-check.sh: exits 1 with no prior manifest (shell fallback)" {
  _env_rust_off
  hook_key="no-prior-$$"
  run bash "${HOOKS_DIR}/incremental-check.sh" "${hook_key}" "${BATS_TEST_TMPDIR}/a.py"
  [ "${status}" -eq 1 ]
}

@test "incremental-check.sh: exits 0 when files unchanged (shell fallback)" {
  _env_rust_off
  hook_key="unchanged-$$"
  test_file="${BATS_TEST_TMPDIR}/unchanged.py"
  echo "x = 1" > "${test_file}"
  bash "${HOOKS_DIR}/incremental-check.sh" "--record" "${hook_key}" "${test_file}"
  run bash "${HOOKS_DIR}/incremental-check.sh" "${hook_key}" "${test_file}"
  [ "${status}" -eq 0 ]
}

@test "incremental-check.sh: exits 1 when file changes (shell fallback)" {
  _env_rust_off
  hook_key="changed-$$"
  test_file="${BATS_TEST_TMPDIR}/changed.py"
  echo "x = 1" > "${test_file}"
  bash "${HOOKS_DIR}/incremental-check.sh" "--record" "${hook_key}" "${test_file}"
  echo "x = 2" > "${test_file}"
  run bash "${HOOKS_DIR}/incremental-check.sh" "${hook_key}" "${test_file}"
  [ "${status}" -eq 1 ]
}

# ===========================================================================
# circuit-breaker.sh — FR-HOOKS-004, FR-HOOKS-003
# ===========================================================================

@test "circuit-breaker.sh: check delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "test-tool"
  [ "${status}" -eq 0 ]
  [ "${output}" = "closed" ]
}

@test "circuit-breaker.sh: record delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "test-tool"
  [ "${status}" -eq 0 ]
}

@test "circuit-breaker.sh: reset delegates to thegent-hooks when THGENT_HOOKS_RUST=1" {
  stub="${BATS_TEST_TMPDIR}/stub"
  _write_stub_binary "${stub}"
  _env_rust_on
  export THGENT_HOOKS_RUST_BIN="${stub}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "reset" "test-tool"
  [ "${status}" -eq 0 ]
}

@test "circuit-breaker.sh: check returns closed initially (shell fallback)" {
  _env_rust_off
  hook_key="fresh-$$"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "${hook_key}"
  [ "${status}" -eq 0 ]
  [ "${output}" = "closed" ]
}

@test "circuit-breaker.sh: opens after threshold failures (shell fallback)" {
  _env_rust_off
  hook_key="threshold-$$"
  export BREAKER_THRESHOLD=2
  export BREAKER_COOLDOWN=9999
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "${hook_key}" "2" "9999"
  [ "${status}" -eq 1 ]
  [ "${output}" = "open" ]
}

@test "circuit-breaker.sh: reset clears state (shell fallback)" {
  _env_rust_off
  hook_key="reset-$$"
  export BREAKER_THRESHOLD=1
  export BREAKER_COOLDOWN=9999
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  bash "${HOOKS_DIR}/circuit-breaker.sh" "reset" "${hook_key}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "${hook_key}" "1" "9999"
  [ "${status}" -eq 0 ]
  [ "${output}" = "closed" ]
}

@test "circuit-breaker.sh: success decrements failure count (shell fallback)" {
  _env_rust_off
  hook_key="success-$$"
  export BREAKER_THRESHOLD=3
  export BREAKER_COOLDOWN=9999
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  bash "${HOOKS_DIR}/circuit-breaker.sh" "success" "${hook_key}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "${hook_key}" "3" "9999"
  [ "${status}" -eq 0 ]
  [ "${output}" = "closed" ]
}

@test "circuit-breaker.sh: returns half-open after cooldown (shell fallback)" {
  _env_rust_off
  hook_key="halfopen-$$"
  export BREAKER_THRESHOLD=1
  export BREAKER_COOLDOWN=0
  bash "${HOOKS_DIR}/circuit-breaker.sh" "record" "${hook_key}"
  run bash "${HOOKS_DIR}/circuit-breaker.sh" "check" "${hook_key}" "1" "0"
  [ "${status}" -eq 0 ]
  [ "${output}" = "half-open" ]
}
