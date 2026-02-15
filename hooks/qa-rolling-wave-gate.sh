#!/usr/bin/env bash
# qa-rolling-wave-gate.stub.sh (CDDL-E1)
# Rolling-wave maturity gate with CLI for checking and advancing maturity levels.
# Usage:
#   qa-rolling-wave-gate.sh                    # Validate rolling-wave.json (stdin mode)
#   qa-rolling-wave-gate.sh --check <item-id>  # Check maturity level of an item
#   qa-rolling-wave-gate.sh --advance <item-id> --to <level> [--evidence <ref>]  # Advance maturity
#   qa-rolling-wave-gate.sh --list             # List all items with maturity levels
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Maturity levels in order of progression
declare -A MATURITY_ORDER=(
  ["idea"]=0
  ["hypothesis"]=1
  ["scoped"]=2
  ["implementable"]=3
  ["verified"]=4
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#######################################
# Print usage information
#######################################
usage() {
  cat << 'EOF'
Rolling-Wave Maturity Gate (CDDL-E1)

Usage:
  qa-rolling-wave-gate.sh                    Validate rolling-wave.json (stdin mode)
  qa-rolling-wave-gate.sh --check <item-id>  Check maturity level of an item
  qa-rolling-wave-gate.sh --advance <item-id> --to <level> [options]
  qa-rolling-wave-gate.sh --list             List all items with maturity levels

Commands:
  --check <item-id>      Check if an item is ready for implementation/approval
  --advance <item-id>    Advance an item's maturity level
  --list                 List all items with their current maturity levels

Options for --advance:
  --to <level>           Target maturity level (idea|hypothesis|scoped|implementable|verified)
  --evidence <ref>       Evidence reference to attach (can be used multiple times)
  --force                Skip blocking question checks

Maturity Levels (in order):
  1. idea           - Initial concept, needs exploration
  2. hypothesis     - Proposed approach, needs validation
  3. scoped         - Requirements defined, needs design
  4. implementable  - Ready to build, can be assigned
  5. verified       - Implemented and tested, can be approved

Gate Rules:
  - Requirements at 'verified' level can be marked Approved
  - Requirements below 'implementable' cannot be assigned to implementation
  - Progression requires evidence at each level

Examples:
  qa-rolling-wave-gate.sh --check TASK-RW-001
  qa-rolling-wave-gate.sh --advance TASK-RW-001 --to scoped --evidence "file://docs/spike.md"
  qa-rolling-wave-gate.sh --list
EOF
}

#######################################
# Get maturity level as integer
# Arguments:
#   $1 - maturity level string
# Outputs:
#   Integer value for the level, or -1 if invalid
#######################################
get_maturity_order() {
  local level="$1"
  echo "${MATURITY_ORDER[$level]:--1}"
}

#######################################
# Check if maturity progression is valid
# Arguments:
#   $1 - current level
#   $2 - target level
# Returns:
#   0 if valid, 1 if invalid
#######################################
is_valid_progression() {
  local current="$1"
  local target="$2"
  local current_order target_order

  current_order=$(get_maturity_order "$current")
  target_order=$(get_maturity_order "$target")

  if [[ "$current_order" -eq -1 ]] || [[ "$target_order" -eq -1 ]]; then
    return 1
  fi

  # Allow advancement by one level at a time, or staying at same level
  if [[ "$target_order" -le "$((current_order + 1))" ]]; then
    return 0
  fi
  return 1
}

#######################################
# Check maturity of a specific item
# Arguments:
#   $1 - item ID
#   $2 - rolling-wave.json path
#######################################
check_item() {
  local item_id="$1"
  local rw_file="$2"
  local item maturity_level maturity_obj last_advanced evidence_refs blocking_questions
  local can_assign can_approve

  item=$(jq -e --arg id "$item_id" '.items[] | select(.item_id == $id)' "$rw_file" 2>/dev/null) || {
    echo -e "${RED}ERROR: Item '$item_id' not found${NC}" >&2
    return 2
  }

  # Extract maturity info - support both old string format and new object format
  maturity_obj=$(echo "$item" | jq -r '.maturity // empty')
  if [[ -z "$maturity_obj" ]] || [[ "$maturity_obj" == "null" ]]; then
    maturity_level="idea"
    last_advanced="N/A"
    evidence_refs="[]"
    blocking_questions="[]"
  elif echo "$maturity_obj" | jq -e 'type == "object"' >/dev/null 2>&1; then
    maturity_level=$(echo "$maturity_obj" | jq -r '.level // "idea"')
    last_advanced=$(echo "$maturity_obj" | jq -r '.last_advanced // "N/A"')
    evidence_refs=$(echo "$maturity_obj" | jq -r '.evidence_refs // []')
    blocking_questions=$(echo "$maturity_obj" | jq -r '.blocking_questions // []')
  else
    # Old string format
    maturity_level="$maturity_obj"
    last_advanced=$(echo "$item" | jq -r '.maturity_updated_at // "N/A"')
    evidence_refs="[]"
    blocking_questions="[]"
  fi

  local maturity_order
  maturity_order=$(get_maturity_order "$maturity_level")

  # Determine gate status
  if [[ "$maturity_order" -ge 4 ]]; then
    can_approve="YES"
    can_assign="YES"
  elif [[ "$maturity_order" -ge 3 ]]; then
    can_approve="NO (requires verified)"
    can_assign="YES"
  else
    can_approve="NO (requires verified)"
    can_assign="NO (requires implementable)"
  fi

  echo -e "${GREEN}=== Maturity Check: $item_id ===${NC}"
  echo "Level:            $maturity_level (order: $maturity_order)"
  echo "Last Advanced:    $last_advanced"
  echo "Evidence Refs:    $(echo "$evidence_refs" | jq -r 'if length == 0 then "none" else .[] end')"
  echo "Blocking Qs:      $(echo "$blocking_questions" | jq -r 'if length == 0 then "none" else .[] end')"
  echo ""
  echo -e "Can Assign:       $can_assign"
  echo -e "Can Approve:      $can_approve"

  # Return non-zero if not ready for implementation
  if [[ "$maturity_order" -lt 3 ]]; then
    return 1
  fi
  return 0
}

#######################################
# Advance maturity of an item
# Arguments:
#   $1 - item ID
#   $2 - target level
#   $3 - rolling-wave.json path
#   $4 - evidence refs (JSON array)
#   $5 - force flag (true/false)
#######################################
advance_item() {
  local item_id="$1"
  local target_level="$2"
  local rw_file="$3"
  local evidence_refs="$4"
  local force="$5"
  local current_level maturity_obj blocking_questions

  # Validate target level
  if [[ $(get_maturity_order "$target_level") -eq -1 ]]; then
    echo -e "${RED}ERROR: Invalid maturity level '$target_level'${NC}" >&2
    echo "Valid levels: idea, hypothesis, scoped, implementable, verified" >&2
    return 2
  fi

  # Check item exists
  if ! jq -e --arg id "$item_id" '.items[] | select(.item_id == $id)' "$rw_file" >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Item '$item_id' not found${NC}" >&2
    return 2
  fi

  # Get current maturity
  maturity_obj=$(jq -r --arg id "$item_id" '.items[] | select(.item_id == $id) | .maturity // empty' "$rw_file")
  if [[ -z "$maturity_obj" ]] || [[ "$maturity_obj" == "null" ]]; then
    current_level="idea"
    blocking_questions="[]"
  elif echo "$maturity_obj" | jq -e 'type == "object"' >/dev/null 2>&1; then
    current_level=$(echo "$maturity_obj" | jq -r '.level // "idea"')
    blocking_questions=$(echo "$maturity_obj" | jq -r '.blocking_questions // []')
  else
    current_level="$maturity_obj"
    blocking_questions="[]"
  fi

  # Check for blocking questions unless forced
  if [[ "$force" != "true" ]]; then
    local blocking_count
    blocking_count=$(echo "$blocking_questions" | jq 'length')
    if [[ "$blocking_count" -gt 0 ]]; then
      echo -e "${RED}ERROR: Item has $blocking_count blocking question(s)${NC}" >&2
      echo "Blocking questions: $(echo "$blocking_questions" | jq -r '.[]')" >&2
      echo "Use --force to override" >&2
      return 2
    fi
  fi

  # Validate progression
  if ! is_valid_progression "$current_level" "$target_level"; then
    echo -e "${RED}ERROR: Cannot advance from '$current_level' to '$target_level'${NC}" >&2
    echo "Maturity can only advance one level at a time" >&2
    return 2
  fi

  # Build new maturity object
  local new_maturity
  new_maturity=$(jq -n \
    --arg level "$target_level" \
    --arg last_advanced "$now" \
    --argjson evidence_refs "$evidence_refs" \
    --argjson blocking_questions "$blocking_questions" \
    '{level: $level, last_advanced: $last_advanced, evidence_refs: $evidence_refs, blocking_questions: $blocking_questions}')

  # Update the file
  local temp_file
  temp_file=$(mktemp)
  jq --arg id "$item_id" --argjson maturity "$new_maturity" '
    .items = [.items[] | if .item_id == $id then .maturity = $maturity else . end] |
    .generated_at = "'"$now"'"
  ' "$rw_file" > "$temp_file" && mv "$temp_file" "$rw_file"

  echo -e "${GREEN}SUCCESS: Advanced '$item_id' from '$current_level' to '$target_level'${NC}"
  echo "Updated at: $now"

  # Show gate status for new level
  local target_order
  target_order=$(get_maturity_order "$target_level")
  if [[ "$target_order" -ge 4 ]]; then
    echo -e "${GREEN}This item can now be APPROVED${NC}"
  elif [[ "$target_order" -ge 3 ]]; then
    echo -e "${GREEN}This item can now be ASSIGNED for implementation${NC}"
  fi
}

#######################################
# List all items with maturity levels
# Arguments:
#   $1 - rolling-wave.json path
#######################################
list_items() {
  local rw_file="$1"

  echo -e "${GREEN}=== Rolling-Wave Items ===${NC}"
  echo ""
  printf "%-20s %-15s %-10s %-15s %s\n" "ITEM_ID" "MATURITY" "HORIZON" "CAN_ASSIGN" "EVIDENCE"
  echo "-----------------------------------------------------------------------------------"

  jq -r '.items[] | @base64' "$rw_file" | while read -r item_b64; do
    local item item_id horizon maturity_obj maturity_level evidence_count
    item=$(echo "$item_b64" | base64 -d)
    item_id=$(echo "$item" | jq -r '.item_id')
    horizon=$(echo "$item" | jq -r '.horizon')

    maturity_obj=$(echo "$item" | jq -r '.maturity // empty')
    if [[ -z "$maturity_obj" ]] || [[ "$maturity_obj" == "null" ]]; then
      maturity_level="idea"
      evidence_count=0
    elif echo "$maturity_obj" | jq -e 'type == "object"' >/dev/null 2>&1; then
      maturity_level=$(echo "$maturity_obj" | jq -r '.level // "idea"')
      evidence_count=$(echo "$maturity_obj" | jq '.evidence_refs | length')
    else
      maturity_level="$maturity_obj"
      evidence_count=$(echo "$item" | jq '(.promotion_evidence // []) | length')
    fi

    local maturity_order can_assign
    maturity_order=$(get_maturity_order "$maturity_level")
    if [[ "$maturity_order" -ge 3 ]]; then
      can_assign="YES"
    else
      can_assign="NO"
    fi

    printf "%-20s %-15s %-10s %-15s %d refs\n" "$item_id" "$maturity_level" "$horizon" "$can_assign" "$evidence_count"
  done
}

#######################################
# Validate rolling-wave.json (stdin mode)
# Arguments:
#   $1 - project directory
#######################################
validate_stdin() {
  local project_dir="$1"
  local rw="$project_dir/contracts/rolling-wave.json"
  local schema="$project_dir/schemas/rolling-wave-plan.schema.json"
  local verify_dir="$project_dir/.claude/verification"
  local report="$verify_dir/rolling-wave-gate.json"

  mkdir -p "$verify_dir"

  if [[ ! -f "$rw" ]]; then
    jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$report"
    echo "ROLLING WAVE GATE: pass (no rolling-wave.json)"
    exit 0
  fi

  jq -e . "$rw" >/dev/null 2>&1 || {
    jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"invalid JSON"}' > "$report"
    echo "ROLLING-WAVE FAIL: invalid JSON in rolling-wave.json" >&2
    exit 2
  }

  jq -e '.generated_at and .items' "$rw" >/dev/null 2>&1 || {
    jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"missing required fields"}' > "$report"
    echo "ROLLING-WAVE FAIL: missing required fields (generated_at, items)" >&2
    exit 2
  }

  bad_items="$(jq -r '[.items[]? | select((.item_id | type != "string" or length == 0) or (.state | type != "string") or (.horizon | type != "string") or (.updated_at | type != "string") or (.next_review_at | type != "string"))] | length' "$rw" 2>/dev/null || echo 0)"
  [[ "${bad_items:-0}" -eq 0 ]] || {
    jq -n --arg ts "$now" --argjson c "$bad_items" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"invalid item shape"}' > "$report"
    echo "ROLLING-WAVE FAIL: $bad_items item(s) with invalid shape" >&2
    exit 2
  }

  # CDDL-E1: Maturity gate checks
  # Items with acceptance_ready must be at 'verified' maturity level
  bad_acceptance="$(jq -r '[.items[]? | select(.acceptance_ready == true and (
    (.maturity | type == "object" and (.level // "idea") != "verified") or
    (.maturity | type == "string" and . != "verified") or
    (.maturity | type == "null")
  ))] | length' "$rw" 2>/dev/null || echo 0)"
  [[ "${bad_acceptance:-0}" -eq 0 ]] || {
    jq -n --arg ts "$now" --argjson c "$bad_acceptance" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"acceptance_ready items must be at verified maturity"}' > "$report"
    echo "ROLLING-WAVE FAIL: $bad_acceptance acceptance_ready item(s) not at verified maturity" >&2
    exit 2
  }

  # Items with acceptance_ready must have non-empty promotion_evidence
  bad_forecast="$(jq -r '[.items[]? | select(.acceptance_ready == true and ((.promotion_evidence | type != "array") or (.promotion_evidence | length == 0)))] | length' "$rw" 2>/dev/null || echo 0)"
  [[ "${bad_forecast:-0}" -eq 0 ]] || {
    jq -n --arg ts "$now" --argjson c "$bad_forecast" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"acceptance_ready items require promotion_evidence"}' > "$report"
    echo "ROLLING-WAVE FAIL: $bad_forecast acceptance_ready item(s) missing promotion_evidence" >&2
    exit 2
  }

  # Schema validation - fail hard if schema validation fails
  if [[ -f "$schema" ]] && [[ -f "$REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
    if ! bash "$REPO_ROOT/scripts/validate-json-schema.sh" "$schema" "$rw" 2>/dev/null; then
      jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"schema validation failed"}' > "$report"
      echo "ROLLING WAVE GATE: fail (schema validation)" >&2
      exit 2
    fi
  fi

  jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$report"
  echo "ROLLING WAVE GATE: pass"
  exit 0
}

