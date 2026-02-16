#!/usr/bin/env bash
# test-phase4-patterns.sh
# Comprehensive test suite for Phase 4 advanced optimizations.
# Validates: extended globs, namerefs, associative arrays, process substitution.
# Usage: bash test-phase4-patterns.sh

set -euo pipefail

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Test counter
TEST_NUM=0

_test() {
  TEST_NUM=$((TEST_NUM + 1))
  local test_name="$1"
  local test_cmd="$2"
  local expected="$3"

  echo -n "Test $TEST_NUM: $test_name ... "

  local output
  if output=$(eval "$test_cmd" 2>&1); then
    if [[ "${output%$'\n'}" == "$expected" ]]; then
      echo -e "${GREEN}PASS${NC}"
      TESTS_PASSED=$((TESTS_PASSED + 1))
    else
      echo -e "${RED}FAIL${NC}"
      echo "  Expected: '$expected'"
      echo "  Got:      '${output%$'\n'}'"
      TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
  else
    echo -e "${RED}ERROR${NC}"
    echo "  Command failed: $test_cmd"
    echo "  Error: $output"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

_skip() {
  TEST_NUM=$((TEST_NUM + 1))
  local test_name="$1"
  local reason="$2"

  echo -e "Test $TEST_NUM: $test_name ... ${YELLOW}SKIP${NC} ($reason)"
  TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

echo -e "${BLUE}=== Phase 4 Advanced Optimizations Test Suite ===${NC}\n"

# ============================================================================
# Section 1: Extended Glob Tests (shopt -s extglob)
# ============================================================================

echo -e "${BLUE}Section 1: Extended Glob Pattern Tests${NC}"

_test "extglob @(a|b) matches a" \
  'bash -c "shopt -s extglob; [[ \"a\" == @(a|b) ]] && echo match || echo nomatch"' \
  "match"

_test "extglob @(a|b) matches b" \
  'bash -c "shopt -s extglob; [[ \"b\" == @(a|b) ]] && echo match || echo nomatch"' \
  "match"

_test "extglob @(a|b) rejects c" \
  'bash -c "shopt -s extglob; [[ \"c\" == @(a|b) ]] && echo match || echo nomatch"' \
  "nomatch"

_test "extglob @(py|rb|sh) case statement" \
  "bash << 'INNER'
shopt -s extglob
ext=py
case \$ext in
  @(py|rb|sh)) echo found;;
  *) echo not;;
esac
INNER" \
  "found"

_test "extglob +(a|b) matches one or more" \
  'bash -c "shopt -s extglob; [[ \"aab\" == +(a|b) ]] && echo match || echo nomatch"' \
  "match"

_test "extglob ?(a|b) matches zero or one" \
  'bash -c "shopt -s extglob; [[ \"a\" == ?(a|b) ]] && echo match || echo nomatch"' \
  "match"

_test "extglob ?(a|b) matches empty" \
  'bash -c "shopt -s extglob; [[ \"\" == ?(a|b) ]] && echo match || echo nomatch"' \
  "match"

# ============================================================================
# Section 2: Nameref Tests (Bash 4.3+)
# ============================================================================

echo -e "\n${BLUE}Section 2: Nameref Pattern Tests${NC}"

# Check Bash version
if (( ${BASH_VERSINFO[0]} < 4 || (${BASH_VERSINFO[0]} == 4 && ${BASH_VERSINFO[1]} < 3) )); then
  _skip "nameref basic reference" "Bash <4.3 (current: $BASH_VERSION)"
  _skip "nameref array append" "Bash <4.3"
  _skip "nameref array count" "Bash <4.3"
