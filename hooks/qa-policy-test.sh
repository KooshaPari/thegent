#!/usr/bin/env bash
# qa-policy-test.sh — PostToolUse hook for policy files
# Runs `opa test` when QA Rego policies are edited.

# Pre-init fast-path for dispatcher mode
[[ -n "${_HOOK_DISPATCHED:-}" && "${FILE_PATH:-}" != *.rego ]] && exit 0

set -euo pipefail
HOOK_NAME="QA-POLICY-TEST"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# --- Fast-path exit: only care about .rego files in qa policy dir ---
[[ -z "$FILE_PATH" ]] && exit 0

# Quick extension check before heavier pattern match (zero spawns)
[[ "$FILE_PATH" != *.rego ]] && exit 0

case "$FILE_PATH" in
  *"/.claude/policies/qa/"*) ;;
  *) exit 0 ;;
esac

POLICY_DIR="$HOME/.claude/policies/qa"

if ! command -v opa >/dev/null 2>&1; then
  echo "POLICY TEST: opa not installed"
  if [[ "${QA_POLICY_TEST_FAIL_CLOSED:-true}" == "true" ]]; then
    echo "POLICY TEST FAIL: opa not installed but required for policy testing" >&2
    exit 2
  fi
  exit 0
fi

[[ ! -d "$POLICY_DIR" ]] && { echo "POLICY TEST: policy dir missing; skipping"; exit 0; }

OUT="$(opa test "$POLICY_DIR" 2>&1 || true)"
if [[ -n "$OUT" ]]; then
  echo "POLICY TEST:"
  echo "$OUT"
fi

# Use bash pattern matching instead of grep subprocess
if [[ "$OUT" == *FAIL* || "$OUT" == *fail* || "$OUT" == *error* ]]; then
  if [[ "${QA_POLICY_TEST_FAIL_CLOSED:-true}" == "true" ]]; then
    echo "POLICY TEST FAIL: opa test detected failures in QA Rego policies" >&2
    exit 2
  fi
fi

exit 0
