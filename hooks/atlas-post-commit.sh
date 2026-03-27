#!/bin/bash
#===============================================================================
# Post-commit Hook: Generate atlas after every commit
# Runs asynchronously to avoid slowing down commits
#===============================================================================

ATLAS_DIR="${ATLAS_DIR:-.atlas}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEN_SCRIPT="$(dirname "$SCRIPT_DIR")/scripts/generate_codebase_atlas.sh"

# Only run if not in git operation (prevent loops)
if [[ "${GIT_ATLAS_SKIP:-}" == "1" ]]; then
    exit 0
fi

# Run atlas generation (async, non-blocking)
if [[ -f "$GEN_SCRIPT" ]]; then
    export GIT_ATLAS_SKIP=1
    export ATLAS_QUIET=true

    # Run in background if bash is available
    if command -v bash &>/dev/null; then
        bash "$GEN_SCRIPT" --quiet --output-dir "$ATLAS_DIR" 2>/dev/null &
        disown $! 2>/dev/null || true
    fi
fi

exit 0
