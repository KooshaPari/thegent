#!/usr/bin/env bash
# suppress-hardcoded-strings.sh — PreToolUse hook (Write|Edit)
# Detects hardcoded provider names and model strings in non-config files.
# Advisory (exit 0 always). Budget: <100ms.
set -euo pipefail

trap 'echo "SUPPRESS-HARDCODED-STRINGS FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" && "$EXT" != "ts" && "$EXT" != "js" ]] && exit 0

# Skip config/settings/constants files where hardcoding is expected
case "$BASENAME" in
  settings.py|config.py|*settings*|*config*|*constants*|*enum*|*.env*) exit 0 ;;
esac
case "$FILE_PATH" in */tests/*|*/test/*) exit 0 ;; esac

SCAN_CONTENT="${TOOL_NEW_STRING:-${TOOL_CONTENT:-}}"
[[ -z "$SCAN_CONTENT" ]] && SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || true
[[ -z "$SCAN_CONTENT" ]] && exit 0

# Check for hardcoded provider/model strings
if echo "$SCAN_CONTENT" | grep -qE "(provider\s*=\s*[\"'](openai|anthropic|google|azure|cohere|mistral|groq)[\"']|model\s*=\s*[\"'](gpt-4|gpt-3|claude|gemini|llama)[\"'])" 2>/dev/null; then
  echo "ANTIPATTERN [${BASENAME}]: Hardcoded provider/model strings detected."
  echo "  FIX: Use ProviderRegistry pattern and config-driven selection:"
  echo "    from ${PROJECT_NAME:-myproject}.config import settings"
  echo "    provider = registry.get(settings.llm_provider)"
fi

exit 0
