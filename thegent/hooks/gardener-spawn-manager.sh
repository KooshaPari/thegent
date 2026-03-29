#!/bin/zsh
# gardener-spawn-manager.sh — Headless agent spawning with resource management
# Manages spawning of Codex agents with context, token, and time budgets
# Based on research: hierarchical orchestration, resource management

set -euo pipefail

# Configuration
readonly _MAX_CONCURRENT="${GARDENER_MAX_CONCURRENT:-5}"
readonly _DEFAULT_TIMEOUT="${GARDENER_TIMEOUT:-300}"  # 5 minutes
readonly _CONTEXT_LIMIT="${GARDENER_CONTEXT_LIMIT:-100000}"  # ~100k tokens
readonly _TOKEN_BUDGET="${GARDENER_TOKEN_BUDGET:-1000000}"  # ~1M tokens
readonly _MIN_USAGE_PERCENT="${GARDENER_MIN_USAGE_PERCENT:-15}"  # Stop at 15% remaining

# State files
readonly _SPAWN_STATE_DIR="${PROJECT_DIR:-.}/.thegent/gardener"
readonly _ACTIVE_AGENTS_FILE="$_SPAWN_STATE_DIR/active-agents.jsonl"
readonly _RESOURCE_USAGE_FILE="$_SPAWN_STATE_DIR/resource-usage.json"

# Ensure state directory exists
mkdir -p "$_SPAWN_STATE_DIR"

# Resource tracking
declare -A AGENT_PIDS=()
declare -A AGENT_START_TIMES=()
declare -A AGENT_CONTEXTS=()

# Check if we can spawn a new agent
can_spawn() {
    local current_count
    current_count=$(get_active_agent_count)

    if [[ "$current_count" -ge "$_MAX_CONCURRENT" ]]; then
        echo "Cannot spawn: max concurrent agents reached ($current_count/$_MAX_CONCURRENT)"
        return 1
    fi

    # Check usage limits (stop at 15% remaining)
    if ! check_usage_limits; then
        return 1
    fi

    return 0
}

# Check usage limits from cost governance
# Stops spawning when usage exceeds threshold (default 85% = 15% remaining)
check_usage_limits() {
    local daily_budget="${GARDENER_DAILY_BUDGET:-10.0}"  # Default $10/day

    # Try to get usage from thegent cost governance
    local current_usage=0
    local usage_percent=0

    # Method 1: Try thegent govern drift (if available)
    if command -v thegent &>/dev/null; then
        local drift_output
        drift_output=$(thegent govern drift 2>/dev/null || echo "")

        # Parse budget usage from output
        if echo "$drift_output" | grep -q "Budget"; then
            current_usage=$(echo "$drift_output" | grep "Budget" | grep -oP '\$[\d.]+' | head -1 | tr -d '$')
        fi
    fi

    # Method 2: Check local usage file if thegent not available
    if [[ "$current_usage" == "0" || -z "$current_usage" ]]; then
        if [[ -f "$_RESOURCE_USAGE_FILE" ]]; then
            current_usage=$(jq -r '.daily_usage_usd // 0' "$_RESOURCE_USAGE_FILE" 2>/dev/null || echo "0")
        fi
    fi

    # Calculate usage percentage
    if [[ -n "$current_usage" && "$current_usage" != "0" ]]; then
        usage_percent=$(echo "scale=2; ($current_usage / $daily_budget) * 100" | bc 2>/dev/null || echo "0")
    fi

    # Check if we've exceeded threshold (85% = 15% remaining)
    local threshold=85
    if (( $(echo "$usage_percent >= $threshold" | bc -l 2>/dev/null || echo 0) )); then
        echo "Cannot spawn: Usage at ${usage_percent}% (threshold: ${threshold}%)"
        echo "Only ${threshold}% budget remaining - pausing agent spawning"
        return 1
    fi

    # Log current usage
    if [[ -n "$current_usage" ]]; then
        echo "Usage: \$${current_usage}/${daily_budget} (${usage_percent}%)"
    fi

    return 0
}

# Update usage tracking
update_usage() {
    local cost="$1"

    # Initialize usage file if needed
    if [[ ! -f "$_RESOURCE_USAGE_FILE" ]]; then
        echo '{"daily_usage_usd": 0, "last_reset": "'"$(date -u +%Y-%m-%d)"'"}' > "$_RESOURCE_USAGE_FILE"
    fi

    # Check if we need to reset (new day)
    local last_reset
    last_reset=$(jq -r '.last_reset' "$_RESOURCE_USAGE_FILE" 2>/dev/null || echo "")
    local today
    today=$(date -u +%Y-%m-%d)

    if [[ "$last_reset" != "$today" ]]; then
        # Reset for new day
        echo '{"daily_usage_usd": 0, "last_reset": "'"$today"'"}' > "$_RESOURCE_USAGE_FILE"
    fi

    # Add cost
    local current
    current=$(jq -r '.daily_usage_usd // 0' "$_RESOURCE_USAGE_FILE")
    local new_total
    new_total=$(echo "$current + $cost" | bc)

    jq --argjson total "$new_total" \
       --arg date "$today" \
       '.daily_usage_usd = $total | .last_reset = $date' \
       "$_RESOURCE_USAGE_FILE" > /tmp/usage_tmp.json

    mv /tmp/usage_tmp.json "$_RESOURCE_USAGE_FILE"
}

# Get count of active agents
get_active_agent_count() {
    if [[ ! -f "$_ACTIVE_AGENTS_FILE" ]]; then
        echo 0
        return
    fi

    local count
    count=$(wc -l < "$_ACTIVE_AGENTS_FILE" 2>/dev/null || echo 0)
    echo "$count"
}

