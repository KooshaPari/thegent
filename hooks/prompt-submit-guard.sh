#!/usr/bin/env bash
# prompt-submit-guard.sh — UserPromptSubmit hook
# Detects antipattern phrases in user prompts and prints advisory QA reminders.
# Advisory only (always exits 0, never blocks).
# OPTIMIZED: No common.sh sourcing. Pure bash builtins. Target: <50ms.
set -euo pipefail

# Stderr message on unexpected failure (set -e)
trap 'echo "PROMPT-SUBMIT-GUARD FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast inline input parsing (no jq, no common.sh) ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # Dispatcher already set PROMPT_TEXT or we extract from env
  PROMPT_TEXT="${PROMPT_TEXT:-}"
else
  # Read stdin, extract prompt text with single jq call
  INPUT="$(cat)"
  PROMPT_TEXT=$(jq -r '.tool_input.prompt // .tool_input.content // .content // empty' <<< "${INPUT:-{\}}" 2>/dev/null) || PROMPT_TEXT=""
fi

[[ -z "$PROMPT_TEXT" ]] && exit 0

# Convert to lowercase for case-insensitive matching (bash builtin, no spawns)
PROMPT_LOWER="${PROMPT_TEXT,,}"

# ---------- Antipattern detection (all bash builtins, zero spawns) ----------
ANTIPATTERNS_FOUND=()

# Test-skipping patterns
for pattern in "skip tests" "skip the tests" "don't write tests" "no tests" "dont write tests" "without tests"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("test-skipping: \"$pattern\"")
    break
  fi
done

# Lint-skipping patterns
for pattern in "disable lint" "ignore lint" "skip lint" "no linting"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("lint-skipping: \"$pattern\"")
    break
  fi
done

# Quality-skipping patterns
for pattern in "just make it work" "just get it working" "just get it done" "make it work somehow"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("quality-shortcut: \"$pattern\"")
    break
  fi
done

# Error-suppression patterns
for pattern in "ignore the errors" "ignore errors" "suppress the" "suppress errors" "hide the errors"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("error-suppression: \"$pattern\"")
    break
  fi
done

# Dangerous git patterns
for pattern in "--no-verify" "--force" "force push" "force-push" "--force-with-lease"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("dangerous-git: \"$pattern\"")
    break
  fi
done

# ---------- Print advisory if antipatterns detected ----------
if [[ ${#ANTIPATTERNS_FOUND[@]} -gt 0 ]]; then
  echo "QA Governance Reminder: Quality enforcement is active."
  echo "  Detected patterns:"
  for ap in "${ANTIPATTERNS_FOUND[@]}"; do
    echo "    - $ap"
  done
  echo "  Consider:"
  echo "    - Tests are required for all new code (TDD mandate)"
  echo "    - Suppressions require inline justification"
  echo "    - All linters must pass"
fi

# ---------- Check for pending QA findings ----------
QA_FINDINGS="$HOME/.claude/.qa-findings-pending"
if [[ -f "$QA_FINDINGS" ]] && [[ -s "$QA_FINDINGS" ]]; then
  # Count lines using bash builtin (eliminates wc + tr spawns)
  FINDING_COUNT=0
  while IFS= read -r _; do
    (( FINDING_COUNT++ ))
  done < "$QA_FINDINGS"
  echo "QA Reminder: $FINDING_COUNT unresolved finding(s) from previous quality checks."
  echo "  Review: $QA_FINDINGS"
fi

exit 0
