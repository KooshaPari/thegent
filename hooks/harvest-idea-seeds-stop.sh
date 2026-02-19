#!/bin/zsh
# harvest-idea-seeds-stop.sh — Stop hook
# Harvests $idea prompts from Claude/Codex session history on session end.
# Runs incrementally (offset-based); only processes new entries.
set -euo pipefail

HOOKS_DIR="${BASH_SOURCE[0]%/*}"
HARVEST_SCRIPT="${HOOKS_DIR}/../scripts/harvest-idea-seeds.sh"

[[ -x "$HARVEST_SCRIPT" ]] || exit 0
[[ -n "${PROJECT_DIR:-}" && -d "$PROJECT_DIR" ]] && export PROJECT_DIR
[[ -n "${OUTPUT_DIR:-}" ]] && export OUTPUT_DIR

"$HARVEST_SCRIPT" 2>/dev/null || true
