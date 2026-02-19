#!/bin/zsh
# agent-antipattern-detector.sh — PostToolUse hook (Edit|Write)
# Detects agent anti-patterns in Python files: reinventing wheels, wrong libraries,
# hardcoded providers, manual patterns that have library equivalents.
# Advisory only (exit 0 always). Budget: <300ms.
# OPTIMIZED: Skip common.sh when dispatched. Inline helpers.
set -euo pipefail

trap 'echo "AGENT-ANTIPATTERN-DETECTOR FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  :
else
  HOOK_NAME="AGENT-ANTIPATTERN-DETECTOR"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

# Only check Python files
BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"
[[ "$EXT" != "py" ]] && exit 0

# Skip test files, conftest, and config files
case "$BASENAME" in
  test_*|*_test.py|conftest.py) exit 0 ;;
esac
case "$FILE_PATH" in
  */tests/*|*/test/*) exit 0 ;;
esac

WARNINGS=()

# Determine content to scan: for Edit use new_string, for Write use content
SCAN_CONTENT=""
if [[ -n "${TOOL_NEW_STRING:-}" ]]; then
  SCAN_CONTENT="$TOOL_NEW_STRING"
elif [[ -n "${TOOL_CONTENT:-}" ]]; then
  SCAN_CONTENT="$TOOL_CONTENT"
else
  # Fallback: read the file (budget-safe, only for non-dispatched mode)
  SCAN_CONTENT="$(cat "$FILE_PATH" 2>/dev/null)" || exit 0
fi

[[ -z "$SCAN_CONTENT" ]] && exit 0

# ---------- 1. Custom retry loops (tenacity is in deps) ----------
if echo "$SCAN_CONTENT" | grep -qE '(while\s+.*retry|for\s+.*in\s+range.*retry|max_retries|retry_count|num_retries|sleep.*retry|except.*retry)' 2>/dev/null; then
  # Exclude if tenacity is already imported in the same content
  if ! echo "$SCAN_CONTENT" | grep -qE '(from tenacity|import tenacity)' 2>/dev/null; then
    WARNINGS+=("ANTIPATTERN: Custom retry logic detected. Use tenacity (already in deps) instead of manual retry loops.")
  fi
fi

# ---------- 2. import logging instead of structlog ----------
if echo "$SCAN_CONTENT" | grep -qE '^\s*(import logging|from logging import|logging\.getLogger)' 2>/dev/null; then
  WARNINGS+=("ANTIPATTERN: Using stdlib logging. Prefer structlog for structured logging (see CLAUDE.md library preferences).")
fi

# ---------- 3. import argparse when typer is available ----------
if echo "$SCAN_CONTENT" | grep -qE '^\s*(import argparse|from argparse import)' 2>/dev/null; then
  WARNINGS+=("ANTIPATTERN: Using argparse. Use typer (already in deps) for CLI argument parsing.")
fi

# ---------- 4. Manual env parsing instead of pydantic-settings ----------
# Only flag in non-settings/config files (settings files legitimately use os.environ)
case "$BASENAME" in
  settings.py|config.py|*settings*.py|*config*.py) ;;
  *)
    ENV_HITS=$(echo "$SCAN_CONTENT" | grep -cE '(os\.environ\[|os\.environ\.get\(|os\.getenv\()' 2>/dev/null || echo 0)
    if [[ "$ENV_HITS" -ge 3 ]]; then
      WARNINGS+=("ANTIPATTERN: Multiple os.environ/os.getenv calls ($ENV_HITS). Use pydantic-settings (already in deps) for config management.")
    fi
    ;;
esac

# ---------- 5. Hardcoded provider strings in non-config files ----------
case "$BASENAME" in
  settings.py|config.py|*settings*.py|*config*.py|*constants*.py|*enum*.py) ;;
  *)
    if echo "$SCAN_CONTENT" | grep -qE '(provider\s*=\s*["\x27](openai|anthropic|google|azure|cohere|mistral|groq)["\x27]|model\s*=\s*["\x27](gpt-4|gpt-3|claude|gemini)["\x27])' 2>/dev/null; then
      WARNINGS+=("ANTIPATTERN: Hardcoded provider/model strings. Use ProviderRegistry pattern and config-driven provider selection.")
    fi
    ;;
esac

# ---------- 6. print() in non-CLI source code ----------
# Skip CLI entry points, __main__, and files that import typer/click/rich
case "$BASENAME" in
  __main__.py|main.py|cli.py|*_cli.py) ;;
  *)
    if echo "$SCAN_CONTENT" | grep -qE '^\s*print\(' 2>/dev/null; then
      # Only warn if this doesn't look like a CLI file
      if ! echo "$SCAN_CONTENT" | grep -qE '(import typer|import click|from rich|from typer|from click)' 2>/dev/null; then
        PRINT_COUNT=$(echo "$SCAN_CONTENT" | grep -cE '^\s*print\(' 2>/dev/null || echo 0)
        if [[ "$PRINT_COUNT" -ge 2 ]]; then
          WARNINGS+=("ANTIPATTERN: $PRINT_COUNT print() calls in non-CLI code. Use structured logging (structlog/rich) instead.")
        fi
      fi
    fi
    ;;
esac

# ---------- 7. Custom HTTP wrapper classes ----------
if echo "$SCAN_CONTENT" | grep -qE '(class\s+\w*(Http|HTTP|Api|API)(Client|Wrapper|Session|Handler)\b)' 2>/dev/null; then
  if ! echo "$SCAN_CONTENT" | grep -qE '(import httpx|from httpx)' 2>/dev/null; then
    WARNINGS+=("ANTIPATTERN: Custom HTTP client class detected. Use httpx directly (see CLAUDE.md library preferences).")
  fi
fi

# ---------- 8. Manual validation instead of pydantic ----------
MANUAL_VALIDATION=$(echo "$SCAN_CONTENT" | grep -cE '(isinstance\(.*,\s*(str|int|float|dict|list)\)|if\s+not\s+isinstance|raise\s+(TypeError|ValueError)\(\s*f?["\x27](Expected|Invalid|Must be))' 2>/dev/null || echo 0)
if [[ "$MANUAL_VALIDATION" -ge 4 ]]; then
  WARNINGS+=("ANTIPATTERN: Extensive manual type validation ($MANUAL_VALIDATION checks). Use pydantic models (already in deps) for data validation.")
fi

# ---------- Output warnings ----------
if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo "AGENT ANTI-PATTERNS [${BASENAME}]: ${#WARNINGS[@]} issue(s) detected"
  for w in "${WARNINGS[@]}"; do
    echo "  - $w"
  done
fi

exit 0
