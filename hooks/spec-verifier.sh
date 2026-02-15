#!/usr/bin/env bash
# spec-verifier.sh — PostToolUse hook (Edit|Write) + Stop hook
# Verifies FR traceability and spec compliance. Checks that test files have FR
# tags, that source @trace annotations reference valid FRs, and reports coverage.
# Advisory only (always exits 0). Budget: <1s.
#
# Optimized: single recursive grep + comm/sort set ops + printf JSON (no jq in hot path).
# Subprocess budget: ~5-7 total (was 300+).
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh (Stop mode only) ---
# When FILE_PATH is not set, this is a Stop invocation
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -z "${FILE_PATH:-}" ]]; then
  _CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
  _CACHE_KEY="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
  _CACHE_FILE="${_CACHE_DIR}/spec-verifier-${_CACHE_KEY}.result"
  if [[ -f "$_CACHE_FILE" ]]; then
    _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
    if (( _age < _CACHE_TTL )); then
      cat "$_CACHE_FILE"
      exit 0
    fi
  fi
fi

HOOK_NAME="SPEC-VERIFIER"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Stderr message on unexpected failure (set -e)
trap 'echo "SPEC-VERIFIER FAIL: unexpected error at line $LINENO" >&2' ERR

# --- P1 optimization: Skip in Stop mode if no FR/test files changed ---
# Only run if FR files or test files were modified (spec verification relevant)
if [[ -z "${FILE_PATH:-}" ]] && ! hook_should_run "check" '(FUNCTIONAL_REQUIREMENTS|test|spec|.*_test|.*\.test\.)'; then
  echo "SPEC-VERIFIER: skipped (no FR or test files changed)"
  exit 0
fi

RESULTS_FILE="$HOME/.claude/.spec-verification.json"

mkdir -p "$HOME/.claude"

# Excluded directories for all recursive searches
EXCLUDE_DIRS="--exclude-dir=node_modules --exclude-dir=vendor --exclude-dir=.git --exclude-dir=target --exclude-dir=out --exclude-dir=dist --exclude-dir=build --exclude-dir=coverage --exclude-dir=__pycache__ --exclude-dir=.process-compose"
# rg globs equivalent (for ripgrep)
RG_GLOBS=(-g '!node_modules' -g '!vendor' -g '!.git' -g '!target' -g '!out' -g '!dist' -g '!build' -g '!coverage' -g '!__pycache__' -g '!.process-compose')
# Prefer rg over grep -r
_RG_CMD=$(command -v rg 2>/dev/null || true)

# Find FUNCTIONAL_REQUIREMENTS.md
FR_FILE="$PROJECT_DIR/FUNCTIONAL_REQUIREMENTS.md"
if [[ ! -f "$FR_FILE" ]]; then
  # Search up to 3 parent directories
  local_dir="$PROJECT_DIR"
  for _ in 1 2 3; do
    local_dir=$(dirname "$local_dir")
    if [[ -f "$local_dir/FUNCTIONAL_REQUIREMENTS.md" ]]; then
      FR_FILE="$local_dir/FUNCTIONAL_REQUIREMENTS.md"
      break
    fi
  done
fi
[[ ! -f "$FR_FILE" ]] && exit 0

# ---------- Mode detection ----------
# If no FILE_PATH, this is a Stop-event invocation: do full scan
# If FILE_PATH is set, this is a PostToolUse invocation: check single file
MODE="single"
[[ -z "$FILE_PATH" ]] && MODE="full"

# ---------- Helpers ----------
# Extract all valid FR IDs from the spec (1 grep/rg + 1 sort subprocess)
if [[ -n "$_RG_CMD" ]]; then
  SPEC_FRS=$("$_RG_CMD" -oN --no-filename 'FR-[A-Z]+-[0-9]+' "$FR_FILE" 2>/dev/null | sort_unique)
else
  SPEC_FRS=$(grep -oE 'FR-[A-Z]+-[0-9]+' "$FR_FILE" 2>/dev/null | sort_unique)
fi
SPEC_COUNT=0
if [[ -n "$SPEC_FRS" ]]; then
  # Count lines with bash builtin — zero subprocesses
  while IFS= read -r _; do
    SPEC_COUNT=$((SPEC_COUNT + 1))
  done <<< "$SPEC_FRS"
fi

