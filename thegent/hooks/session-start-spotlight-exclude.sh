#!/usr/bin/env zsh
# session-start-spotlight-exclude.sh — SessionStart hook
# Run spotlight-exclude once per environment if not yet done (macOS only).
# Reduces mds_stores CPU/memory during agent runs. Advisory; exit 0.
# See: docs/reference/SWARM_PROCESS_OPTIMIZATIONS.md
set -euo pipefail

# macOS only
[[ "$(uname -s)" = "Darwin" ]] || exit 0

# Opt-in: set THGENT_SPOTLIGHT_EXCLUDE_ON_SESSION_START=1 to enable
[[ "${THGENT_SPOTLIGHT_EXCLUDE_ON_SESSION_START:-0}" == "1" ]] || exit 0

# Use thegent cache dir; STATE_DIR from dispatcher may override
BASE_DIR="${STATE_DIR:-$HOME/.cache/thegent}"
[[ -z "$BASE_DIR" ]] && BASE_DIR="$HOME/.cache/thegent"
FLAG_FILE="$BASE_DIR/.spotlight-excluded"

mkdir -p "$BASE_DIR"
[[ -f "$FLAG_FILE" ]] && exit 0

if command -v thegent >/dev/null 2>&1; then
  thegent mcp spotlight-exclude 2>/dev/null || true
  touch "$FLAG_FILE" 2>/dev/null || true
fi

exit 0
