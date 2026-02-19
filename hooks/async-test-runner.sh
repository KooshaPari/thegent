#!/bin/zsh
# async-test-runner.sh — PostToolUse hook (Edit|Write)
# After file edits, detects which test framework applies and runs relevant
# tests asynchronously. Results are stored for later consumption by other hooks.
# Advisory only (always exits 0). Budget: <2s for dispatch, tests run async.
set -euo pipefail
HOOK_NAME="ASYNC-TEST-RUNNER"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Initialize variables if not set by hook_init/dispatcher
PROJECT_DIR="${PROJECT_DIR:-.}"
now="${now:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

# Stderr message on unexpected failure (set -e)
trap 'echo "ASYNC-TEST-RUNNER FAIL: unexpected error at line $LINENO" >&2' ERR

RESULTS_FILE="$HOME/.claude/.async-test-results.json"
PID_FILE="$HOME/.claude/.async-test-pid"

[[ -z "$FILE_PATH" ]] && exit 0

# --- Fast-path exit: only analyze source and test files ---
EXT="${FILE_PATH##*.}"
case "$EXT" in
  py|sh|bash|ts|tsx|js|jsx|go|rs|rb|php|java|kt|swift|bats) ;;
  *) exit 0 ;;
esac

# Skip non-source paths (bash builtin pattern matching, no spawns)
case "$FILE_PATH" in
  */node_modules/*|*/.git/*|*/vendor/*|*/__pycache__/*|*/.venv/*|*/dist/*|*/build/*) exit 0 ;;
esac

# ---------- Determine test files (P4: use shared get_affected_tests from common.sh) ----------
# Consolidates with quality-gate affected test selection; same logic as affected_tests_for_file.
TEST_FILES=$(get_affected_tests "$FILE_PATH")

# If no test files found, nothing to run
[[ -z "$TEST_FILES" ]] && exit 0

# Kill previous async test if still running
if [[ -f "$PID_FILE" ]]; then
  OLD_PID=$(< "$PID_FILE")
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null || true
  fi
  rm -f "$PID_FILE"
fi

# Build and run the test command asynchronously
run_tests_async() {
  local test_output=""
  local test_exit=0
  local test_framework=""
  local started_at="$now"

  case "$EXT" in
    py)
      if [[ "$(tool_available pytest)" == "true" ]]; then
        test_framework="pytest"
        test_output=$(pytest --tb=short --no-header -q "$TEST_FILES" 2>&1) || test_exit=$?
      elif command -v python3 >/dev/null 2>&1; then
        test_framework="unittest"
        for tf in $TEST_FILES; do
          test_output+=$(python3 -m pytest "$tf" --tb=short -q 2>&1) || test_exit=$?
        done
      fi
      ;;
    sh|bash|bats)
      if [[ "$(tool_available bats)" == "true" ]]; then
        test_framework="bats"
        test_output=$(bats "$TEST_FILES" 2>&1) || test_exit=$?
      fi
      ;;
    ts|tsx|js|jsx)
      if [[ -f "${PROJECT_DIR}/node_modules/.bin/vitest" ]]; then
        test_framework="vitest"
        test_output=$(cd "$PROJECT_DIR" && _js_exec vitest run --reporter=verbose "$TEST_FILES" 2>&1) || test_exit=$?
      elif [[ -f "${PROJECT_DIR}/node_modules/.bin/jest" ]]; then
        test_framework="jest"
        test_output=$(cd "$PROJECT_DIR" && _js_exec jest --verbose "$TEST_FILES" 2>&1) || test_exit=$?
      fi
      ;;
    go)
      test_framework="go-test"
      # Get first test file's directory using bash parameter expansion (no dirname/head)
      local first_test="${TEST_FILES%%$'\n'*}"
      local test_dir="${first_test%/*}"
      test_output=$(cd "$test_dir" && go test -v -count=1 ./... 2>&1) || test_exit=$?
      ;;
  esac

  # Skip writing if no framework was found
  [[ -z "$test_framework" ]] && { rm -f "$PID_FILE"; return; }

  # Generate finished_at from bash (reuse $now format pattern, but need current time)
  local finished_at
  finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  # Truncate output to avoid huge JSON
  if [[ ${#test_output} -gt 4096 ]]; then
    test_output="${test_output:0:2048}

... (truncated) ...

${test_output: -2048}"
  fi

  # Build test_files JSON array and escape output using bash _json_escape helper
  # This eliminates 2 jq spawns (jq -Rs, jq -R | jq -s)
  local escaped_output
  escaped_output="\"$(_json_escape "$test_output")\""

  local test_files_json="["
  local _first=true
  local _tf
  while IFS= read -r _tf; do
    [[ -z "$_tf" ]] && continue
    if [[ "$_first" == "true" ]]; then
      test_files_json+="\"$(_json_escape "$_tf")\""
      _first=false
    else
      test_files_json+=",\"$(_json_escape "$_tf")\""
    fi
  done <<< "$TEST_FILES"
  test_files_json+="]"

  local status_str
  [[ $test_exit -eq 0 ]] && status_str="passed" || status_str="failed"

  printf '{"started_at":"%s","finished_at":"%s","trigger_file":"%s","test_files":%s,"framework":"%s","exit_code":%d,"output":%s,"status":"%s"}\n' \
    "$started_at" "$finished_at" "$(_json_escape "$FILE_PATH")" "$test_files_json" \
    "$test_framework" "$test_exit" "$escaped_output" "$status_str" > "$RESULTS_FILE"

  # Count test files using bash (no wc/tr spawns)
  local file_count=0
  local _w
  for _w in $TEST_FILES; do (( file_count++ )); done

  if [[ $test_exit -eq 0 ]]; then
    echo "Async tests PASSED ($test_framework): ${file_count} file(s)"
  else
    echo "Async tests FAILED ($test_framework, exit=$test_exit): ${file_count} file(s)"
    # Show last few lines of output using bash (no tail spawn)
    local -a _lines=()
    while IFS= read -r _line; do
      _lines+=("$_line")
    done <<< "$test_output"
    local _total=${#_lines[@]}
    local _start=$(( _total > 10 ? _total - 10 : 0 ))
    local _i
    for (( _i=_start; _i<_total; _i++ )); do
      echo "${_lines[$_i]}"
    done
  fi

  rm -f "$PID_FILE"
}

# Run in background
run_tests_async &
echo $! > "$PID_FILE"
disown

echo "Async test runner: dispatched for ${FILE_PATH##*/}"
exit 0
