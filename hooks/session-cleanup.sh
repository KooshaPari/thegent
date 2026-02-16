#!/bin/bash
# Hook: SessionEnd
# Purpose: Clean up session-level state and finalize any pending tracker updates.
# OPTIMIZED: Skip common.sh when dispatched. Just rm 2 files.
set -euo pipefail

# Stderr message on unexpected failure (set -e)
trap 'echo "SESSION-CLEANUP FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  CHANGE_LOG="${PROJECT_DIR:-.}/.claude/session-changes.log"
  QA_STATE="${PROJECT_DIR:-.}/.claude/qa-state.json"
else
  HOOK_NAME="SESSION-CLEANUP"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

# Clean up session change log if it wasn't consumed by stop hook
rm -f "${CHANGE_LOG:-}" 2>/dev/null || true

# Clean up qa-state.json (ephemeral per-session, written by qa-preflight)
rm -f "${QA_STATE:-}" 2>/dev/null || true

exit 0
