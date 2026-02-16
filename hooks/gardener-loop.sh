#!/usr/bin/env bash
# gardener-loop.sh — Stop hook + periodic timer
# Main gardener loop that scans for "hunger" states and spawns agents to address them.
# Implements the 4X "game loop" for automatic infrastructure maintenance.
set -euo pipefail

HOOK_NAME="GARDENER-LOOP"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

# Configuration
readonly _CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
readonly _GARDENER_STATE="${PROJECT_DIR}/contracts/garden-state.json"
readonly _GARDENER_CACHE_TTL="${HOOK_CACHE_TTL:-300}"  # 5 min cache

# Gardener loop function
_gardener_loop() {
    echo "GARDENER: Starting loop..."

    # 1. SCAN: Check all hunger states
    echo "GARDENER: Scanning hunger states..."
    source "${BASH_SOURCE[0]%/*}/gardener-scan.sh"

    # 2. PRIORITIZE: Rank responses by urgency
    echo "GARDENER: Prioritizing responses..."

    # 3. ROUTE: Match to bounded context
    echo "GARDENER: Routing to bounded contexts..."

    # 4. EXECUTE: Spawn agents
    echo "GARDENER: Executing responses..."
    source "${BASH_SOURCE[0]%/*}/gardener-spawn.sh"

    # 5. VERIFY: Confirm resolution
    echo "GARDENER: Verifying resolution..."

    # 6. REPORT: Log actions
    echo "GARDENER: Reporting..."

    echo "GARDENER: Loop complete"
}

# Check if we should run
_should_run_gardener() {
    # Run on Stop event
    [[ "${STOP_ACTIVE:-false}" == "true" ]] && return 0

    # Run periodically if timer trigger
    if [[ -n "${GARDENER_TIMER:-}" ]]; then
        return 0
    fi

    # Skip if no garden state file
    [[ -f "$_GARDENER_STATE" ]] || return 1

    return 0
}

# Main execution
if _should_run_gardener; then
    _gardener_loop
fi

exit 0
