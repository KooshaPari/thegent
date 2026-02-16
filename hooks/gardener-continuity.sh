#!/usr/bin/env bash
# gardener-continuity.sh — Continuity packet handoff system
# Enables structured handoffs between agents in different phases
# Based on research: DDD context maps, CrewAI structured output

set -euo pipefail

# Configuration
readonly _CONTINUITY_DIR="${PROJECT_DIR:-.}/.thegent/gardener/continuity"
readonly _PACKET_TEMPLATE='{
  "packet_id": "",
  "run_id": "",
  "phase": "",
  "progress": 0.0,
  "summary": "",
  "next_action": "",
  "owner": "",
  "handoff_to": "",
  "artifacts": [],
  "context": {},
  "created_at": "",
  "completed_at": null
}'

# Ensure directory exists
mkdir -p "$_CONTINUITY_DIR"

# Generate unique packet ID
generate_packet_id() {
    echo "cp_$(date +%s)_$$"
}

# Generate run ID
generate_run_id() {
    echo "run_$(date +%s)_$$"
}

# Create a new continuity packet
packet_create() {
    local phase="$1"
    local owner="$2"
    local handoff_to="$3"

    local packet_id
    packet_id=$(generate_packet_id)
    local run_id
    run_id=$(generate_run_id)
    local created_at
    created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    local packet
    packet=$(echo "$_PACKET_TEMPLATE" | jq \
        --arg id "$packet_id" \
        --arg run "$run_id" \
        --arg p "$phase" \
        --arg o "$owner" \
        --arg h "$handoff_to" \
        --arg ca "$created_at" \
        '.packet_id = $id | .run_id = $run | .phase = $p | .owner = $o | .handoff_to = $h | .created_at = $ca')

    echo "$packet"
}

# Update packet fields
packet_update() {
    local packet_file="$1"
    local field="$2"
    local value="$3"

    if [[ ! -f "$packet_file" ]]; then
        echo "Packet file not found: $packet_file"
        return 1
    fi

    local updated
    updated=$(jq --arg f "$field" --argjson v "$value" \
        'setpath($f | split("."); $v)' "$packet_file")

    echo "$updated" > "$packet_file"
}

# Add artifact to packet
packet_add_artifact() {
    local packet_file="$1"
    local artifact="$2"

    if [[ ! -f "$packet_file" ]]; then
        echo "Packet file not found: $packet_file"
        return 1
    fi

    local updated
    updated=$(jq --arg a "$artifact" \
        '.artifacts += [$a]' "$packet_file")

    echo "$updated" > "$packet_file"
}

# Add context to packet
packet_add_context() {
    local packet_file="$1"
    local key="$2"
    local value="$3"

    if [[ ! -f "$packet_file" ]]; then
        echo "Packet file not found: $packet_file"
        return 1
    fi

    local updated
    updated=$(jq --arg k "$key" --arg v "$value" \
        '.context[$k] = $v' "$packet_file")

    echo "$updated" > "$packet_file"
}

# Save packet to file
packet_save() {
    local packet_json="$1"
    local packet_id
    packet_id=$(echo "$packet_json" | jq -r '.packet_id')

    echo "$packet_json" > "$_CONTINUITY_DIR/${packet_id}.json"
    echo "$_CONTINUITY_DIR/${packet_id}.json"
}

# Load packet from file
packet_load() {
    local packet_id="$1"
    local packet_file="$_CONTINUITY_DIR/${packet_id}.json"

    if [[ -f "$packet_file" ]]; then
        cat "$packet_file"
    else
        echo "{}"
    fi
}

# Mark packet complete
packet_complete() {
    local packet_file="$1"
    local summary="$2"

    if [[ ! -f "$packet_file" ]]; then
        echo "Packet file not found: $packet_file"
        return 1
    fi

    local completed_at
    completed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    local updated
    updated=$(jq --arg s "$summary" --arg ca "$completed_at" \
        '.summary = $s | .completed_at = $ca | .progress = 1.0' "$packet_file")

    echo "$updated" > "$packet_file"
}

# Get packets by phase
packet_list_by_phase() {
    local phase="$1"

    find "$_CONTINUITY_DIR" -name "*.json" -exec jq -r \
        --arg p "$phase" \
        'select(.phase == $p) | .packet_id' {} \; 2>/dev/null
}

# Get pending handoffs
packet_pending_handoffs() {
    find "$_CONTINUITY_DIR" -name "*.json" -exec jq -r \
        'select(.completed_at == null) | .packet_id' {} \; 2>/dev/null
}

# Get completed packets
packet_completed() {
    find "$_CONTINUITY_DIR" -name "*.json" -exec jq -r \
        'select(.completed_at != null) | .packet_id' {} \; 2>/dev/null
}

# Archive completed packet
packet_archive() {
    local packet_id="$1"
    local archive_dir="$_CONTINUITY_DIR/archive"
    mkdir -p "$archive_dir"

    local packet_file="$_CONTINUITY_DIR/${packet_id}.json"
    if [[ -f "$packet_file" ]]; then
        mv "$packet_file" "$archive_dir/"
    fi
}

# Extract handoff info for next agent
packet_get_handoff() {
    local packet_id="$1"

    local packet_file="$_CONTINUITY_DIR/${packet_id}.json"
    if [[ ! -f "$packet_file" ]]; then
        echo "{}"
        return
    fi

    jq '{
        next_action: .next_action,
        handoff_to: .handoff_to,
        progress: .progress,
        summary: .summary,
        artifacts: .artifacts,
        context: .context
    }' "$packet_file"
}

# Main when run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        create)
            packet_create "$2" "$3" "$4"
            ;;
        save)
            packet_save "$2"
            ;;
        load)
            packet_load "$2"
            ;;
        complete)
            packet_complete "$2" "$3"
            ;;
        add-artifact)
            packet_add_artifact "$2" "$3"
            ;;
        add-context)
            packet_add_context "$2" "$3" "$4"
            ;;
        list-by-phase)
            packet_list_by_phase "$2"
            ;;
        pending)
            packet_pending_handoffs
            ;;
        completed)
            packet_completed
            ;;
        handoff)
            packet_get_handoff "$2"
            ;;
        archive)
            packet_archive "$2"
            ;;
        *)
            echo "Usage: $0 {create|save|load|complete|add-artifact|add-context|list-by-phase|pending|completed|handoff|archive} [args...]"
            exit 1
            ;;
    esac
fi
