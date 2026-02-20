#!/bin/zsh
# suppression-blocker.sh — PreToolUse hook (Write|Edit)
# Blocks introduction of NEW lint suppressions. Budget: <500ms.
# Exit 2 + JSON to block, exit 0 to pass.
set -euo pipefail
HOOK_NAME="SUPPRESSION-BLOCKER"

# Dispatched mode: env vars already set by dispatcher, but we still need common helpers
if [[ -z "${FILE_PATH:-}" || -z "${TOOL_NAME:-}" ]]; then
  source "${0:h}/lib/common.sh"
  hook_init
  hook_extract_content
elif [[ -z "${_HOOK_LIB_LOADED:-}" ]]; then
  source "${0:h}/lib/common.sh"
fi

[[ -z "${FILE_PATH:-}" ]] && exit 0

# Honor skip list
if hook_should_skip "$HOOK_NAME"; then
  exit 0
fi

# Suppression patterns (grep -E extended regex)
SUPPRESSION_RE='#[[:space:]]*noqa|#[[:space:]]*type:[[:space:]]*ignore|#[[:space:]]*pragma:[[:space:]]*no[[:space:]]*cover|//[[:space:]]*eslint-disable|/\*[[:space:]]*eslint-disable|@ts-ignore|@ts-expect-error|//[[:space:]]*nolint|#\[allow\(|#[[:space:]]*nosec|//[[:space:]]*nosemgrep|@SuppressWarnings|@Suppress\(|//[[:space:]]*swiftlint:disable|#[[:space:]]*rubocop:disable|//[[:space:]]*phpcs:disable|//[[:space:]]*@phpstan-ignore|/\*[[:space:]]*stylelint-disable|<!--[[:space:]]*markdownlint-disable|//[[:space:]]*ignore:|//[[:space:]]*ignore_for_file:|--[[:space:]]*noqa|#[[:space:]]*tfsec:ignore|--[[:space:]]*luacheck:[[:space:]]*ignore|#[[:space:]]*credo:disable|\{-[[:space:]]*HLINT[[:space:]]*ignore'

# Count suppression lines using grep -cE (much faster than bash loop)
count_suppressions() {
  local text="$1"
  [[ -z "$text" ]] && { echo 0; return; }
  grep -cE "$SUPPRESSION_RE" <<< "$text" 2>/dev/null || echo 0
}

if [[ "$TOOL_NAME" == "Write" ]]; then
  [[ -z "$TOOL_CONTENT" ]] && exit 0

  NEW_COUNT=$(count_suppressions "$TOOL_CONTENT")

  # Compare against existing file
  if [[ -f "$FILE_PATH" ]]; then
    OLD_COUNT=$(count_suppressions "$(< "$FILE_PATH")")
  else
    OLD_COUNT=0
  fi

  if [[ "$NEW_COUNT" -gt "$OLD_COUNT" ]]; then
    DIFF=$(( NEW_COUNT - OLD_COUNT ))
    echo "{\"decision\":\"block\",\"reason\":\"Suppression blocker: $DIFF new lint suppression(s) detected in ${FILE_PATH##*/}. Fix the code instead of suppressing warnings. If unavoidable, add an inline justification comment (e.g. # noqa: E501 -- line is a URL).\"}"
    echo "SUPPRESSION BLOCKER FAIL: $DIFF new lint suppression(s) detected in ${FILE_PATH##*/}" >&2
    exit 2
  fi

elif [[ "$TOOL_NAME" == "Edit" ]]; then
  [[ -z "$TOOL_NEW_STRING" ]] && exit 0

  OLD_COUNT=$(count_suppressions "$TOOL_OLD_STRING")
  NEW_COUNT=$(count_suppressions "$TOOL_NEW_STRING")

  if [[ "$NEW_COUNT" -gt "$OLD_COUNT" ]]; then
    DIFF=$(( NEW_COUNT - OLD_COUNT ))
    echo "{\"decision\":\"block\",\"reason\":\"Suppression blocker: $DIFF new lint suppression(s) in edit to ${FILE_PATH##*/}. Fix the code instead of suppressing warnings. If unavoidable, add an inline justification comment.\"}"
    echo "SUPPRESSION BLOCKER FAIL: $DIFF new lint suppression(s) in edit to ${FILE_PATH##*/}" >&2
    exit 2
  fi
fi

exit 0