# Locate test directories (pure bash, no subprocesses)
find_test_dirs() {
  local dirs=()
  [[ -d "$PROJECT_DIR/test" ]] && dirs+=("$PROJECT_DIR/test")
  [[ -d "$PROJECT_DIR/tests" ]] && dirs+=("$PROJECT_DIR/tests")
  [[ -d "$PROJECT_DIR/__tests__" ]] && dirs+=("$PROJECT_DIR/__tests__")
  [[ -d "$PROJECT_DIR/spec" ]] && dirs+=("$PROJECT_DIR/spec")
  echo "${dirs[*]}"
}

# ---------- Single file mode ----------
if [[ "$MODE" == "single" ]]; then
  [[ ! -f "$FILE_PATH" ]] && exit 0

  BASENAME="${FILE_PATH##*/}"
  EXT="${BASENAME##*.}"
  FINDINGS=()

  # Determine file role
  IS_TEST=false
  IS_SOURCE=false
  IS_SPEC=false

  case "$BASENAME" in
    test_*|*_test.*|*.test.*|*.spec.*|*.bats) IS_TEST=true ;;
  esac
  case "$FILE_PATH" in
    */test/*|*/tests/*|*/__tests__/*|*/spec/*) IS_TEST=true ;;
  esac
  case "$BASENAME" in
    FUNCTIONAL_REQUIREMENTS*|PRD*|ADR*|PLAN*|USER_JOURNEYS*) IS_SPEC=true ;;
  esac
  if [[ "$IS_TEST" == "false" ]] && [[ "$IS_SPEC" == "false" ]]; then
    case "$EXT" in
      py|sh|bash|ts|tsx|js|jsx|go|rs|rb|php|java|kt|swift|ex|hs|lua|pl|dart|bats) IS_SOURCE=true ;;
    esac
  fi

  # Skip non-relevant files
  [[ "$IS_TEST" == "false" ]] && [[ "$IS_SOURCE" == "false" ]] && [[ "$IS_SPEC" == "false" ]] && exit 0

  # Check 1: Test files must have FR tags (-m 1: stop after first match)
  if [[ "$IS_TEST" == "true" ]]; then
    if ! grep -m 1 -qE 'FR-[A-Z]+-[0-9]+' "$FILE_PATH" 2>/dev/null; then
      FINDINGS+=("TRACEABILITY: Test file '${BASENAME}' has no FR reference tag (e.g., @trace FR-XXX-NNN)")
      emit_feedback "suggestion" "spec-verification" "Test file '${BASENAME}' has no FR reference tag" "SPEC-MISSING-TAG" "Add an @trace FR-XXX-NNN tag to this test file to link it to a functional requirement."
    fi
  fi

  # Check 2: Source @trace annotations should reference valid FRs
  if [[ "$IS_SOURCE" == "true" ]]; then
    SOURCE_FRS=$(grep -oE 'FR-[A-Z]+-[0-9]+' "$FILE_PATH" 2>/dev/null | sort -u || true)
    if [[ -n "$SOURCE_FRS" ]]; then
      # Use comm for set difference instead of per-FR grep loop
      INVALID_FRS=$(comm -23 <(echo "$SOURCE_FRS") <(echo "$SPEC_FRS") 2>/dev/null || true)
      if [[ -n "$INVALID_FRS" ]]; then
        while IFS= read -r fr_id; do
          [[ -z "$fr_id" ]] && continue
          FINDINGS+=("INVALID FR: '${BASENAME}' references '${fr_id}' which is not in FUNCTIONAL_REQUIREMENTS.md")
          emit_feedback "warning" "spec-verification" "'${BASENAME}' references invalid FR: ${fr_id}" "SPEC-INVALID-FR" "Check FUNCTIONAL_REQUIREMENTS.md for valid FR IDs and correct the reference in '${BASENAME}'."
        done <<< "$INVALID_FRS"
      fi
    fi
  fi

  # Check 3: If FR spec is edited, look for orphaned test references
  if [[ "$IS_SPEC" == "true" ]] && [[ "$BASENAME" == "FUNCTIONAL_REQUIREMENTS"* ]]; then
    TEST_DIRS=$(find_test_dirs)
    if [[ -n "$TEST_DIRS" ]]; then
      # Try pre-built index for orphan check
      _fr_index_file="${HOOK_SHARED_DIR:-/tmp/claude-hook-shared-$$}/fr_index"
      if [[ -f "$_fr_index_file" ]]; then
        TEST_FRS=$(awk -F: '{print $NF}' "$_fr_index_file" | sort_unique || true)
      else
        # Single recursive search for all test FR references
        # shellcheck disable=SC2086
        if [[ -n "$_RG_CMD" ]]; then
          TEST_FRS=$("$_RG_CMD" -oN --no-filename "${RG_GLOBS[@]}" 'FR-[A-Z]+-[0-9]+' $TEST_DIRS 2>/dev/null | sort_unique || true)
        else
          TEST_FRS=$(grep -rohE $EXCLUDE_DIRS 'FR-[A-Z]+-[0-9]+' $TEST_DIRS 2>/dev/null | sort_unique || true)
        fi
      fi
      if [[ -n "$TEST_FRS" ]]; then
        # Use comm: FRs in tests but not in spec = orphaned
        ORPHANED_FRS=$(comm -23 <(echo "$TEST_FRS") <(echo "$SPEC_FRS") 2>/dev/null || true)
        if [[ -n "$ORPHANED_FRS" ]]; then
          while IFS= read -r test_fr; do
            [[ -z "$test_fr" ]] && continue
            FINDINGS+=("ORPHANED TEST: Tests reference '${test_fr}' but it no longer exists in FUNCTIONAL_REQUIREMENTS.md")
            emit_feedback "warning" "spec-verification" "Tests reference orphaned FR: ${test_fr}" "SPEC-ORPHANED-TEST" "Remove the reference to '${test_fr}' or update the spec to include it."
          done <<< "$ORPHANED_FRS"
        fi
      fi
    fi
  fi

  # Write verification result using printf JSON (no jq)
  FILE_ROLE="source"
  [[ "$IS_TEST" == "true" ]] && FILE_ROLE="test"
  [[ "$IS_SPEC" == "true" ]] && FILE_ROLE="spec"

  FINDING_COUNT=${#FINDINGS[@]}
  FINDINGS_JSON="[]"
  if [[ $FINDING_COUNT -gt 0 ]]; then
    local_items=""
    for f in "${FINDINGS[@]}"; do
      local_esc="$(_json_escape "$f")"
      if [[ -z "$local_items" ]]; then
        local_items="\"$local_esc\""
      else
        local_items="$local_items,\"$local_esc\""
      fi
    done
    FINDINGS_JSON="[$local_items]"
  fi

  printf '{"mode":"single","timestamp":"%s","trigger_file":"%s","file_role":"%s","finding_count":%d,"findings":%s,"total_frs":%d}\n' \
    "$(_json_escape "$now")" \
    "$(_json_escape "$FILE_PATH")" \
    "$FILE_ROLE" \
    "$FINDING_COUNT" \
    "$FINDINGS_JSON" \
    "$SPEC_COUNT" > "$RESULTS_FILE"

  # Output findings
  if [[ $FINDING_COUNT -gt 0 ]]; then
    echo "Spec Verification (${FINDING_COUNT} finding(s)):"
    for f in "${FINDINGS[@]}"; do
      echo "  $f"
    done
  fi

  exit 0
fi

# ---------- Full scan mode (Stop event) ----------
# Strategy: single recursive grep -rHoE to get file:FR pairs, then
# use awk to compute covered FRs and identify orphan test files.
# This replaces find + 316 per-file greps with 1 find + 1 grep.

# Cache check — skip full scan if unchanged since last run
_spec_cache_key="${HOOK_NAME}_${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}_$(hook_file_hash_cache "$FR_FILE" 2>/dev/null || echo none)"
if hook_cache_check "$_spec_cache_key" 120; then
  hook_cache_read "$_spec_cache_key"
  exit $?
fi

_spec_full_scan() {

TEST_DIRS=$(find_test_dirs)

# Collect all test files (1 find subprocess)
TEST_FILE_LIST=""
if [[ -n "$TEST_DIRS" ]]; then
  # shellcheck disable=SC2086
  TEST_FILE_LIST=$(find $TEST_DIRS \
    \( -name "node_modules" -o -name "vendor" -o -name ".git" -o -name "target" \
       -o -name "out" -o -name "dist" -o -name "build" -o -name "coverage" \
       -o -name "__pycache__" -o -name ".process-compose" \) -prune -o \
    \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.test.js" \
       -o -name "*.test.tsx" -o -name "*.test.jsx" -o -name "*.spec.ts" -o -name "*.spec.js" \
       -o -name "*.bats" -o -name "*_test.go" -o -name "*Test.java" \) -print 2>/dev/null) || true
fi

[[ -z "$TEST_FILE_LIST" ]] && {
  # No test files: all FRs uncovered, no orphans
  COVERED_COUNT=0
  UNCOVERED_COUNT=$SPEC_COUNT
  ORPHAN_COUNT=0
  COVERAGE_PCT=0
  VERDICT="GAPS_FOUND"
  [[ "$SPEC_COUNT" -eq 0 ]] && VERDICT="VERIFIED"

  printf '{"mode":"full","timestamp":"%s","total_frs":%d,"covered_frs":0,"uncovered_frs":%d,"orphan_tests":0,"coverage_pct":0,"uncovered_list":[],"orphan_list":[],"verdict":"%s"}\n' \
    "$(_json_escape "$now")" "$SPEC_COUNT" "$UNCOVERED_COUNT" "$VERDICT" > "$RESULTS_FILE"

  if [[ "$VERDICT" != "VERIFIED" ]] && [[ -n "$SPEC_FRS" ]]; then
    echo "Spec Verification FAIL: FRs=$SPEC_COUNT Gaps=$UNCOVERED_COUNT (no coverage)"
  else
    echo "Spec: ok"
  fi
  return 0
}

# Single recursive search across all test dirs for FR references (1 rg/grep subprocess).
# Output: file:FR-XXX-NNN pairs. We also need the test file list to find orphans.
# Try pre-built FR index first (populated by speculative-stop-prewarmer)
_fr_index_file="${HOOK_SHARED_DIR:-/tmp/claude-hook-shared-$$}/fr_index"
if [[ -f "$_fr_index_file" ]]; then
  FR_MATCHES=$(cat "$_fr_index_file")
else
  # shellcheck disable=SC2086
  if [[ -n "$_RG_CMD" ]]; then
    FR_MATCHES=$("$_RG_CMD" -oN --no-heading "${RG_GLOBS[@]}" 'FR-[A-Z]+-[0-9]+' $TEST_DIRS 2>/dev/null || true)
  else
    FR_MATCHES=$(grep -rHoE $EXCLUDE_DIRS 'FR-[A-Z]+-[0-9]+' $TEST_DIRS 2>/dev/null || true)
  fi
fi

# Use awk to process grep output: build sets of covered FRs and files-with-FRs.
# Input 1 (FR_MATCHES): "filepath:FR-XXX-NNN" lines
# Input 2 (TEST_FILE_LIST): one filepath per line
# Output: covered FRs ||| orphan test files
AWK_RESULT=$(awk '
BEGIN { OFS="\t" }
NR==FNR {
  # Phase 1: grep output (file:FR-XXX-NNN pairs)
  # FR ID is always the last colon-separated field; file path is everything before
  n = split($0, parts, ":")
  if (n >= 2) {
    fr = parts[n]
    # Reconstruct file path (handles paths with colons)
    file = parts[1]
    for (i = 2; i < n; i++) file = file ":" parts[i]
    covered_frs[fr] = 1
    files_with_fr[file] = 1
  }
  next
}
{
  # Phase 2: test file list
  file = $0
  if (file != "" && !(file in files_with_fr)) {
    orphans[file] = 1
  }
}
END {
  # Output covered FRs
  n = 0
  for (fr in covered_frs) {
    if (n++ > 0) printf "\n"
    printf "%s", fr
  }
  printf "|||"
  # Output orphan test files
  n = 0
  for (f in orphans) {
    if (n++ > 0) printf "\n"
    printf "%s", f
  }
}
' <(echo "$FR_MATCHES") <(echo "$TEST_FILE_LIST"))

# Split awk output
COVERED_FR_LIST="${AWK_RESULT%%|||*}"
ORPHAN_TEST_LIST="${AWK_RESULT#*|||}"

# Sort covered FRs for comm
COVERED_FR_SORTED=""
if [[ -n "$COVERED_FR_LIST" ]]; then
  COVERED_FR_SORTED=$(echo "$COVERED_FR_LIST" | sort -u)
fi

# Use comm for set operations (1 comm subprocess each)
if [[ -n "$COVERED_FR_SORTED" ]]; then
  UNCOVERED_FR_LIST=$(comm -23 <(echo "$SPEC_FRS") <(echo "$COVERED_FR_SORTED"))
  ACTUALLY_COVERED=$(comm -12 <(echo "$SPEC_FRS") <(echo "$COVERED_FR_SORTED"))
else
  UNCOVERED_FR_LIST="$SPEC_FRS"
  ACTUALLY_COVERED=""
fi

# Count with bash builtins (zero subprocesses)
COVERED_COUNT=0
if [[ -n "$ACTUALLY_COVERED" ]]; then
  while IFS= read -r _; do
    COVERED_COUNT=$((COVERED_COUNT + 1))
  done <<< "$ACTUALLY_COVERED"
fi

UNCOVERED_COUNT=$((SPEC_COUNT - COVERED_COUNT))

ORPHAN_COUNT=0
if [[ -n "$ORPHAN_TEST_LIST" ]]; then
  while IFS= read -r _; do
    ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
  done <<< "$ORPHAN_TEST_LIST"
fi

COVERAGE_PCT=0
if [[ "$SPEC_COUNT" -gt 0 ]]; then
  COVERAGE_PCT=$((COVERED_COUNT * 100 / SPEC_COUNT))
fi

VERDICT="GAPS_FOUND"
[[ "$UNCOVERED_COUNT" -eq 0 ]] && [[ "$ORPHAN_COUNT" -eq 0 ]] && VERDICT="VERIFIED"

# Build JSON with printf (no jq)
UNCOVERED_JSON="[]"
if [[ -n "$UNCOVERED_FR_LIST" ]]; then
  local_items=""
  while IFS= read -r fr; do
    [[ -z "$fr" ]] && continue
    local_esc="$(_json_escape "$fr")"
    if [[ -z "$local_items" ]]; then
      local_items="\"$local_esc\""
    else
      local_items="$local_items,\"$local_esc\""
    fi
  done <<< "$UNCOVERED_FR_LIST"
  [[ -n "$local_items" ]] && UNCOVERED_JSON="[$local_items]"
fi

ORPHAN_JSON="[]"
if [[ -n "$ORPHAN_TEST_LIST" ]]; then
  local_items=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    local_esc="$(_json_escape "$f")"
    if [[ -z "$local_items" ]]; then
      local_items="\"$local_esc\""
    else
      local_items="$local_items,\"$local_esc\""
    fi
  done <<< "$ORPHAN_TEST_LIST"
  [[ -n "$local_items" ]] && ORPHAN_JSON="[$local_items]"
fi

printf '{"mode":"full","timestamp":"%s","total_frs":%d,"covered_frs":%d,"uncovered_frs":%d,"orphan_tests":%d,"coverage_pct":%d,"uncovered_list":%s,"orphan_list":%s,"verdict":"%s"}\n' \
  "$(_json_escape "$now")" \
  "$SPEC_COUNT" \
  "$COVERED_COUNT" \
  "$UNCOVERED_COUNT" \
  "$ORPHAN_COUNT" \
  "$COVERAGE_PCT" \
  "$UNCOVERED_JSON" \
  "$ORPHAN_JSON" \
  "$VERDICT" > "$RESULTS_FILE"

  # Print report
  echo ""
  # Print report — only verbose on fails
  if [[ "$VERDICT" != "VERIFIED" ]]; then
    echo "Spec Verification FAIL: FRs=$SPEC_COUNT Covered=$COVERED_COUNT ($COVERAGE_PCT%) Gaps=$UNCOVERED_COUNT Orphans=$ORPHAN_COUNT"
    if [[ -n "$UNCOVERED_FR_LIST" ]]; then
      echo "Uncovered FRs:"
      echo "$UNCOVERED_FR_LIST" | while IFS= read -r fr; do [[ -n "$fr" ]] && echo "  - $fr"; done
    fi
    if [[ -n "$ORPHAN_TEST_LIST" ]]; then
      echo "Orphan tests:"
      echo "$ORPHAN_TEST_LIST" | while IFS= read -r f; do [[ -n "$f" ]] && echo "  - $f"; done
    fi
  else
    echo "Spec: ok"
  fi

} # end _spec_full_scan

# Run main, capture output, cache result
_output=$(_spec_full_scan 2>&1); _rc=$?
hook_cache_write "$_spec_cache_key" "$_rc" "$_output"
# Ultra-fast cache for next time (only in Stop mode)
if [[ -n "${_CACHE_DIR:-}" ]]; then
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  echo "$_output" > "$_CACHE_FILE" 2>/dev/null || true
fi
[[ -n "$_output" ]] && echo "$_output"
exit "$_rc"
