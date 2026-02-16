#!/usr/bin/env bash
# task-completion-verifier.sh — TaskCompleted hook
# Checks that modified files have corresponding test files and pass syntax
# checks. Advisory only (always exits 0).
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_FILE="${_CACHE_DIR}/task-completion-${_CACHE_KEY}.result"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < _CACHE_TTL )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

HOOK_NAME="TASK-COMPLETION-VERIFIER"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Output immediately to prevent idle timeout
echo "TASK-COMPLETION-VERIFIER: starting..." >&2

# --- P1 optimization: Skip if no source files changed ---
# Only run if code files were modified
if ! any_source_changed; then
  echo "TASK-COMPLETION-VERIFIER: skipped (no source files changed)"
  exit 0
fi

# --- Cache check — skip if unchanged within TTL ---
_tc_cache_key="${HOOK_NAME}_${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}"
_ttl="${HOOK_CACHE_TTL:-600}"
if hook_cache_check "$_tc_cache_key" "$_ttl"; then
  hook_cache_read "$_tc_cache_key" | tee "$_CACHE_FILE" 2>/dev/null
  exit 0
fi

# Stderr message on unexpected failure (set -e)
trap 'echo "TASK-COMPLETION-VERIFIER FAIL: unexpected error at line $LINENO" >&2' ERR

TASK_START_MARKER="/tmp/.claude-task-start"

WARNINGS=()
CHECKED=0

# ---------- Collect recently modified source files ----------
# Use CHANGED_FILES from dispatcher if available, otherwise use session-changes.log
MODIFIED_FILES=()

# Priority 1: Use dispatcher-provided CHANGED_FILES
if [[ -n "${CHANGED_FILES:-}" ]]; then
  while IFS= read -r file; do
    [[ -n "$file" && -f "$file" ]] && MODIFIED_FILES+=("$file")
  done < <(echo "$CHANGED_FILES" | tr ' ' '\n' | grep -E '\.(py|sh|bash|ts|js|tsx|jsx|go|rs)$')
fi

# Priority 2: Fallback to session-changes.log (no find fallback - too slow)
if [[ ${#MODIFIED_FILES[@]} -eq 0 ]] && [[ -f "$CHANGE_LOG" ]]; then
  while IFS= read -r file; do
    [[ -f "$file" ]] && MODIFIED_FILES+=("$file")
  done < <(grep -oE '/[^ ]+\.(py|sh|bash|ts|js|tsx|jsx|go|rs)' "$CHANGE_LOG" 2>/dev/null | sort -u)
fi

# Priority 3: Only use git diff if no other source (last resort, not find)
if [[ ${#MODIFIED_FILES[@]} -eq 0 ]] && in_git_repo >/dev/null 2>&1; then
  while IFS= read -r file; do
    [[ -f "$file" ]] && MODIFIED_FILES+=("$file")
  done < <(git diff --name-only HEAD 2>/dev/null | grep -E '\.(py|sh|bash|ts|js|tsx|jsx|go|rs)$')
fi

# ---------- Batch syntax checks by type (reduce spawns) ----------
# Collect files by type first
PY_SYNTAX_FILES=(); SH_SYNTAX_FILES=(); RS_GREP_FILES=()

for file in "${MODIFIED_FILES[@]}"; do
  CHECKED=$((CHECKED + 1))
  basename="${file##*/}"
  ext="${basename##*.}"
  name="${basename%.*}"
  dir="${file%/*}"

  # --- Test file existence check (pure bash, no subprocess) ---
  has_test=false

  case "$ext" in
    py)
      for candidate in \
        "${dir}/test_${name}.py" \
        "${dir}/tests/test_${name}.py" \
        "${PROJECT_DIR}/test/unit/test_${name}.py" \
        "${PROJECT_DIR}/tests/test_${name}.py" \
        "${PROJECT_DIR}/test/test_${name}.py"; do
        [[ -f "$candidate" ]] && { has_test=true; break; }
      done
      PY_SYNTAX_FILES+=("$file")
      ;;
    sh|bash)
      for candidate in \
        "${PROJECT_DIR}/test/unit/test_${name}.bats" \
        "${PROJECT_DIR}/test/unit/${name}.bats" \
        "${PROJECT_DIR}/test/integration/test_${name}.bats" \
        "${PROJECT_DIR}/test/integration/${name}.bats"; do
        [[ -f "$candidate" ]] && { has_test=true; break; }
      done
      SH_SYNTAX_FILES+=("$file")
      ;;
    ts|tsx|js|jsx)
      for candidate in \
        "${dir}/${name}.test.${ext}" \
        "${dir}/${name}.spec.${ext}" \
        "${dir}/__tests__/${name}.test.${ext}" \
        "${dir}/__tests__/${name}.${ext}"; do
        [[ -f "$candidate" ]] && { has_test=true; break; }
      done
      ;;
    go)
      [[ -f "${dir}/${name}_test.go" ]] && has_test=true
      ;;
    rs)
      # Defer grep to batch below
      RS_GREP_FILES+=("$file")
      [[ -f "${dir}/tests/${name}.rs" ]] && has_test=true
      ;;
  esac

  if [[ "$has_test" == "false" ]]; then
    case "$file" in
      *test*|*spec*|*config*|*migration*|*__init__*|*setup*|*conftest*) ;;
      *) WARNINGS+=("No test file for: $file") ;;
    esac
  fi
