#!/usr/bin/env bash
# gardener-xp.sh — XP and level progression system
# Tracks XP, levels, and achievements for gamification
# Based on research: game mechanics, achievement systems

set -euo pipefail

# Configuration
readonly _XP_STATE_DIR="${PROJECT_DIR:-.}/.thegent/gardener/xp"
readonly _XP_STATE_FILE="$_XP_STATE_DIR/state.json"
readonly _ACHIEVEMENTS_FILE="$_XP_STATE_DIR/achievements.json"
readonly _LEVELS_FILE="$_XP_STATE_DIR/levels.json"

# Default XP awards (from garden-state.json)
declare -A XP_AWARDS=(
    ["research_stage_complete"]=50
    ["quality_gate_pass"]=100
    ["critical_bug_fix"]=75
    ["test_coverage_increase"]=25
    ["implementation_complete"]=150
    ["code_review_pass"]=50
    ["task_complete"]=25
    ["spec_approved"]=75
    ["debt_eliminated"]=50
)

# Level thresholds
declare -A LEVEL_THRESHOLDS=(
    ["1"]=0
    ["2"]=500
    ["3"]=1500
    ["4"]=5000
    ["5"]=15000
)

# Ensure directory exists
mkdir -p "$_XP_STATE_DIR"

# Initialize XP state if not exists
init_xp_state() {
    if [[ ! -f "$_XP_STATE_FILE" ]]; then
        cat > "$_XP_STATE_FILE" <<EOF
{
  "total_xp": 0,
  "level": 1,
  "xp_to_next_level": 500,
  "lifetime_xp": 0,
  "tasks_completed": 0,
  "quality_gates_passed": 0,
  "achievements_unlocked": [],
  "recent_xp": [],
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    fi
}

# Get current XP state
get_xp_state() {
    init_xp_state
    cat "$_XP_STATE_FILE"
}

# Award XP for an action
award_xp() {
    local action="$1"
    local amount="${XP_AWARDS[$action]:-25}"

    init_xp_state

    local current_xp
    current_xp=$(jq -r '.total_xp' "$_XP_STATE_FILE")
    local current_level
    current_level=$(jq -r '.level' "$_XP_STATE_FILE")
    local lifetime_xp
    lifetime_xp=$(jq -r '.lifetime_xp' "$_XP_STATE_FILE")

    local new_xp=$((current_xp + amount))
    local new_lifetime=$((lifetime_xp + amount))

    # Check for level up
    local next_level=$((current_level + 1))
    local xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"

    local leveled_up=false
    while [[ $new_xp -ge $xp_needed && $next_level -le 5 ]]; do
        new_xp=$((new_xp - xp_needed))
        current_level=$next_level
        next_level=$((next_level + 1))
        xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"
        leveled_up=true
    done

    # Update state
    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    jq --argjson new_xp "$new_xp" \
       --argjson level "$current_level" \
       --argjson next_xp "$xp_needed" \
       --argjson lifetime "$new_lifetime" \
       --arg action "$action" \
       --argjson amount "$amount" \
       --arg ts "$timestamp" \
       '.total_xp = $new_xp | .level = $level | .xp_to_next_level = $next_xp | .lifetime_xp = $lifetime | .last_updated = $ts | .recent_xp += [{"action": $action, "amount": $amount, "timestamp": $ts}] | .tasks_completed += 1' \
       "$_XP_STATE_FILE" > /tmp/xp_state_tmp.json

    mv /tmp/xp_state_tmp.json "$_XP_STATE_FILE"

    echo "Awarded +$amount XP for '$action'"

    if [[ "$leveled_up" == "true" ]]; then
        echo "LEVEL UP! Now level $current_level"
    fi
}

# Award XP for quality gate pass
award_quality_gate() {
    init_xp_state

    local current_xp
    current_xp=$(jq -r '.total_xp' "$_XP_STATE_FILE")
    local current_level
    current_level=$(jq -r '.level' "$_XP_STATE_FILE")
    local gates_passed
    gates_passed=$(jq -r '.quality_gates_passed' "$_XP_STATE_FILE")

    local amount=100
    local new_xp=$((current_xp + amount))
    local new_gates=$((gates_passed + 1))

    # Check level up
    local next_level=$((current_level + 1))
    local xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"

    local leveled_up=false
    while [[ $new_xp -ge $xp_needed && $next_level -le 5 ]]; do
        new_xp=$((new_xp - xp_needed))
        current_level=$next_level
        next_level=$((next_level + 1))
        xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"
        leveled_up=true
    done

    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    jq --argjson new_xp "$new_xp" \
       --argjson level "$current_level" \
       --argjson next_xp "$xp_needed" \
       --argjson gates "$new_gates" \
       --arg ts "$timestamp" \
       '.total_xp = $new_xp | .level = $level | .xp_to_next_level = $next_xp | .quality_gates_passed = $gates | .last_updated = $ts' \
       "$_XP_STATE_FILE" > /tmp/xp_state_tmp.json

    mv /tmp/xp_state_tmp.json "$_XP_STATE_FILE"

    echo "Quality gate passed! +$amount XP (total: $new_gates gates)"

    if [[ "$leveled_up" == "true" ]]; then
        echo "LEVEL UP! Now level $current_level"
    fi
}

# Unlock achievement
unlock_achievement() {
    local achievement_id="$1"

    init_xp_state

    local current_achievements
    current_achievements=$(jq -r '.achievements_unlocked[]' "$_XP_STATE_FILE" 2>/dev/null || echo "")

    # Check if already unlocked
    if echo "$current_achievements" | grep -q "^${achievement_id}$"; then
        echo "Achievement '$achievement_id' already unlocked"
        return 0
    fi

    # Get achievement XP reward
    local xp_reward=0
    if [[ -f "$_ACHIEVEMENTS_FILE" ]]; then
        xp_reward=$(jq -r --arg id "$achievement_id" \
            '.achievements[] | select(.id == $id) | .xp_reward' "$_ACHIEVEMENTS_FILE" 2>/dev/null || echo "0")
    fi

    # Add achievement
    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    jq --arg id "$achievement_id" \
       --argjson xp "$xp_reward" \
       --arg ts "$timestamp" \
       '.achievements_unlocked += [{"id": $id, "unlocked_at": $ts}] | .total_xp += $xp | .lifetime_xp += $xp' \
       "$_XP_STATE_FILE" > /tmp/xp_state_tmp.json

    mv /tmp/xp_state_tmp.json "$_XP_STATE_FILE"

    echo "ACHIEVEMENT UNLOCKED: $achievement_id (+$xp_reward XP)"

    # Check for achievement-based level ups
    local current_xp
    current_xp=$(jq -r '.total_xp' "$_XP_STATE_FILE")
    local current_level
    current_level=$(jq -r '.level' "$_XP_STATE_FILE")

    local next_level=$((current_level + 1))
    local xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"

    while [[ $current_xp -ge $xp_needed && $next_level -le 5 ]]; do
        current_xp=$((current_xp - xp_needed))
        current_level=$next_level
        next_level=$((next_level + 1))
        xp_needed="${LEVEL_THRESHOLDS[$next_level]:-999999}"
    done

    if [[ $current_level -gt $(jq -r '.level' "$_XP_STATE_FILE") ]]; then
        jq --argjson level "$current_level" \
           --argjson next_xp "$xp_needed" \
           '.level = $level | .xp_to_next_level = $next_xp | .total_xp = $current_xp' \
           "$_XP_STATE_FILE" > /tmp/xp_state_tmp.json
        mv /tmp/xp_state_tmp.json "$_XP_STATE_FILE"
        echo "LEVEL UP! Now level $current_level"
    fi
}

# Get current level
get_level() {
    init_xp_state
    jq -r '.level' "$_XP_STATE_FILE"
}

# Get XP progress
get_xp_progress() {
    init_xp_state
    jq '{total_xp, level, xp_to_next_level, lifetime_xp, tasks_completed, quality_gates_passed, achievements_count: (.achievements_unlocked | length)}' "$_XP_STATE_FILE"
}

# Get recent XP history
get_xp_history() {
    init_xp_state
    jq '.recent_xp | reverse | .[0:10]' "$_XP_STATE_FILE"
}

# Initialize achievements if not exists
init_achievements() {
    if [[ ! -f "$_ACHIEVEMENTS_FILE" ]]; then
        cat > "$_ACHIEVEMENTS_FILE" <<EOF
{
  "achievements": [
    {"id": "first_blood", "name": "First Blood", "description": "Complete first task", "xp_reward": 10},
    {"id": "quality_guardian", "name": "Quality Guardian", "description": "Pass 10 quality gates", "xp_reward": 100},
    {"id": "research_master", "name": "Research Master", "description": "Complete all research stages", "xp_reward": 200},
    {"id": "speed_demon", "name": "Speed Demon", "description": "Complete task in <5 minutes", "xp_reward": 50},
    {"id": "zero_debt", "name": "Zero Debt", "description": "No technical debt for 7 days", "xp_reward": 150},
    {"id": "coverage_champion", "name": "Coverage Champion", "description": "Reach 90% test coverage", "xp_reward": 100},
    {"id": "documentation_guru", "name": "Documentation Guru", "description": "Complete all doc gaps", "xp_reward": 75},
    {"id": "gardener", "name": "Gardener", "description": "Run 50 gardener loops", "xp_reward": 150},
    {"id": "multi_tasker", "name": "Multi-Tasker", "description": "Have 5 agents running in parallel", "xp_reward": 50},
    {"id": "spec_master", "name": "Spec Master", "description": "Create 10 approved specs", "xp_reward": 200}
  ]
}
EOF
    fi
}

# Check and auto-unlock achievements
check_achievements() {
    init_xp_state
    init_achievements

    local current_achievements
    current_achievements=$(jq -r '.achievements_unlocked[].id' "$_XP_STATE_FILE" 2>/dev/null || echo "")

    local gates_passed
    gates_passed=$(jq -r '.quality_gates_passed' "$_XP_STATE_FILE")

    local tasks_completed
    tasks_completed=$(jq -r '.tasks_completed' "$_XP_STATE_FILE")

    # First blood
    if [[ $tasks_completed -ge 1 ]] && ! echo "$current_achievements" | grep -q "first_blood"; then
        unlock_achievement "first_blood"
    fi

    # Quality guardian
    if [[ $gates_passed -ge 10 ]] && ! echo "$current_achievements" | grep -q "quality_guardian"; then
        unlock_achievement "quality_guardian"
    fi

    # Multi-tasker (check active agents)
    local active_agents
    active_agents=$(get_active_agent_count 2>/dev/null || echo 0)
    if [[ $active_agents -ge 5 ]] && ! echo "$current_achievements" | grep -q "multi_tasker"; then
        unlock_achievement "multi_tasker"
    fi
}

# Helper for checking active agents
get_active_agent_count() {
    local state_dir="${PROJECT_DIR:-.}/.thegent/gardener"
    local active_file="$state_dir/active-agents.jsonl"

    if [[ -f "$active_file" ]]; then
        wc -l < "$active_file"
    else
        echo 0
    fi
}

# Main when run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        award)
            award_xp "$2"
            ;;
        award-gate)
            award_quality_gate
            ;;
        unlock)
            unlock_achievement "$2"
            ;;
        level)
            get_level
            ;;
        progress)
            get_xp_progress
            ;;
        history)
            get_xp_history
            ;;
        check)
            check_achievements
            ;;
        state)
            get_xp_state
            ;;
        *)
            echo "Usage: $0 {award|award-gate|unlock|level|progress|history|check|state} [args...]"
            exit 1
            ;;
    esac
fi
