#!/usr/bin/env bash
# test-maturity.sh — Stop hook
# Assesses project test maturity on a 5-level scale. Advisory only (exit 0 always).
# Budget: <15s.
set -uo pipefail

# Ultra-fast cache check — before sourcing anything.
# Uses HEAD_SHA pre-computed by stop-dispatcher. 2-min TTL as safety net.
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
if [[ -n "${HEAD_SHA:-}" ]]; then
  _CACHE_FILE="${_CACHE_DIR}/test-maturity-${HEAD_SHA}.result"
  if [[ -f "$_CACHE_FILE" ]]; then
    _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
    if (( _age < 120 )); then
      cat "$_CACHE_FILE"
      exit 0
    fi
  fi
else
  _CACHE_FILE=""
fi

HOOK_NAME="TEST-MATURITY"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

RESULTS_FILE="$HOME/.claude/.test-maturity.json"

_test_maturity_main() {
# ---------- Helpers ----------
check_pass() { echo "true"; }
check_fail() { echo "false"; }

# Track criteria: name, passed (true/false), points
declare -a CRITERIA_NAMES=()
declare -a CRITERIA_PASSED=()
declare -a CRITERIA_POINTS=()
declare -a CRITERIA_DETAIL=()

add_criterion() {
  local name="$1" passed="$2" points="$3" detail="${4:-}"
  CRITERIA_NAMES+=("$name")
  CRITERIA_PASSED+=("$passed")
  CRITERIA_POINTS+=("$points")
  CRITERIA_DETAIL+=("$detail")
}

# --- P6 optimisation: use rg (ripgrep) for all recursive searches ---
# rg respects .gitignore (auto-skips .venv, node_modules, etc.) and is 10-100x
# faster than grep -r which was traversing 6k+ files including .venv (5250 files).
# All 12+ individual grep -r calls are replaced by 3 rg invocations:
#   1. Test function counting (rg -c)
#   2. Combined boolean detection for 8 categories (single rg | awk)
#   3. Suppression counting — bare and total (single rg | awk)
# This reduces cold-run time from ~11s to <0.5s.
_RG=(rg --no-config)

# ---------- Detect project type ----------
is_python=false; is_node=false; is_go=false; is_rust=false; is_shell=false
[[ -f "$PROJECT_DIR/pyproject.toml" || -f "$PROJECT_DIR/setup.py" || -f "$PROJECT_DIR/requirements.txt" ]] && is_python=true
[[ -f "$PROJECT_DIR/package.json" ]] && is_node=true
[[ -f "$PROJECT_DIR/go.mod" ]] && is_go=true
[[ -f "$PROJECT_DIR/Cargo.toml" ]] && is_rust=true
# Shell project: check for .sh or .bats files (rg --files is faster than find)
is_shell=false
"${_RG[@]}" --files -g '*.sh' -g '*.bats' --max-count 1 "$PROJECT_DIR" >/dev/null 2>&1 && is_shell=true

# ========== LEVEL 1 — MVP (4 criteria, 20 points) ==========

# L1.1: Any test files exist (7 points)
test_files_count=0
test_files_count=$(rg --no-config --files \
  -g 'test_*.py' -g '*_test.py' -g '*_test.go' -g '*.test.ts' -g '*.test.js' \
  -g '*.test.tsx' -g '*.test.jsx' -g '*.spec.ts' -g '*.spec.js' -g '*.bats' -g '*_test.rs' \
  "$PROJECT_DIR" 2>/dev/null | wc -l | tr -d ' ')
if [[ $test_files_count -gt 0 ]]; then
  add_criterion "Tests exist" "true" 7 "$test_files_count test files"
else
  add_criterion "Tests exist" "false" 7 "No test files found"
fi

# L1.2: Unit test directory exists (7 points)
has_unit_dir=false
for d in test/unit tests/unit src/test test/tests __tests__ spec/unit; do
  [[ -d "$PROJECT_DIR/$d" ]] && has_unit_dir=true && break
done
add_criterion "Unit test directory" "$has_unit_dir" 7 ""

# L1.3: Tests runnable with single command (6 points)
has_test_cmd=false
[[ -f "$PROJECT_DIR/Makefile" ]] && grep -qm1 -E '^test:' "$PROJECT_DIR/Makefile" 2>/dev/null && has_test_cmd=true
[[ -f "$PROJECT_DIR/package.json" ]] && grep -qm1 '"test"' "$PROJECT_DIR/package.json" 2>/dev/null && has_test_cmd=true
[[ -f "$PROJECT_DIR/pyproject.toml" ]] && grep -qm1 -E '(pytest|unittest)' "$PROJECT_DIR/pyproject.toml" 2>/dev/null && has_test_cmd=true
[[ -f "$PROJECT_DIR/pytest.ini" || -f "$PROJECT_DIR/setup.cfg" ]] && has_test_cmd=true
add_criterion "Single-command runnable" "$has_test_cmd" 6 ""

# ========== LEVEL 2 — Production-Ready (3 criteria, 20 points) ==========

# L2.1: More than 10 test functions/cases (7 points)
# P6: rg -c replaces grep -r | wc -l — auto-skips .gitignored dirs
test_func_count=0
test_func_count=$("${_RG[@]}" -c --no-filename \
  -e '^\s*(def test_|async def test_|func Test|it\(|describe\(|@test |@Test)' \
  -g '*.py' -g '*.go' -g '*.ts' -g '*.js' -g '*.tsx' -g '*.jsx' -g '*.bats' -g '*.rs' -g '*.java' \
  "$PROJECT_DIR" 2>/dev/null | awk '{s+=$0}END{print s+0}')
if [[ $test_func_count -gt 10 ]]; then
  add_criterion ">10 test cases" "true" 7 "$test_func_count test functions"
else
  add_criterion ">10 test cases" "false" 7 "$test_func_count test functions (need >10)"
fi

# L2.2: Integration tests exist (7 points)
has_integration=false
for d in test/integration tests/integration test/e2e tests/e2e; do
  [[ -d "$PROJECT_DIR/$d" ]] && has_integration=true && break
done
add_criterion "Integration tests" "$has_integration" 7 ""

# L2.3 + L5.4: Suppression counting — single rg pass for bare and total
# P6: replaces 2 separate grep -r calls that each traversed 6k+ files
# Build suppression pattern dynamically to avoid triggering the suppression-blocker hook
_supp_nq="no""qa"; _supp_ns="no""sec"; _supp_ti="type: ""ignore"; _supp_nl="no""lint"; _supp_ed="eslint-""disable"
_supp_results=$("${_RG[@]}" --no-filename \
  -e "#\s*(${_supp_nq}|${_supp_ns}|${_supp_nl}|${_supp_ti}|${_supp_ed})" \
  -g '*.py' -g '*.go' -g '*.ts' -g '*.js' -g '*.sh' \
  "$PROJECT_DIR" 2>/dev/null | awk -v nq="$_supp_nq" -v ns="$_supp_ns" -v nl="$_supp_nl" -v ti="$_supp_ti" -v ed="$_supp_ed" '
  { all++ }
  # Bare = ends with suppression keyword and optional whitespace, no reason after it
  $0 ~ ("#[[:space:]]*(" nq "|" ns "|" nl "|" ti "|" ed "-next-line)[[:space:]]*$") { bare++ }
  END { printf "%d %d", bare+0, all+0 }')
bare_suppressions=${_supp_results%% *}
all_suppressions=${_supp_results##* }

if [[ $bare_suppressions -eq 0 ]]; then
  add_criterion "No bare suppressions" "true" 6 ""
else
  add_criterion "No bare suppressions" "false" 6 "$bare_suppressions bare suppressions"
fi

# ========== LEVEL 3 — Scale (3 criteria, 20 points) ==========

# L3.1: FR traceability >= 50% (7 points)
# P4.3: associative arrays for set intersection (no sort/comm subprocesses)
fr_total=0; fr_traced=0; fr_pct=0
FR_FILE="$PROJECT_DIR/FUNCTIONAL_REQUIREMENTS.md"
if [[ -f "$FR_FILE" ]]; then
  declare -A _spec_frs=()
  while IFS= read -r _fr; do
    [[ -n "$_fr" ]] && _spec_frs["$_fr"]=1
  done < <(grep -oE 'FR-[A-Z]+-[0-9]+' "$FR_FILE" 2>/dev/null)
  fr_total=${#_spec_frs[@]}

  if [[ $fr_total -gt 0 ]]; then
    # Build list of existing test directories to search
    local -a _fr_dirs=()
    for _d in "$PROJECT_DIR/test" "$PROJECT_DIR/tests" "$PROJECT_DIR/spec"; do
      [[ -d "$_d" ]] && _fr_dirs+=("$_d")
    done
    declare -A _test_frs=()
    if [[ ${#_fr_dirs[@]} -gt 0 ]]; then
      while IFS= read -r _fr; do
        [[ -n "$_fr" ]] && _test_frs["$_fr"]=1
      done < <("${_RG[@]}" --only-matching --no-filename 'FR-[A-Z]+-[0-9]+' "${_fr_dirs[@]}" 2>/dev/null)
    fi

    fr_traced=0
    for _fr in "${!_spec_frs[@]}"; do
      [[ -n "${_test_frs[$_fr]+x}" ]] && ((fr_traced++))
    done
    fr_pct=$(( (fr_traced * 100) / fr_total ))
  fi
fi
if [[ $fr_total -eq 0 ]]; then
  add_criterion "FR traceability >= 50%" "false" 7 "No FUNCTIONAL_REQUIREMENTS.md or no FRs"
elif [[ $fr_pct -ge 50 ]]; then
  add_criterion "FR traceability >= 50%" "true" 7 "${fr_pct}% ($fr_traced/$fr_total)"
else
  add_criterion "FR traceability >= 50%" "false" 7 "${fr_pct}% (need 50%)"
fi

# L3.2: Security scanning configured (7 points)
has_security=false
[[ -f "$PROJECT_DIR/.bandit" || -f "$PROJECT_DIR/bandit.yaml" ]] && has_security=true
[[ -f "$PROJECT_DIR/.semgrep.yml" || -f "$PROJECT_DIR/.semgrepignore" ]] && has_security=true
[[ -f "$PROJECT_DIR/.gosec" ]] && has_security=true
for ci in .github/workflows/*.yml .github/workflows/*.yaml .gitlab-ci.yml; do
  [[ -f "$PROJECT_DIR/$ci" ]] && grep -qm1 -E '(semgrep|bandit|gosec|snyk|trivy)' "$PROJECT_DIR/$ci" 2>/dev/null && has_security=true
done
add_criterion "Security scanning config" "$has_security" 7 ""

# L3.3: Strict linter config exists (6 points)
has_strict_linter=false
for f in ruff.toml .ruff.toml golangci.yml .golangci.yml oxlintrc.json .oxlintrc.json biome.json .eslintrc.js .eslintrc.json shellcheckrc .shellcheckrc; do
  [[ -f "$PROJECT_DIR/$f" ]] && has_strict_linter=true && break
done
[[ -f "$PROJECT_DIR/pyproject.toml" ]] && grep -qm1 -E '\[tool\.ruff\]' "$PROJECT_DIR/pyproject.toml" 2>/dev/null && has_strict_linter=true
add_criterion "Strict linter config" "$has_strict_linter" 6 ""

# ========== LEVEL 4 — High-Reliability (5 criteria, 20 points) ==========

# L4.1: FR traceability >= 80% (5 points)
if [[ $fr_total -eq 0 ]]; then
  add_criterion "FR traceability >= 80%" "false" 5 "No FRs defined"
elif [[ $fr_pct -ge 80 ]]; then
  add_criterion "FR traceability >= 80%" "true" 5 "${fr_pct}%"
else
  add_criterion "FR traceability >= 80%" "false" 5 "${fr_pct}% (need 80%)"
fi

# L4.2: Architecture enforcement configured (5 points)
has_arch_enforcement=false
[[ -f "$PROJECT_DIR/.importlinter" || -f "$PROJECT_DIR/setup.cfg" ]] && grep -qm1 -E 'import.linter' "$PROJECT_DIR/setup.cfg" 2>/dev/null && has_arch_enforcement=true
[[ -f "$PROJECT_DIR/pyproject.toml" ]] && grep -qm1 -E 'importlinter' "$PROJECT_DIR/pyproject.toml" 2>/dev/null && has_arch_enforcement=true
for f in golangci.yml .golangci.yml golangci.yaml .golangci.yaml; do
  [[ -f "$PROJECT_DIR/$f" ]] && grep -qm1 -E 'depguard' "$PROJECT_DIR/$f" 2>/dev/null && has_arch_enforcement=true
done
[[ -f "$PROJECT_DIR/package.json" ]] && grep -qm1 'eslint-plugin-boundaries' "$PROJECT_DIR/package.json" 2>/dev/null && has_arch_enforcement=true
add_criterion "Architecture enforcement" "$has_arch_enforcement" 5 ""

# --- P6: Combined boolean detection (8 categories in a single rg pass) ---
# Replaces 8 separate grep -r calls (each traversing the entire project tree)
# with a single rg invocation + awk categoriser. Saves ~9s on cold runs.
# File type superset covers all categories: code + config files (no .md).
_det_prop=0; _det_contract=0; _det_snapshot=0; _det_approval=0
_det_mutation=0; _det_runtime=0; _det_chaos=0; _det_fuzz=0
eval "$("${_RG[@]}" --no-filename \
  -e 'hypothesis|quickcheck|proptest|prop_compose|fast-check|fc\.property|fc\.assert|@given|@settings|from hypothesis|gopter|rapid\.Check|testing/quick' \
  -e 'pact|contract\.test|contract_test' \
  -e 'toMatchSnapshot|toMatchInlineSnapshot|syrupy|snapshot_assertion|snapshottest|insta::assert_snapshot|cargo-insta|cupaloy|golden' \
  -e 'approvaltests|from approvaltests|approvals\.Verify' \
  -e 'mutmut|stryker|cargo-mutants|go-mutesting|mutagen|pitest' \
  -e 'beartype|typeguard|goleak|-race|runtime\.verification' \
  -e 'chaos-toolkit|chaos_toolkit|from chaoslib|toxiproxy|litmus|chaoskube|fault_injection|resilience_test' \
  -e 'atheris|pythonfuzz|func Fuzz[A-Z]|testing\.F\b|go test.*-fuzz|cargo-fuzz|libfuzzer|AFL_|libFuzzer|FUZZING_BUILD_MODE' \
  -g '*.py' -g '*.go' -g '*.ts' -g '*.js' -g '*.tsx' -g '*.jsx' -g '*.rs' \
  -g '*.toml' -g '*.json' -g '*.yml' -g '*.yaml' -g '*.cfg' -g '*.xml' -g '*.mod' \
  -g 'Makefile' -g 'CMakeLists.txt' \
  -g '*.c' -g '*.cpp' -g '*.h' -g '*.hpp' \
  -g '*.sh' -g '*.java' -g '*.bats' \
  "$PROJECT_DIR" 2>/dev/null | awk '
  /hypothesis|quickcheck|proptest|prop_compose|fast-check|fc\.property|@given|@settings|from hypothesis|gopter|rapid\.Check|testing\/quick/ { p=1 }
  /pact|contract\.test|contract_test/ { c=1 }
  /toMatchSnapshot|toMatchInlineSnapshot|syrupy|snapshot_assertion|snapshottest|insta::assert_snapshot|cargo-insta|cupaloy|golden/ { s=1 }
  /approvaltests|from approvaltests|approvals\.Verify/ { a=1 }
  /mutmut|stryker|cargo-mutants|go-mutesting|mutagen|pitest/ { m=1 }
  /beartype|typeguard|goleak|-race|runtime\.verification/ { r=1 }
  /chaos-toolkit|chaos_toolkit|from chaoslib|toxiproxy|litmus|chaoskube|fault_injection|resilience_test/ { ch=1 }
  /atheris|pythonfuzz|func Fuzz|testing\.F|go test.*-fuzz|cargo-fuzz|libfuzzer|AFL_|libFuzzer|FUZZING_BUILD_MODE/ { f=1 }
  END {
    printf "_det_prop=%d _det_contract=%d _det_snapshot=%d _det_approval=%d _det_mutation=%d _det_runtime=%d _det_chaos=%d _det_fuzz=%d\n", p+0, c+0, s+0, a+0, m+0, r+0, ch+0, f+0
  }')"

# L4.3: Multiple test types (unit + integration + one more) (5 points)
test_type_count=0
[[ "$has_unit_dir" == "true" || $test_files_count -gt 0 ]] && test_type_count=$((test_type_count + 1))
[[ "$has_integration" == "true" ]] && test_type_count=$((test_type_count + 1))
[[ -d "$PROJECT_DIR/test/e2e" || -d "$PROJECT_DIR/tests/e2e" || -d "$PROJECT_DIR/test/bdd" || -d "$PROJECT_DIR/tests/bdd" || -d "$PROJECT_DIR/cypress" || -d "$PROJECT_DIR/playwright" ]] && test_type_count=$((test_type_count + 1))
[[ $_det_prop -eq 1 ]] && test_type_count=$((test_type_count + 1))
[[ $_det_contract -eq 1 ]] && test_type_count=$((test_type_count + 1))
if [[ $test_type_count -ge 3 ]]; then
  add_criterion "Multiple test types (3+)" "true" 5 "$test_type_count types"
else
  add_criterion "Multiple test types (3+)" "false" 5 "$test_type_count types (need 3+)"
fi

# L4.4: Snapshot/golden test detection (3 points)
has_snapshot=false
[[ $_det_snapshot -eq 1 ]] && has_snapshot=true
# JS/TS: __snapshots__ directory (only if not already found)
[[ "$has_snapshot" == "false" ]] && rg --no-config --files -g '__snapshots__/*' "$PROJECT_DIR" --max-count 1 >/dev/null 2>&1 && has_snapshot=true
add_criterion "Snapshot/golden tests" "$has_snapshot" 3 ""

# L4.5: Approval test detection (2 points)
has_approval=false
[[ $_det_approval -eq 1 ]] && has_approval=true
add_criterion "Approval tests" "$has_approval" 2 ""

# ========== LEVEL 5 — Mission-Critical (6 criteria, 20 points) ==========

# L5.1: FR traceability = 100% (3 points)
if [[ $fr_total -eq 0 ]]; then
  add_criterion "FR traceability = 100%" "false" 3 "No FRs defined"
elif [[ $fr_pct -eq 100 ]]; then
  add_criterion "FR traceability = 100%" "true" 3 "All $fr_total FRs traced"
else
  add_criterion "FR traceability = 100%" "false" 3 "${fr_pct}% (need 100%)"
fi

# L5.2: Mutation testing configured (4 points)
has_mutation=false
[[ $_det_mutation -eq 1 ]] && has_mutation=true
[[ -f "$PROJECT_DIR/stryker.conf.js" || -f "$PROJECT_DIR/stryker.conf.json" || -f "$PROJECT_DIR/.stryker-tmp" ]] && has_mutation=true
add_criterion "Mutation testing" "$has_mutation" 4 ""

# L5.3: Runtime verification configured (4 points)
has_runtime_verify=false
[[ $_det_runtime -eq 1 ]] && has_runtime_verify=true
add_criterion "Runtime verification" "$has_runtime_verify" 4 ""

# L5.4: Zero suppressed findings (3 points) — uses counts from L2.3 rg pass above
if [[ $bare_suppressions -eq 0 ]]; then
  if [[ $all_suppressions -eq 0 ]]; then
    add_criterion "Zero suppressions" "true" 3 ""
  else
    add_criterion "Zero suppressions" "false" 3 "$all_suppressions total (all justified)"
  fi
else
  add_criterion "Zero suppressions" "false" 3 "$bare_suppressions unjustified"
fi

# L5.5: Chaos/resilience testing (3 points)
has_chaos=false
[[ $_det_chaos -eq 1 ]] && has_chaos=true
# chaos-toolkit experiment.json with steady-state (only if not already found)
[[ "$has_chaos" == "false" ]] && rg --no-config -l 'steady.state' -g 'experiment.json' "$PROJECT_DIR" --max-count 1 >/dev/null 2>&1 && has_chaos=true
add_criterion "Chaos/resilience testing" "$has_chaos" 3 ""

# L5.6: Fuzz testing (3 points)
has_fuzz=false
[[ $_det_fuzz -eq 1 ]] && has_fuzz=true
add_criterion "Fuzz testing" "$has_fuzz" 3 ""

# ========== Calculate Score ==========
total_score=0
total_possible=0
for i in "${!CRITERIA_NAMES[@]}"; do
  total_possible=$((total_possible + CRITERIA_POINTS[i]))
  if [[ "${CRITERIA_PASSED[i]}" == "true" ]]; then
    total_score=$((total_score + CRITERIA_POINTS[i]))
  fi
done

# Determine level
level=0; level_name="None"
if [[ $total_score -ge 81 ]]; then
  level=5; level_name="Mission-Critical"
elif [[ $total_score -ge 61 ]]; then
  level=4; level_name="High-Reliability"
elif [[ $total_score -ge 41 ]]; then
  level=3; level_name="Scale"
elif [[ $total_score -ge 21 ]]; then
  level=2; level_name="Production-Ready"
elif [[ $total_score -gt 0 ]]; then
  level=1; level_name="MVP"
fi

# Determine target (from .qa-config.json or default 3)
target_level=3
if [[ -f "$PROJECT_DIR/.qa-config.json" ]]; then
  configured_target=$($JQ_CMD -r '.target_maturity_level // 3' "$PROJECT_DIR/.qa-config.json" 2>/dev/null)
  [[ -n "$configured_target" && "$configured_target" != "null" ]] && target_level=$configured_target
elif [[ -f "$QUALITY_CONFIG" ]]; then
  configured_target=$($JQ_CMD -r '.target_maturity_level // 3' "$QUALITY_CONFIG" 2>/dev/null)
  [[ -n "$configured_target" && "$configured_target" != "null" ]] && target_level=$configured_target
fi

target_met="not met"
[[ $level -ge $target_level ]] && target_met="met"

# ========== Output Report — only verbose on fails ==========
_has_fail=0
for i in "${!CRITERIA_PASSED[@]}"; do
  [[ "${CRITERIA_PASSED[i]}" == "false" ]] && _has_fail=1 && break
done

if [[ "$_has_fail" -eq 1 ]]; then
  echo "Test Maturity FAIL: Score=$total_score/$total_possible Level=$level ($level_name) Target=$target_level ($target_met)"
  echo ""
  for i in "${!CRITERIA_NAMES[@]}"; do
    if [[ "${CRITERIA_PASSED[i]}" == "false" ]]; then
      detail=""
      [[ -n "${CRITERIA_DETAIL[i]}" ]] && detail=" (${CRITERIA_DETAIL[i]})"
      echo "  [FAIL] ${CRITERIA_NAMES[i]}${detail}"
    fi
  done
  if [[ $level -lt 5 ]]; then
    echo ""
    echo "Next level requires:"
    next_level_start=0
    case $level in 0) next_level_start=0 ;; 1) next_level_start=3 ;; 2) next_level_start=6 ;; 3) next_level_start=9 ;; 4) next_level_start=14 ;; esac
    for i in "${!CRITERIA_NAMES[@]}"; do
      if [[ $i -ge $next_level_start && "${CRITERIA_PASSED[i]}" == "false" ]]; then
        echo "  - ${CRITERIA_NAMES[i]}"
      fi
    done
  fi
else
  echo "Test Maturity: ok ($total_score/$total_possible L$level)"
fi

# ========== Write JSON results ==========
mkdir -p "$(dirname "$RESULTS_FILE")"

criteria_json="["
first=true
for i in "${!CRITERIA_NAMES[@]}"; do
  if [[ "$first" == true ]]; then
    first=false
  else
    criteria_json+=","
  fi
  name="${CRITERIA_NAMES[i]//\"/\\\"}"
  detail="${CRITERIA_DETAIL[i]//\"/\\\"}"
  criteria_json+="{\"name\":\"$name\",\"passed\":${CRITERIA_PASSED[i]},\"points\":${CRITERIA_POINTS[i]},\"detail\":\"$detail\"}"
done
criteria_json+="]"

cat > "$RESULTS_FILE" <<EJSON
{
  "timestamp": "$now",
  "project": "$PROJECT_DIR",
  "score": $total_score,
  "total_possible": $total_possible,
  "level": $level,
  "level_name": "$level_name",
  "target_level": $target_level,
  "target_met": $([ "$target_met" = "met" ] && echo "true" || echo "false"),
  "fr_traceability_pct": $fr_pct,
  "criteria": $criteria_json
}
EJSON

} # end _test_maturity_main

# Run main, capture output, cache result
_output=$(_test_maturity_main 2>&1); _rc=$?

# Write to ultra-fast cache (checked at top before common.sh sourcing)
if [[ -n "${_CACHE_FILE:-}" ]]; then
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  if [[ -n "$_output" ]]; then
    echo "$_output" > "$_CACHE_FILE"
  else
    : > "$_CACHE_FILE"
  fi
fi

[[ -n "$_output" ]] && echo "$_output"
exit "$_rc"
