#!/usr/bin/env bash
# suppress-isolated-classes.sh — PreToolUse hook (Write|Edit)
# Detects God classes (too many methods) and suggests decomposition.
# Advisory (exit 0 always). Budget: <200ms.
set -euo pipefail

trap 'echo "SUPPRESS-ISOLATED-CLASSES FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" ]] && exit 0

# Skip test files
case "$FILE_PATH" in */tests/*|*/test/*) exit 0 ;; esac

SCAN_CONTENT="${TOOL_NEW_STRING:-${TOOL_CONTENT:-}}"
[[ -z "$SCAN_CONTENT" ]] && SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || true
[[ -z "$SCAN_CONTENT" ]] && exit 0

# Count methods per class — flag if a class has >15 methods
METHOD_COUNT=$(echo "$SCAN_CONTENT" | grep -cE '^\s+def\s+' 2>/dev/null || echo 0)
CLASS_COUNT=$(echo "$SCAN_CONTENT" | grep -cE '^\s*class\s+' 2>/dev/null || echo 0)

if [[ "$CLASS_COUNT" -ge 1 && "$METHOD_COUNT" -gt 15 ]]; then
  AVG=$((METHOD_COUNT / CLASS_COUNT))
  if [[ "$AVG" -gt 15 ]]; then
    echo "ANTIPATTERN [${BASENAME}]: Potential God class (${METHOD_COUNT} methods across ${CLASS_COUNT} class(es), avg ${AVG})."
    echo "  FIX: Decompose into smaller classes with single responsibilities."
    echo "  Consider: Protocol/ABC for shared interface, composition over inheritance."
  fi
fi

# Detect classes that duplicate functionality of existing patterns
if echo "$SCAN_CONTENT" | grep -qE 'class\s+\w*(Manager|Handler|Controller|Service)\b.*:' 2>/dev/null; then
  # Check if there are multiple Manager/Handler/etc. in the same file
  PATTERN_COUNT=$(echo "$SCAN_CONTENT" | grep -cE 'class\s+\w*(Manager|Handler|Controller|Service)\b.*:' 2>/dev/null || echo 0)
  if [[ "$PATTERN_COUNT" -ge 3 ]]; then
    echo "ANTIPATTERN [${BASENAME}]: ${PATTERN_COUNT} Manager/Handler/Service classes in one file."
    echo "  FIX: Consider a generic registry pattern instead of N isolated classes."
  fi
fi

exit 0
