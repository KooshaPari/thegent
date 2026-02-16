#!/usr/bin/env bash
# suppress-direct-http.sh — PreToolUse hook (Write|Edit)
# Detects raw requests/urllib usage when httpx should be used.
# Advisory (exit 0 always). Budget: <100ms.
set -euo pipefail

trap 'echo "SUPPRESS-DIRECT-HTTP FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" ]] && exit 0

# Skip test files and scripts
case "$FILE_PATH" in */tests/*|*/test/*|*/scripts/*) exit 0 ;; esac

SCAN_CONTENT="${TOOL_NEW_STRING:-${TOOL_CONTENT:-}}"
[[ -z "$SCAN_CONTENT" ]] && SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || true
[[ -z "$SCAN_CONTENT" ]] && exit 0

# Detect requests library usage (should use httpx)
if echo "$SCAN_CONTENT" | grep -qE '^\s*(import requests|from requests import|requests\.(get|post|put|delete|patch)\()' 2>/dev/null; then
  echo "ANTIPATTERN [${BASENAME}]: Using 'requests' library. Prefer httpx (async-capable, modern)."
  echo "  FIX: Replace with httpx:"
  echo "    import httpx"
  echo "    response = httpx.get(url, timeout=10)"
  echo "    # Or async: async with httpx.AsyncClient() as client: ..."
fi

# Detect urllib usage
if echo "$SCAN_CONTENT" | grep -qE '^\s*(import urllib|from urllib import|urllib\.request\.)' 2>/dev/null; then
  echo "ANTIPATTERN [${BASENAME}]: Using urllib. Prefer httpx for HTTP requests."
  echo "  FIX: import httpx; response = httpx.get(url, timeout=10)"
fi

# Detect custom HTTP wrapper classes (without httpx underneath)
if echo "$SCAN_CONTENT" | grep -qE 'class\s+\w*(Http|HTTP|Api|API)(Client|Wrapper|Session|Handler)\b' 2>/dev/null; then
  if ! echo "$SCAN_CONTENT" | grep -qE '(import httpx|from httpx)' 2>/dev/null; then
    echo "ANTIPATTERN [${BASENAME}]: Custom HTTP client class without httpx."
    echo "  FIX: Use httpx directly or wrap httpx.Client/AsyncClient."
  fi
fi

exit 0
