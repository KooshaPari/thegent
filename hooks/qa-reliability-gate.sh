#!/bin/zsh
# qa-reliability-gate.sh
# Reliability/flake governance from async test results.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
RESULTS="$HOME/.claude/.async-test-results.json"
FAIL_CLOSED="${QA_RELIABILITY_FAIL_CLOSED:-false}"
MAX_FLAKE_RATE="${QA_MAX_FLAKE_RATE:-0.10}"

if [[ ! -f "$RESULTS" ]]; then
  echo "RELIABILITY GATE: no async results file ($RESULTS), skipping"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "RELIABILITY GATE: jq missing"
  [[ "$FAIL_CLOSED" == "true" ]] && { echo "RELIABILITY GATE FAIL: jq command not found" >&2; exit 2; } || exit 0
fi

total="$(jq '.total // 0' "$RESULTS" 2>/dev/null || echo 0)"
failed="$(jq '.failed // 0' "$RESULTS" 2>/dev/null || echo 0)"
flaky="$(jq '.flaky // 0' "$RESULTS" 2>/dev/null || echo 0)"

if [[ "$total" -eq 0 ]]; then
  echo "RELIABILITY GATE: total=0 (no data)"
  exit 0
fi

flake_rate="$(awk -v f="$flaky" -v t="$total" 'BEGIN { if (t==0) print 0; else printf "%.4f", f/t }')"

echo "RELIABILITY GATE: total=$total failed=$failed flaky=$flaky flake_rate=$flake_rate"

exceeds="$(awk -v r="$flake_rate" -v m="$MAX_FLAKE_RATE" 'BEGIN { if (r>m) print "true"; else print "false" }')"
if [[ "$exceeds" == "true" ]]; then
  echo "RELIABILITY GATE: flake rate exceeds max ($MAX_FLAKE_RATE)"
  [[ "$FAIL_CLOSED" == "true" ]] && { echo "RELIABILITY GATE FAIL: flake rate $flake_rate exceeds max $MAX_FLAKE_RATE" >&2; exit 2; } || exit 0
fi

exit 0
