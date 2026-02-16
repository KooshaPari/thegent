#!/usr/bin/env bash
# gardener-parallel.sh — Parallel agent execution coordinator
# Manages running multiple agents simultaneously with proper resource management
# Based on research: LangGraph parallel execution, swarm coordination

set -euo pipefail

# Configuration
readonly _MAX_PARALLEL="${GARDENER_MAX_PARALLEL:-5}"
readonly _PARALLEL_STATE_DIR="${PROJECT_DIR:-.}/.thegent/gardener/parallel"
readonly _TASKS_FILE="$_PARALLEL_STATE_DIR/tasks.json"
readonly _RESULTS_DIR="$_PARALLEL_STATE_DIR/results"

# Ensure directories exist
mkdir -p "$_PARALLEL_STATE_DIR"
mkdir -p "$_RESULTS_DIR"

# Task states
declare -A TASK_STATES=(
    ["pending"]="pending"
    ["running"]="running"
    ["completed"]="completed"
    ["failed"]="failed"
    ["cancelled"]="cancelled"
)

# Initialize tasks file
init_tasks() {
    if [[ ! -f "$_TASKS_FILE" ]]; then
        echo '{"tasks": [], "next_id": 1}' > "$_TASKS_FILE"
    fi
}

# Add a task to the queue
task_add() {
    local agent_name="$1"
    local task_description="$2"
    local priority="${3:-medium}"
    local context="${4:-}"

    init_tasks

    local task_id
    task_id=$(jq -r '.next_id' "$_TASKS_FILE")

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    local new_task=$(cat <<EOF
{
  "id": $task_id,
  "agent_name": "$agent_name",
  "description": "$task_description",
  "priority": "$priority",
  "context": "$context",
  "state": "pending",
  "created_at": "$timestamp",
  "started_at": null,
  "completed_at": null,
  "result": null,
  "error": null
}
EOF
)

    # Add task and increment next_id
    jq --argjson task "$new_task" \
        '.tasks += [$task] | .next_id = .next_id + 1' \
        "$_TASKS_FILE" > /tmp/tasks_tmp.json

    mv /tmp/tasks_tmp.json "$_TASKS_FILE"

    echo "Task $task_id added: $agent_name - $task_description"
    echo "$task_id"
}

# Get pending tasks sorted by priority
task_get_pending() {
    init_tasks

    # Priority order: critical > high > medium > low
    jq -r '.tasks | map(select(.state == "pending")) | sort_by(
        if .priority == "critical" then 0
        elif .priority == "high" then 1
        elif .priority == "medium" then 2
        else 3 end
    ) | .[0:'"$_MAX_PARALLEL"' | .[] | .id' "$_TASKS_FILE" 2>/dev/null
}

# Start a task
task_start() {
    local task_id="$1"

    init_tasks

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    jq --argjson id "$task_id" \
       --arg ts "$timestamp" \
       '(.tasks[] | select(.id == $id)) | .state = "running" | .started_at = $ts' \
       "$_TASKS_FILE" > /tmp/tasks_tmp.json

    mv /tmp/tasks_tmp.json "$_TASKS_FILE"

    echo "Task $task_id started"
}

# Complete a task
task_complete() {
    local task_id="$1"
    local result="$2"

    init_tasks

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    # Save result to file
    echo "$result" > "$_RESULTS_DIR/result_$task_id.json"

    jq --argjson id "$task_id" \
       --arg ts "$timestamp" \
       --arg result "result_$task_id.json" \
       '(.tasks[] | select(.id == $id)) | .state = "completed" | .completed_at = $ts | .result = $result' \
       "$_TASKS_FILE" > /tmp/tasks_tmp.json

    mv /tmp/tasks_tmp.json "$_TASKS_FILE"

    echo "Task $task_id completed"
}

# Fail a task
task_fail() {
    local task_id="$1"
    local error="$2"

    init_tasks

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    jq --argjson id "$task_id" \
       --arg ts "$timestamp" \
       --arg err "$error" \
       '(.tasks[] | select(.id == $id)) | .state = "failed" | .completed_at = $ts | .error = $err' \
       "$_TASKS_FILE" > /tmp/tasks_tmp.json

    mv /tmp/tasks_tmp.json "$_TASKS_FILE"

    echo "Task $task_id failed: $error"
}