#######################################
# Main entry point
#######################################
main() {
  local rw_file="${REPO_ROOT}/contracts/rolling-wave.json"
  local evidence_refs="[]"
  local force="false"
  local target_level=""
  local item_id=""

  # No arguments - stdin validation mode
  if [[ $# -eq 0 ]]; then
    INPUT="$(cat)"
    CWD="$(jq -r '.cwd // empty' <<< "$INPUT" 2>/dev/null || echo "")"
    PROJECT_DIR="${CWD:-$(pwd)}"
    validate_stdin "$PROJECT_DIR"
  fi

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --check)
        shift
        if [[ $# -eq 0 ]]; then
          echo -e "${RED}ERROR: --check requires an item-id${NC}" >&2
          exit 2
        fi
        item_id="$1"
        shift
        ;;
      --advance)
        shift
        if [[ $# -eq 0 ]]; then
          echo -e "${RED}ERROR: --advance requires an item-id${NC}" >&2
          exit 2
        fi
        item_id="$1"
        shift
        ;;
      --to)
        shift
        if [[ $# -eq 0 ]]; then
          echo -e "${RED}ERROR: --to requires a level${NC}" >&2
          exit 2
        fi
        target_level="$1"
        shift
        ;;
      --evidence)
        shift
        if [[ $# -eq 0 ]]; then
          echo -e "${RED}ERROR: --evidence requires a reference${NC}" >&2
          exit 2
        fi
        # Append to evidence_refs array
        evidence_refs=$(echo "$evidence_refs" | jq --arg ref "$1" '. + [$ref]')
        shift
        ;;
      --force)
        force="true"
        shift
        ;;
      --list)
        if [[ ! -f "$rw_file" ]]; then
          echo -e "${RED}ERROR: rolling-wave.json not found at $rw_file${NC}" >&2
          exit 2
        fi
        list_items "$rw_file"
        exit 0
        ;;
      *)
        echo -e "${RED}ERROR: Unknown option '$1'${NC}" >&2
        usage >&2
        exit 2
        ;;
    esac
  done

  # Check if file exists for CLI operations
  if [[ ! -f "$rw_file" ]]; then
    echo -e "${RED}ERROR: rolling-wave.json not found at $rw_file${NC}" >&2
    exit 2
  fi

  # Execute commands
  if [[ -n "$item_id" ]]; then
    if [[ -n "$target_level" ]]; then
      # Advance mode
      advance_item "$item_id" "$target_level" "$rw_file" "$evidence_refs" "$force"
    else
      # Check mode
      check_item "$item_id" "$rw_file"
    fi
  else
    # No specific command - show usage
    usage
    exit 1
  fi
}

main "$@"
