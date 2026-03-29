#!/usr/bin/env bash
# BATS test configuration — strict shell testing
# Source this from test_helper.bash

# Strict mode
set -euo pipefail

# BATS configuration
export BATS_TEST_TIMEOUT=30  # seconds per test
export BATS_NUMBER_OF_PARALLEL_JOBS=4

# Load BATS libraries
BATS_LIB_DIR="${BATS_TEST_DIRNAME}/libs"
load "${BATS_LIB_DIR}/bats-support/load"
load "${BATS_LIB_DIR}/bats-assert/load"

# Test helper functions
setup() {
  # Create temp directory for test artifacts
  TEST_TEMP_DIR="$(mktemp -d)"
  export TEST_TEMP_DIR
}

teardown() {
  # Clean up temp directory
  if [[ -d "${TEST_TEMP_DIR:-}" ]]; then
    rm -rf "${TEST_TEMP_DIR}"
  fi
}

# Assert file exists and is non-empty
assert_file_exists() {
  local file="$1"
  [[ -f "$file" ]] || fail "Expected file to exist: $file"
  [[ -s "$file" ]] || fail "Expected file to be non-empty: $file"
}

# Assert command succeeds within timeout
assert_succeeds_within() {
  local timeout="$1"
  shift
  timeout "$timeout" "$@" || fail "Command did not succeed within ${timeout}s: $*"
}

# FR traceability helper — extract FR tags from test name
extract_fr_tags() {
  local test_name="$1"
  echo "$test_name" | grep -oE 'FR-[A-Z]+-[0-9]+' || true
}
