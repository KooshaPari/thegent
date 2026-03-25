#!/bin/bash
#===============================================================================
# Pre-push Hook: Generate atlas before push
# Updates atlas and optionally amends the commit with atlas changes
#===============================================================================

ATLAS_DIR="${ATLAS_DIR:-.atlas}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEN_SCRIPT="$(dirname "$SCRIPT_DIR")/scripts/generate_codebase_atlas.sh"

echo "[Atlas] Generating codebase atlas before push..."

# Run atlas generation
if [[ -f "$GEN_SCRIPT" ]]; then
    export ATLAS_QUIET=false

    if bash "$GEN_SCRIPT" --quiet --output-dir "$ATLAS_DIR" 2>&1; then
        echo "[Atlas] Atlas generated successfully"

        # Check if there are atlas changes
        if git diff --stat "$ATLAS_DIR" 2>/dev/null | grep -q .; then
            echo "[Atlas] Atlas files changed. Staging..."
            git add "$ATLAS_DIR/"

            # Optionally amend commit
            # Uncomment the following to include atlas in the commit:
            # if git commit --amend --no-edit 2>/dev/null; then
            #     echo "[Atlas] Committed atlas changes"
            # else
            #     echo "[Atlas] Warning: Could not amend commit"
            # fi
        else
            echo "[Atlas] No changes to atlas"
        fi
    else
        echo "[Atlas] Warning: Atlas generation failed"
    fi
else
    echo "[Atlas] Warning: Generator script not found at $GEN_SCRIPT"
fi

exit 0