# Get available context budget
get_available_context() {
    local used=0

    if [[ -f "$_RESOURCE_USAGE_FILE" ]]; then
        used=$(jq -r '.context_used // 0' "$_RESOURCE_USAGE_FILE" 2>/dev/null || echo 0)
    fi

    local available=$((_CONTEXT_LIMIT - used))
    echo "$available"
}

# Spawn a headless agent
spawn_agent() {
    local agent_name="$1"
    local task="$2"
    local priority="${3:-medium}"
    local context="${4:-}"

    # Backoff between spawn attempts (ADVANCED_STRATEGIES §2.4)
    local _backoff="${GARDENER_SPAWN_BACKOFF_SEC:-0}"
    [[ "${_backoff:-0}" -gt 0 ]] && sleep "$_backoff"

    # Check resources
    can_spawn || return 1

    local agent_id="agent_$(date +%s)_$$"
    local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    echo "Spawning agent: $agent_name (ID: $agent_id, priority: $priority)"

    # Build the agent prompt
    local prompt="TASK: $task

CONTEXT: $context

PRIORITY: $priority

Execute this task using best practices. Report results in JSON format:
{
  \"status\": \"success|failed\",
  \"artifacts\": [\"file1.md\", ...],
  \"summary\": \"brief summary\",
  \"xp_earned\": 50
}"

    # Run the agent in background
    if command -v codex &>/dev/null; then
        codex -q "$prompt" > "$_SPAWN_STATE_DIR/output_$agent_id.log" 2>&1 &
        local pid=$!
    elif command -v thegent &>/dev/null; then
        thegent agent run "$agent_name" --prompt="$task" --headless > "$_SPAWN_STATE_DIR/output_$agent_id.log" 2>&1 &
        local pid=$!
    else
        echo "No agent runner found (codex or thegent)"
        return 1
    fi

    # Track the agent
    AGENT_PIDS["$agent_id"]=$pid
    AGENT_START_TIMES["$agent_id"]=$start_time
    AGENT_CONTEXTS["$agent_id"]="$agent_name"

    # Write to active agents file
    echo "{\"agent_id\":\"$agent_id\",\"agent_name\":\"$agent_name\",\"pid\":$pid,\"start_time\":\"$start_time\",\"priority\":\"$priority\"}" >> "$_ACTIVE_AGENTS_FILE"

    echo "Agent $agent_id spawned with PID $pid"
    echo "$agent_id"
}

# Check agent status
check_agent_status() {
    local agent_id="$1"

    if [[ ! -f "$_ACTIVE_AGENTS_FILE" ]]; then
        echo "unknown"
        return
    fi

    local pid
    pid=$(jq -r ".pid" "$_ACTIVE_AGENTS_FILE" 2>/dev/null | head -1)

    if [[ -z "$pid" || "$pid" == "null" ]]; then
        echo "unknown"
        return
    fi

    if kill -0 "$pid" 2>/dev/null; then
        echo "running"
    else
        echo "completed"
    fi
}

# Wait for agent completion
wait_for_agent() {
    local agent_id="$1"
    local timeout="${2:-$_DEFAULT_TIMEOUT}"

    local pid
    pid=$(jq -r ".pid" "$_ACTIVE_AGENTS_FILE" 2>/dev/null || echo "")

    if [[ -z "$pid" ]]; then
        echo "Agent $agent_id not found"
        return 1
    fi

    # Wait with timeout
    local elapsed=0
    while kill -0 "$pid" 2>/dev/null; do
        if [[ $elapsed -ge $timeout ]]; then
            echo "Agent $agent_id timed out"
            kill "$pid" 2>/dev/null || true
            return 1
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done

    echo "Agent $agent_id completed"
    return 0
}

# Get agent output
get_agent_output() {
    local agent_id="$1"
    local output_file="$_SPAWN_STATE_DIR/output_$agent_id.log"

    if [[ -f "$output_file" ]]; then
        cat "$output_file"
    else
        echo "No output found for $agent_id"
    fi
}

# Cleanup completed agents
cleanup_agents() {
    local now_agents=()

    if [[ ! -f "$_ACTIVE_AGENTS_FILE" ]]; then
        return
    fi

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue

        local pid
        pid=$(echo "$line" | jq -r '.pid' 2>/dev/null)

        if [[ -n "$pid" && "$pid" != "null" ]] && kill -0 "$pid" 2>/dev/null; then
            now_agents+=("$line")
        fi
    done < "$_ACTIVE_AGENTS_FILE"

    # Rewrite active agents file
    printf '%s\n' "${now_agents[@]}" > "$_ACTIVE_AGENTS_FILE"
}

# Spawn multiple agents in parallel
spawn_parallel() {
    local -a agent_specs=("${@}")
    local -a spawned_ids=()

    for spec in "${agent_specs[@]}"; do
        # spec format: "agent_name|task|priority|context"
        IFS='|' read -r name task priority context <<< "$spec"

        local agent_id
        if agent_id=$(spawn_agent "$name" "$task" "$priority" "$context"); then
            spawned_ids+=("$agent_id")
        fi
    done

    # Return spawned IDs
    printf '%s\n' "${spawned_ids[@]}"
}

# Main when run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        spawn)
            spawn_agent "$2" "$3" "${4:-medium}" "${5:-}"
            ;;
        status)
            check_agent_status "$2"
            ;;
        wait)
            wait_for_agent "$2" "${3:-$_DEFAULT_TIMEOUT}"
            ;;
        output)
            get_agent_output "$2"
            ;;
        count)
            get_active_agent_count
            ;;
        cleanup)
            cleanup_agents
            ;;
        parallel)
            shift
            spawn_parallel "$@"
            ;;
        *)
            echo "Usage: $0 {spawn|status|wait|output|count|cleanup|parallel} [args...]"
            exit 1
            ;;
    esac
fi
