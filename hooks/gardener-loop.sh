#!/bin/zsh
# gardener-loop.sh — AgilePlus governance loop shim
# This is a backward-compatible shim that calls the new thegent go cycle command.
# The original logic has been replaced by the AgilePlus 4X system in:
#   src/thegent/governance/agileplus.py
#   src/thegent/governance/triggers.py
set -euo pipefail

HOOK_NAME="AGILEPLUS-LOOP"

# Get project root (assumes this script is in hooks/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Run one AgilePlus governance cycle
# Use --force to run even if health >= threshold (for periodic triggers)
exec python -m thegent go cycle --force "$@"
