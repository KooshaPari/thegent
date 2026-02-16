#!/usr/bin/env bash
# suppress-v2-files.sh — PreToolUse hook (Write)
# Blocks creation of *_v2.*, *_new.*, *_old.*, *_backup.* files.
# Philosophy: refactor the original, never duplicate.
# BLOCKING (exit 2 with JSON to block). Budget: <50ms.
set -euo pipefail

trap 'echo "SUPPRESS-V2-FILES FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0

BASENAME="${FILE_PATH##*/}"

# Check for v2/new/old/backup naming patterns
if echo "$BASENAME" | grep -qiE '(_v[0-9]+\.|_new\.|_old\.|_backup\.|_copy\.|_orig\.|\.bak$)' 2>/dev/null; then
  echo "{\"decision\":\"block\",\"reason\":\"File '${BASENAME}' uses a v2/new/old/backup naming pattern. Refactor the original file instead of creating duplicates. See CLAUDE.md: 'Extend, Never Duplicate'.\"}"
  echo "SUPPRESS-V2-FILES FAIL: blocked creation of '${BASENAME}' — refactor the original instead" >&2
  exit 2
fi

exit 0
