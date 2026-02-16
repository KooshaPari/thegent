#!/usr/bin/env bash
# post-edit-checker.sh — PostToolUse hook (Edit|Write)
# Lightweight per-file checks for immediate feedback after edits.
# Full lint runs are handled by quality-gate.sh on Stop — this hook only does:
#   1. AI slop detection (placeholder/filler content)
#   2. Syntax check on the specific file just edited
#   3. Dead import quick-check (immediate feedback)
# Advisory only (exit 0 always). Budget: <200ms.
# OPTIMIZED: Skip common.sh when dispatched. Inline helpers.
set -euo pipefail

# Stderr message on unexpected failure (set -e)
trap 'echo "POST-EDIT-CHECKER FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # All env vars already set by dispatcher: FILE_PATH, TOOL_NAME, PROJECT_DIR, etc.
  :
else
  HOOK_NAME="POST-EDIT-CHECKER"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

[[ -z "${FILE_PATH:-}" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0

# Inline file_ext / file_basename (avoid function call overhead)
BASENAME="${FILE_PATH##*/}"
EXT="${BASENAME##*.}"

# Inline tool_available: use command -v directly (avoid function + subshell)
_has_cmd() { command -v "$1" >/dev/null 2>&1; }

# ---------- 1. Syntax check (language-specific, fast) ----------
SYNTAX_OUTPUT=""

case "$EXT" in
  py)
    if _has_cmd python3; then
      SYNTAX_OUTPUT=$(timeout 3 python3 -m py_compile "$FILE_PATH" 2>&1 || true)
    elif _has_cmd python; then
      SYNTAX_OUTPUT=$(timeout 3 python -m py_compile "$FILE_PATH" 2>&1 || true)
    fi
    ;;
  sh|bash)
    SYNTAX_OUTPUT=$(bash -n "$FILE_PATH" 2>&1 || true)
    ;;
  ts|tsx|js|jsx)
    if [[ "$EXT" == "js" || "$EXT" == "jsx" ]]; then
      if _has_cmd bun; then
        # Bun: use 'bun build' as a syntax check (no-bundle)
        SYNTAX_OUTPUT=$(timeout 3 bun build --no-bundle "$FILE_PATH" 2>&1 >/dev/null || true)
      elif _has_cmd deno; then
        # Deno: use 'deno check'
        SYNTAX_OUTPUT=$(timeout 3 deno check "$FILE_PATH" 2>&1 || true)
      elif _has_cmd node; then
        SYNTAX_OUTPUT=$(timeout 3 node --check "$FILE_PATH" 2>&1 || true)
      fi
    fi
    ;;
  rb)
    if _has_cmd ruby; then
      SYNTAX_OUTPUT=$(timeout 3 ruby -c "$FILE_PATH" 2>&1 || true)
      [[ "$SYNTAX_OUTPUT" == "Syntax OK" ]] && SYNTAX_OUTPUT=""
    fi
    ;;
  go)
    if _has_cmd go; then
      SYNTAX_OUTPUT=$(timeout 3 go vet "$FILE_PATH" 2>&1 || true)
    fi
    ;;
  json)
    if _has_cmd jq; then
      SYNTAX_OUTPUT=$(timeout 3 jq empty "$FILE_PATH" 2>&1 || true)
    elif _has_cmd python3; then
      SYNTAX_OUTPUT=$(timeout 3 python3 -m json.tool "$FILE_PATH" >/dev/null 2>&1 || true)
    fi
    ;;
  xml)
    if _has_cmd xmllint; then
      SYNTAX_OUTPUT=$(timeout 3 xmllint --noout "$FILE_PATH" 2>&1 || true)
    fi
    ;;
esac

if [[ -n "$SYNTAX_OUTPUT" ]] && [[ "$SYNTAX_OUTPUT" =~ [^[:space:]] ]]; then
  echo "SYNTAX CHECK [${BASENAME}]:"
  echo "$SYNTAX_OUTPUT"
fi

# ---------- 2. AI Slop Detection ----------
check_slop() {
  local file="$1"
  local basename="$2"

  # Skip test fixture files
  case "$file" in
    */test/fixtures/*|*/__fixtures__/*) return 0 ;;
  esac

  # Build combined pattern
  local pattern='TODO:\s*(implement|add)'
  pattern+='|Lorem ipsum'
  pattern+='|your-.*-here|replace-with|CHANGEME'
  pattern+='|As an AI|I cannot|I apologize'
  pattern+='|#.*This function\s+.*does'
  pattern+='|#\s*This is a\s+(helper|utility|simple|basic|generic|common|main|class|function|method|module|script|file|wrapper|handler|manager|service|factory|component|controller)'
  pattern+='|pass\s+#\s*(placeholder|TODO)'
  pattern+='|throw new Error\(.*(not implemented|todo)'
  pattern+='|panic\(.*(not implemented|todo|unimplemented)'

  # For non-test files, also detect example.com
  case "$file" in
    */test/*|*/tests/*|*_test.*|*_spec.*|*.test.*|*.spec.*) ;;
    *) pattern+='|example\.com' ;;
  esac

  local matches
  matches=$(grep -inE "$pattern" "$file" 2>/dev/null || true)
  [[ -z "$matches" ]] && return 0

  # Count lines with bash builtin
  local count=0
  while IFS= read -r _; do (( count++ )); done <<< "$matches"
  echo "SLOP: $count potential AI-generated placeholder(s) in $basename"
  echo "$matches" | head -5
}

# ---------- 3. Dead Import Quick-Check ----------
check_dead_imports() {
  local file="$1"
  local ext="$2"
  local basename="$3"
  local output=""

  case "$ext" in
    py)
      _has_cmd ruff || return 0
      output=$(timeout 3 ruff check --select F401 --no-fix "$file" 2>/dev/null || true)
      ;;
    js|ts|jsx|tsx)
      _has_cmd oxlint || return 0
      output=$(timeout 3 oxlint -D no-unused-vars "$file" 2>/dev/null || true)
      ;;
    *)
      return 0
      ;;
  esac

  [[ -z "$output" ]] && return 0
  [[ ! "$output" =~ [^[:space:]] ]] && return 0

  # Count lines with bash
  local count=0
  while IFS= read -r _; do (( count++ )); done <<< "$output"
  echo "DEAD IMPORTS: $count unused import(s) in $basename"
  echo "$output"
}

check_slop "$FILE_PATH" "$BASENAME"
check_dead_imports "$FILE_PATH" "$EXT" "$BASENAME"

exit 0
