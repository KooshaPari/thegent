#!/usr/bin/env bash
# async-test-runner.sh — PostToolUse hook (Edit|Write)
# After file edits, detects which test framework applies and runs relevant
# tests asynchronously. Results are stored for later consumption by other hooks.
# Advisory only (always exits 0). Budget: <2s for dispatch, tests run async.
set -euo pipefail
HOOK_NAME="ASYNC-TEST-RUNNER"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

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

# Derive test files for a given source file (pure bash, no subprocess spawns)
find_test_files() {
  local src="$1"
  local base ext name dir
  base="${src##*/}"
  ext="${base##*.}"
  name="${base%.*}"
  # dirname via parameter expansion (eliminates dirname subprocess)
  dir="${src%/*}"

  case "$ext" in
    py)
      for candidate in \
        "${dir}/test_${name}.py" \
        "${dir}/tests/test_${name}.py" \
        "${PROJECT_DIR}/test/unit/test_${name}.py" \
        "${PROJECT_DIR}/tests/test_${name}.py" \
        "${PROJECT_DIR}/test/test_${name}.py"; do
        [[ -f "$candidate" ]] && echo "$candidate"
      done
      # If the file itself is a test
      [[ "$base" == test_* ]] && echo "$src"
      ;;
    sh|bash)
      for candidate in \
        "${PROJECT_DIR}/test/unit/test_${name}.bats" \
        "${PROJECT_DIR}/test/unit/${name}.bats" \
        "${PROJECT_DIR}/test/integration/test_${name}.bats" \
        "${PROJECT_DIR}/test/integration/${name}.bats"; do
        [[ -f "$candidate" ]] && echo "$candidate"
      done
      ;;
    bats)
      echo "$src"
      ;;
    ts|tsx|js|jsx)
      for candidate in \
        "${dir}/${name}.test.${ext}" \
        "${dir}/${name}.spec.${ext}" \
        "${dir}/__tests__/${name}.test.${ext}" \
        "${dir}/__tests__/${name}.${ext}"; do
        [[ -f "$candidate" ]] && echo "$candidate"
      done
      # If the file itself is a test
      case "$base" in
        *.test.*|*.spec.*) echo "$src" ;;
      esac
      ;;
    go)
      [[ -f "${dir}/${name}_test.go" ]] && echo "${dir}/${name}_test.go"
      # If the file itself is a test
      [[ "$base" == *_test.go ]] && echo "$src"
      ;;
  esac
  return 0
}

# ---------- Determine test files ----------
TEST_FILES=$(find_test_files "$FILE_PATH")

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
        test_output=$(pytest --tb=short --no-header -q $TEST_FILES 2>&1) || test_exit=$?
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
        test_output=$(bats $TEST_FILES 2>&1) || test_exit=$?
      fi
      ;;
    ts|tsx|js|jsx)
      if [[ -f "${PROJECT_DIR}/node_modules/.bin/vitest" ]]; then
        test_framework="vitest"
        test_output=$(cd "$PROJECT_DIR" && npx vitest run --reporter=verbose $TEST_FILES 2>&1) || test_exit=$?
      elif [[ -f "${PROJECT_DIR}/node_modules/.bin/jest" ]]; then
        test_framework="jest"
        test_output=$(cd "$PROJECT_DIR" && npx jest --verbose $TEST_FILES 2>&1) || test_exit=$?
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