else
  _test "nameref basic reference" \
    'bash -c "
      func() {
        x=hello
        local -n ref=x
        echo \$ref
      }
      func
    "' \
    "hello"

  _test "nameref array append" \
    'bash -c "
      func() {
        declare -a arr=(a b)
        local -n ref=arr
        ref+=(c)
        echo \${arr[@]}
      }
      func
    "' \
    "a b c"

  _test "nameref array count" \
    'bash -c "
      func() {
        declare -a arr=(x y z)
        local -n ref=arr
        echo \${#ref[@]}
      }
      func
    "' \
    "3"

  _test "nameref function parameter" \
    'bash -c "
      func() {
        local -n items=\$1
        echo \${#items[@]}
      }
      declare -a myarr=(1 2 3 4)
      func myarr
    "' \
    "4"
fi

# ============================================================================
# Section 3: Associative Array Tests
# ============================================================================

echo -e "\n${BLUE}Section 3: Associative Array Dispatch Tests${NC}"

_test "assoc array basic lookup" \
  'bash -c "declare -A map=([py]=python [sh]=shell); echo \${map[py]}"' \
  "python"

_test "assoc array missing key returns empty" \
  'bash -c "declare -A map=([py]=python); [[ -z \${map[unknown]:-} ]] && echo empty || echo found"' \
  "empty"

_test "assoc array iteration" \
  'bash -c "
    declare -A types=([py]=python [js]=javascript)
    count=0
    for key in \"\${!types[@]}\"; do
      count=\$((count + 1))
    done
    echo \$count
  "' \
  "2"

_test "assoc array with defaults" \
  'bash -c "
    declare -A linters=([py]=ruff [rb]=rubocop)
    ext=unknown
    echo \${linters[\$ext]:-unknown-linter}
  "' \
  "unknown-linter"

# ============================================================================
# Section 4: File Type Classification Pattern Tests
# ============================================================================

echo -e "\n${BLUE}Section 4: File Type Classification Tests${NC}"

_test "classify Python file" \
  'bash -c "
    shopt -s extglob
    ext=\"py\"
    case \$ext in
      @(py|pyw|pyi)) echo python;;
      *) echo unknown;;
    esac
  "' \
  "python"

_test "classify TypeScript file" \
  'bash -c "
    shopt -s extglob
    ext=\"tsx\"
    case \$ext in
      @(ts|tsx|js|jsx)) echo typescript;;
      *) echo unknown;;
    esac
  "' \
  "typescript"

_test "classify Shell file" \
  'bash -c "
    shopt -s extglob
    ext=\"bash\"
    case \$ext in
      @(sh|bash)) echo shell;;
      *) echo unknown;;
    esac
  "' \
  "shell"

_test "classify CSS file" \
  'bash -c "
    shopt -s extglob
    ext=\"scss\"
    case \$ext in
      @(css|scss|less)) echo stylesheet;;
      *) echo unknown;;
    esac
  "' \
  "stylesheet"

_test "reject unknown extension" \
  'bash -c "
    shopt -s extglob
    ext=\"xyz\"
    case \$ext in
      @(py|sh|ts)) echo found;;
      *) echo unknown;;
    esac
  "' \
  "unknown"

# ============================================================================
# Section 5: Library Import Tests
# ============================================================================

echo -e "\n${BLUE}Section 5: Library Import Tests${NC}"

# Test that dispatch-patterns.sh can be sourced without errors
_test "dispatch-patterns.sh sourcing" \
  'bash -c "source hooks/lib/dispatch-patterns.sh && echo loaded"' \
  "loaded"

# Test that FILE_TYPE_MAP is available
_test "FILE_TYPE_MAP availability after import" \
  'bash -c "
    source hooks/lib/dispatch-patterns.sh
    echo \${FILE_TYPE_MAP[py]:-}
  "' \
  "python"

# ============================================================================
# Section 6: Performance Comparison Tests
# ============================================================================

echo -e "\n${BLUE}Section 6: Performance Baseline Tests${NC}"

_test "extended glob case statement compiles" \
  'bash -c "
    shopt -s extglob
    case test in
      @(foo|bar|baz)) echo fail;;
      *) echo ok;;
    esac
  "' \
  "ok"

_test "nameref in loop works correctly" \
  'bash -c "
    func() {
      if (( \${BASH_VERSINFO[0]} >= 4 && \${BASH_VERSINFO[1]} >= 3 )); then
        declare -a items=(a b c)
        local -n ref=items
        count=0
        for item in \"\${ref[@]}\"; do
          count=\$((count + 1))
        done
        echo \$count
      else
        echo 0
      fi
    }
    func
  "' \
  "3"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"
echo -e "Total:   $((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
  echo -e "\n${GREEN}All tests passed!${NC}"
  exit 0
else
  echo -e "\n${RED}$TESTS_FAILED test(s) failed!${NC}"
  exit 1
fi