done

# Batch Python syntax check: single python3 invocation for all .py files
if [[ ${#PY_SYNTAX_FILES[@]} -gt 0 ]]; then
  # Build a single Python script that checks all files
  _py_check_script='import ast, sys
for f in sys.argv[1:]:
    try:
        with open(f) as fh: ast.parse(fh.read(), filename=f)
    except SyntaxError as e:
        print(f"{f}:{e.lineno}: {e.msg}")
'
  py_errors=$(python3 -c "$_py_check_script" "${PY_SYNTAX_FILES[@]}" 2>/dev/null) || true
  if [[ -n "$py_errors" ]]; then
    while IFS= read -r err_line; do
      [[ -n "$err_line" ]] && WARNINGS+=("Syntax error in: $err_line")
    done <<< "$py_errors"
  fi
fi

# Batch shell syntax checks (single bash -n invocation for all shell files)
if [[ ${#SH_SYNTAX_FILES[@]} -gt 0 ]]; then
  sh_errors=$(bash -n "${SH_SYNTAX_FILES[@]}" 2>&1) || true
  if [[ -n "$sh_errors" ]]; then
    while IFS= read -r err_line; do
      [[ -n "$err_line" ]] && WARNINGS+=("Syntax error: $err_line")
    done <<< "$sh_errors"
  fi
fi

# Batch Rust #[cfg(test)] check: single grep across all .rs files
if [[ ${#RS_GREP_FILES[@]} -gt 0 ]]; then
  # grep -l returns filenames that match; those have inline tests
  _rs_with_tests=$(grep -l '#\[cfg(test)\]' "${RS_GREP_FILES[@]}" 2>/dev/null) || true
  # For any .rs file that already had has_test=true from dir check, skip.
  # For files found by grep, they have inline tests — remove from warnings.
  if [[ -n "$_rs_with_tests" ]]; then
    # Remove "No test file" warnings for files that have inline tests
    _new_warnings=()
    for w in "${WARNINGS[@]}"; do
      _skip=false
      while IFS= read -r _rs_file; do
        [[ "$w" == *"$_rs_file"* ]] && { _skip=true; break; }
      done <<< "$_rs_with_tests"
      [[ "$_skip" == "false" ]] && _new_warnings+=("$w")
    done
    WARNINGS=("${_new_warnings[@]}")
  fi
fi

# ---------- Report ----------
echo "Task Completion Quality Report"
echo "=============================="
echo "Files checked: $CHECKED"

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo ""
  echo "Warnings (${#WARNINGS[@]}):"
  for w in "${WARNINGS[@]}"; do
    echo "  $w"
  done
else
  echo "Status: All checks passed"
fi

# Touch task start marker for next task
touch "$TASK_START_MARKER" 2>/dev/null || true

# --- Cache write ---
_tc_output="Task Completion Quality Report
==============================
Files checked: $CHECKED"
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  _tc_output+=$'\n\n'"Warnings (${#WARNINGS[@]}):"
  for w in "${WARNINGS[@]}"; do
    _tc_output+=$'\n'"  $w"
  done
fi
[[ ${#WARNINGS[@]} -eq 0 ]] && _tc_output+=$'\n'"Status: All checks passed"
hook_cache_write "$_tc_cache_key" "0" "$_tc_output"
# Ultra-fast cache for next time
mkdir -p "$_CACHE_DIR" 2>/dev/null || true
echo "$_tc_output" > "$_CACHE_FILE" 2>/dev/null || true

exit 0
