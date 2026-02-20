#!/usr/bin/env zsh
# tts.sh - Hook wrapper for TTS service.
# Usage: hook-dispatcher tts '{"content": "message to speak"}'

HOOK_NAME="TTS"
# Using absolute path to common.sh relative to script
source "${(%):-%x:h}/lib/common.sh"
hook_init

# Extract content to speak
MESSAGE="${TOOL_CONTENT:-$1}"
if [[ -z "$MESSAGE" ]]; then
    exit 0
fi

# Determine language
# (Simple detection or ENV override)
LANG="${THGENT_TTS_LANG:-en}"

# Call the standalone tts tool
# Assuming it's in ~/.local/bin/ which should be in PATH
# but we'll use full path to be safe.
TTS_BIN="$HOME/.local/bin/tts"

if [[ ! -x "$TTS_BIN" ]]; then
    echo "Error: tts tool not found at $TTS_BIN" >&2
    exit 1
fi

# Speak the message
# Note: we use a temp file because the tts tool expects a filename
TMP_MSG=$(mktemp)
echo "$MESSAGE" > "$TMP_MSG"

"$TTS_BIN" "$LANG" "$TMP_MSG"

rm -f "$TMP_MSG"
