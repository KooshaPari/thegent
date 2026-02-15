#!/usr/bin/env bash
# pre-write-validator.sh — PreToolUse hook (Write|Edit)
# Validates syntax of file content before write lands.
# Budget: <1s. Exit 2 + JSON to block, exit 0 to pass.
set -euo pipefail
HOOK_NAME="PRE-WRITE-VALIDATOR"

# Dispatched mode: skip common.sh entirely — env vars already set by dispatcher
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # FILE_PATH, TOOL_NAME, TOOL_CONTENT, TOOL_NEW_STRING, TIMEOUT_CMD already exported
  :
else
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
  hook_extract_content
fi

[[ -z "${FILE_PATH:-}" ]] && exit 0

# Determine content to validate based on tool type
CONTENT=""
if [[ "$TOOL_NAME" == "Write" ]]; then
  CONTENT="${TOOL_CONTENT:-}"
elif [[ "$TOOL_NAME" == "Edit" ]]; then
  CONTENT="${TOOL_NEW_STRING:-}"
fi

[[ -z "$CONTENT" ]] && exit 0

# Detect file type from extension (bash builtin, no subprocess)
EXT="${FILE_PATH##*.}"

block_with_reason() {
  local reason="$1"
  echo "{\"decision\":\"block\",\"reason\":\"Syntax error in ${FILE_PATH##*/}: $reason\"}"
  echo "PRE-WRITE VALIDATOR FAIL: syntax error in ${FILE_PATH##*/}: $reason" >&2
  exit 2
}

run_short_timeout() {
  if [[ -n "${TIMEOUT_CMD:-}" ]]; then
    "$TIMEOUT_CMD" 3 "$@"
  else
    "$@"
  fi
}

case "$EXT" in
  py)
    # Python: compile check via temp file
    if [[ "$TOOL_NAME" == "Write" ]]; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.py)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(python3 -c "compile(open('$TMPF').read(), '$TMPF', 'exec')" 2>&1) || block_with_reason "$ERR"
    fi
    # For Edit, we only have a snippet — skip full compile
    ;;
  sh|bash)
    # Shell: bash -n syntax check (only full files)
    if [[ "$TOOL_NAME" == "Write" ]]; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.sh)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(bash -n "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  json)
    # JSON: validate with jq or python
    if [[ "$TOOL_NAME" == "Write" ]]; then
      ERR=$(echo "$CONTENT" | jq . >/dev/null 2>&1) || {
        ERR=$(echo "$CONTENT" | python3 -m json.tool 2>&1 >/dev/null) || block_with_reason "$ERR"
      }
    fi
    ;;
  yaml|yml)
    # YAML: python yaml.safe_load
    if [[ "$TOOL_NAME" == "Write" ]]; then
      ERR=$(echo "$CONTENT" | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin)" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  toml)
    # TOML: python tomllib (3.11+)
    if [[ "$TOOL_NAME" == "Write" ]]; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.toml)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(python3 -c "import tomllib; tomllib.load(open('$TMPF','rb'))" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  c|h)
    # C: gcc syntax-only check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v gcc &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.c)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(gcc -fsyntax-only -x c "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  cpp|hpp|cc|cxx)
    # C++: g++ syntax-only check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v g++ &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.cpp)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(g++ -fsyntax-only -x c++ "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  java)
    # Java: javac syntax/type check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v javac &>/dev/null; then
      TMPD=$(mktemp -d /tmp/qa-validate-java-XXXXXX)
      TMPF="$TMPD/Main.java"
      trap 'rm -rf "$TMPD"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(run_short_timeout javac -d "$TMPD" "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  kt|kts)
    # Kotlin: lightweight compile/script check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v kotlinc &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.kt)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(run_short_timeout kotlinc -script "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  swift)
    # Swift: typecheck only
    if [[ "$TOOL_NAME" == "Write" ]] && command -v swiftc &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.swift)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(run_short_timeout swiftc -typecheck "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  rb)
    # Ruby: syntax check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v ruby &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.rb)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(ruby -c "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  php)
    # PHP: lint check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v php &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.php)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(php -l "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  lua)
    # Lua: luac parse check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v luac &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.lua)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(luac -p "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  pl|pm)
    # Perl: syntax check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v perl &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.pl)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(perl -c "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  xml)
    # XML: xmllint well-formedness check
    if [[ "$TOOL_NAME" == "Write" ]] && command -v xmllint &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.xml)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(xmllint --noout "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  html|htm)
    # HTML: xmllint html mode (lenient — don't block on warnings)
    if [[ "$TOOL_NAME" == "Write" ]] && command -v xmllint &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.html)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      xmllint --html --noout "$TMPF" 2>/dev/null || true
    fi
    ;;
  dart)
    # Dart: skip — dart analyze requires project context, too slow for pre-write
    ;;
  hs)
    # Haskell: ghc no-code syntax check (timeout guarded)
    if [[ "$TOOL_NAME" == "Write" ]] && command -v ghc &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.hs)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(run_short_timeout ghc -fno-code "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  proto)
    # Protobuf: buf lint check in ephemeral module context
    if [[ "$TOOL_NAME" == "Write" ]] && command -v buf &>/dev/null; then
      TMPD=$(mktemp -d /tmp/qa-validate-proto-XXXXXX)
      TMPF="$TMPD/tmp.proto"
      trap 'rm -rf "$TMPD"' EXIT
      echo "$CONTENT" > "$TMPF"
      cat > "$TMPD/buf.yaml" <<'EOB'
version: v1
lint:
  use:
    - DEFAULT
EOB
      ERR=$(run_short_timeout buf lint "$TMPD" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  ex|exs)
    # Elixir: compile check (timeout guarded)
    if [[ "$TOOL_NAME" == "Write" ]] && command -v elixirc &>/dev/null; then
      TMPF=$(mktemp /tmp/qa-validate-XXXXXX.ex)
      trap 'rm -f "$TMPF"' EXIT
      echo "$CONTENT" > "$TMPF"
      ERR=$(run_short_timeout elixirc --ignore-module-conflict "$TMPF" 2>&1) || block_with_reason "$ERR"
    fi
    ;;
  *)
    # Unknown file type — pass through
    ;;
esac

exit 0