# Get task info
task_get() {
    local task_id="$1"

    init_tasks
    jq --argjson id "$task_id" '.tasks[] | select(.id == $id)' "$_TASKS_FILE"
}

# Get running task count
get_running_count() {
    init_tasks
    jq '[.tasks[] | select(.state == "running")] | length' "$_TASKS_FILE"
}

# Get pending task count
get_pending_count() {
    init_tasks
    jq '[.tasks[] | select(.state == "pending")] | length' "$_TASKS_FILE"
}

# Get completed task count
get_completed_count() {
    init_tasks
    jq '[.tasks[] | select(.state == "completed")] | length' "$_TASKS_FILE"
}

# Run pending tasks in parallel
run_parallel() {
    local max_concurrent="${1:-$_MAX_PARALLEL}"

    local running
    running=$(get_running_count)

    # Check if we can run more
    while [[ $running -lt $max_concurrent ]]; do
        local pending
        pending=$(task_get_pending)

        if [[ -z "$pending" ]]; then
            break
        fi

        # Get first pending task
        local task_id
        task_id=$(echo "$pending" | head -1)

        # Get task details
        local agent_name
        agent_name=$(jq --argjson id "$task_id" -r '.tasks[] | select(.id == $id) | .agent_name' "$_TASKS_FILE")

        local description
        description=$(jq --argjson id "$task_id" -r '.tasks[] | select(.id == $id) | .description' "$_TASKS_FILE")

        local context
        context=$(jq --argjson id "$task_id" -r '.tasks[] | select(.id == $id) | .context' "$_TASKS_FILE")

        # Start the task
        task_start "$task_id"

        # Run in background
        (
            if command -v codex &>/dev/null; then
                local output
                output=$(codex -q "TASK: $description" 2>&1) || true
                task_complete "$task_id" "$output"
            elif command -v thegent &>/dev/null; then
                local output
                output=$(thegent agent run "$agent_name" --prompt="$description" --headless 2>&1) || true
                task_complete "$task_id" "$output"
            else
                task_fail "$task_id" "No agent runner found"
            fi
        ) &

        running=$((running + 1))
    done

    echo "Running $running tasks"
}

# Wait for all running tasks to complete
wait_for_completion() {
    local timeout="${1:-300}"

    while true; do
        local running
        running=$(get_running_count)

        if [[ $running -eq 0 ]]; then
            break
        fi

        if [[ $timeout -le 0 ]]; then
            echo "Timeout waiting for tasks to complete"
            return 1
        fi

        sleep 1
        timeout=$((timeout - 1))
    done

    echo "All tasks completed"
    return 0
}

# Get all task results
get_all_results() {
    init_tasks
    jq '.tasks | map(select(.state == "completed")) | .[] | {id, agent_name, description, result}' "$_TASKS_FILE"
}

# Get task statistics
get_stats() {
    init_tasks
    jq '{
        total: (.tasks | length),
        pending: ([.tasks[] | select(.state == "pending")] | length),
        running: ([.tasks[] | select(.state == "running")] | length),
        completed: ([.tasks[] | select(.state == "completed")] | length),
        failed: ([.tasks[] | select(.state == "failed")] | length)
    }' "$_TASKS_FILE"
}

# Clear completed tasks
clear_completed() {
    init_tasks
    jq '.tasks = [.tasks[] | select(.state != "completed" and .state != "failed")]' "$_TASKS_FILE" > /tmp/tasks_tmp.json
    mv /tmp/tasks_tmp.json "$_TASKS_FILE"
    echo "Cleared completed tasks"
}

# Main when run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        add)
            task_add "$2" "$3" "${4:-medium}" "${5:-}"
            ;;
        start)
            task_start "$2"
            ;;
        complete)
            task_complete "$2" "$3"
            ;;
        fail)
            task_fail "$2" "$3"
            ;;
        get)
            task_get "$2"
            ;;
        pending)
            task_get_pending
            ;;
        running)
            get_running_count
            ;;
        stats)
            get_stats
            ;;
        run)
            run_parallel "${2:-$_MAX_PARALLEL}"
            ;;
        wait)
            wait_for_completion "${2:-300}"
            ;;
        results)
            get_all_results
            ;;
        clear)
            clear_completed
            ;;
        *)
            echo "Usage: $0 {add|start|complete|fail|get|pending|running|stats|run|wait|results|clear} [args...]"
            exit 1
            ;;
    esac
fi
