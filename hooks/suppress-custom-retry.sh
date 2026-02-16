#!/usr/bin/env bash
# suppress-custom-retry.sh — PreToolUse hook (Write|Edit)
# Detects custom retry logic when tenacity is available in project deps.
# Advisory (exit 0 always). Budget: <100ms.
set -euo pipefail

trap 'echo "SUPPRESS-CUSTOM-RETRY FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" ]] && exit 0

# Skip test files
case "$FILE_PATH" in */tests/*|*/test/*|test_*) exit 0 ;; esac

SCAN_CONTENT="${TOOL_NEW_STRING:-${TOOL_CONTENT:-}}"
[[ -z "$SCAN_CONTENT" ]] && SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || true
[[ -z "$SCAN_CONTENT" ]] && exit 0

if echo "$SCAN_CONTENT" | grep -qE '(while\s+.*retry|for\s+.*in\s+range.*retry|max_retries|retry_count|num_retries|sleep.*retry|except.*retry)' 2>/dev/null; then
  if ! echo "$SCAN_CONTENT" | grep -qE '(from tenacity|import tenacity)' 2>/dev/null; then
    echo "ANTIPATTERN [${BASENAME}]: Custom retry logic detected."
    echo "  FIX: Use tenacity (already in deps):"
    echo "    from tenacity import retry, stop_after_attempt, wait_exponential"
    echo "    @retry(stop=stop_after_attempt(5), wait=wait_exponential())"
    echo "    def fetch(url: str) -> httpx.Response:"
    echo "        return httpx.get(url, timeout=10)"
  fi
fi

exit 0
