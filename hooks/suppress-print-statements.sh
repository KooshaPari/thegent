#!/usr/bin/env bash
# suppress-print-statements.sh — PreToolUse hook (Write|Edit)
# Detects print() in non-CLI source code. Enforces structlog usage.
# Advisory (exit 0 always). Budget: <100ms.
set -euo pipefail

trap 'echo "SUPPRESS-PRINT-STATEMENTS FAIL: unexpected error at line $LINENO" >&2' ERR

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" ]] && exit 0

# Skip CLI entry points, scripts, and tests
case "$BASENAME" in
  __main__.py|main.py|cli.py|*_cli.py) exit 0 ;;
esac
case "$FILE_PATH" in */tests/*|*/test/*|*/scripts/*) exit 0 ;; esac

SCAN_CONTENT="${TOOL_NEW_STRING:-${TOOL_CONTENT:-}}"
[[ -z "$SCAN_CONTENT" ]] && SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || true
[[ -z "$SCAN_CONTENT" ]] && exit 0

# Skip if file imports typer/click/rich (CLI files)
if echo "$SCAN_CONTENT" | grep -qE '(import typer|import click|from rich|from typer|from click)' 2>/dev/null; then
  exit 0
fi

PRINT_COUNT=$(echo "$SCAN_CONTENT" | grep -cE '^\s*print\(' 2>/dev/null || echo 0)
if [[ "$PRINT_COUNT" -ge 2 ]]; then
  echo "ANTIPATTERN [${BASENAME}]: ${PRINT_COUNT} print() calls in non-CLI code."
  echo "  FIX: Use structured logging instead:"
  echo "    import structlog"
  echo "    logger = structlog.get_logger()"
  echo "    logger.info(\"message\", key=\"value\")"
fi

exit 0
