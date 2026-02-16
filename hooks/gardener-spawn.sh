#!/usr/bin/env bash
# gardener-spawn.sh — Agent spawning logic
# Spawns agents to address detected hunger states
# Based on research: hierarchical orchestration + bounded contexts

set -euo pipefail

# Project directory
PROJECT_DIR="${PROJECT_DIR:-$(cd "${BASH_SOURCE[0]%/*}/../.." && pwd)}"
BOUNDED_CONTEXTS_FILE="${PROJECT_DIR}/agents/bounded-contexts.yaml"

# Bounded context to agent mapping (fallback if yaml not available)
declare -A CONTEXT_AGENTS=(
    ["qa"]="qa-test-coverage-expert"
    ["docs"]="code-documentor"
    ["code"]="wbs-task-executor"
    ["governance"]="quality-gatekeeper"
    ["research"]="product-research-analyst"
    ["planning"]="product-orchestrator"
    ["infrastructure"]="ops-concierge"
    ["safety"]="security-auditor"
)

# Load bounded contexts from YAML if available
load_bounded_contexts() {
    if [[ -f "$BOUNDED_CONTEXTS_FILE" ]] && command -v yq &>/dev/null; then
        # Get agents for a context
        local context="$1"
        yq -r ".contexts.${context}.agents[0]" "$BOUNDED_CONTEXTS_FILE" 2>/dev/null || echo ""
    fi
}

# Priority to response time mapping
declare -A PRIORITY_TIMES=(
    ["critical"]="immediate"   # Within 5 min
    ["high"]="within_hour"   # Within 1 hour
    ["medium"]="within_day"  # Within 24 hours
    ["low"]="batch"          # Next batch run
)

# Spawn agent for hunger type
spawn_agent_for_hunger() {
    local hunger_type="$1"
    local priority="$2"

    local agent_type
    case "$hunger_type" in
        test_coverage)
            agent_type="${CONTEXT_AGENTS[qa]}"
            ;;
        lint_violations)
            agent_type="${CONTEXT_AGENTS[qa]}"
            ;;
        doc_disorganization)
            agent_type="${CONTEXT_AGENTS[docs]}"
            ;;
        fragmented_research)
            agent_type="${CONTEXT_AGENTS[research]}"
            ;;
        missing_specs)
            agent_type="${CONTEXT_AGENTS[governance]}"
            ;;
        technical_debt)
            agent_type="${CONTEXT_AGENTS[code]}"
            ;;
        stale_items)
            agent_type="${CONTEXT_AGENTS[governance]}"
            ;;
        agent_failure)
            agent_type="${CONTEXT_AGENTS[governance]}"
            ;;
        *)
            echo "Unknown hunger type: $hunger_type"
            return 1
            ;;
    esac

    echo "Spawning $agent_type for $hunger_type (priority: $priority)"

    # Spawn the agent (thegent spawn or direct call)
    if command -v thegent &>/dev/null; then
        thegent agent run "$agent_type" --hunger="$hunger_type" --priority="$priority" &
    else
        echo "thegent not found, skipping spawn for $hunger_type"
    fi
}

# Prioritize hunger states
prioritize_hungers() {
    local hungers=("$@")
    local critical=() high=() medium=() low=()

    for hunger in "${hungers[@]}"; do
        case "$hunger" in
            test_coverage|lint_violations|agent_failure)
                critical+=("$hunger")
                ;;
            doc_disorganization|fragmented_research)
                high+=("$hunger")
                ;;
            missing_specs|technical_debt)
                medium+=("$hunger")
                ;;
            stale_items)
                low+=("$hunger")
                ;;
        esac
    done

    # Return prioritized list
    echo "critical:${critical[*]}:high:${high[*]}:medium:${medium[*]}:low:${low[*]}"
}

# Main spawn function
gardener_spawn() {
    local detected_hungers="${GARDENER_DETECTED_HUNGERS:-}"
    [[ -z "$detected_hungers" ]] && echo "No hungers to address" && return 0

    echo "Addressing hunger states: $detected_hungers"

    # Convert to array
    IFS=' ' read -ra HUNGER_ARRAY <<< "$detected_hungers"

    # Prioritize
    local priorities
    priorities=$(prioritize_hungers "${HUNGER_ARRAY[@]}")

    # Extract and spawn by priority
    IFS=':' read -ra PRIO_PARTS <<< "$priorities"

    local current_priority="critical"
    for part in "${PRIO_PARTS[@]}"; do
        case "$part" in
            critical) current_priority="critical" ;;
            high) current_priority="high" ;;
            medium) current_priority="medium" ;;
            low) current_priority="low" ;;
            *)
                if [[ -n "$part" && "$part" != " " ]]; then
                    spawn_agent_for_hunger "$part" "$current_priority"
                fi
                ;;
        esac
    done

    echo "Spawn complete"
}

# Run spawn if sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    gardener_spawn
fi
