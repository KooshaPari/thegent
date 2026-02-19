#!/bin/zsh
# qa-methodology-enforcer.sh
# Advisory/optional-enforcing methodology report from QA attestation.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
ATTEST_FILE="$PROJECT_DIR/.claude/verification/qa-attestation.json"
FAIL_CLOSED="${QA_METHODOLOGY_FAIL_CLOSED:-false}"

if [[ ! -f "$ATTEST_FILE" ]]; then
  echo "METHODOLOGY ENFORCER: attestation missing ($ATTEST_FILE)"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "METHODOLOGY ENFORCER: jq missing; skipping"
  exit 0
fi

FR_TOTAL="$(jq '.summary.fr_total // 0' "$ATTEST_FILE")"
FR_COVERED="$(jq '.summary.fr_covered // 0' "$ATTEST_FILE")"
ORPHAN_TESTS="$(jq '.summary.orphan_tests // 0' "$ATTEST_FILE")"
MISSING_PAIRS="$(jq '.methodology.test_first.missing_test_pairs | length // 0' "$ATTEST_FILE")"
MISSING_TYPES="$(jq '.methodology.missing_required_test_types | length // 0' "$ATTEST_FILE")"

echo "METHODOLOGY ENFORCER:"
echo "- FR coverage: $FR_COVERED/$FR_TOTAL"
echo "- Orphan tests: $ORPHAN_TESTS"
echo "- Missing test-first pairs: $MISSING_PAIRS"
echo "- Missing required test types: $MISSING_TYPES"

violations=0
(( MISSING_PAIRS > 0 )) && violations=$((violations + 1))
(( MISSING_TYPES > 0 )) && violations=$((violations + 1))
(( FR_TOTAL > 0 && FR_COVERED < FR_TOTAL )) && violations=$((violations + 1))

if [[ "$FAIL_CLOSED" == "true" ]] && (( violations > 0 )); then
  echo "METHODOLOGY ENFORCER FAIL: $violations methodology violation(s) found (missing_pairs=$MISSING_PAIRS missing_types=$MISSING_TYPES)" >&2
  exit 2
fi

exit 0
