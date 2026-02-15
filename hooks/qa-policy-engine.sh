#!/usr/bin/env bash
# qa-policy-engine.sh (P8 + VP-C1)
# Policy-as-Code: OPA eval on quality.json + policies. Fail-closed defaults.
# VP-C1: Full break-glass support with reason, approver, expiry, and audit log.
set -euo pipefail

# --- Constants and Paths ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERIFY_DIR="$REPO_ROOT/.claude/verification"
VAR_DIR="$REPO_ROOT/var"
BREAK_GLASS_AUDIT="$VAR_DIR/break-glass-audit.log"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- Ensure directories exist ---
mkdir -p "$VERIFY_DIR"
mkdir -p "$VAR_DIR"

# --- Utility Functions ---
log_audit() {
  local entry="$1"
  echo "$entry" >> "$BREAK_GLASS_AUDIT"
}

generate_uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    # Fallback using /dev/urandom
    od -x /dev/urandom | head -1 | awk '{print $2$3$4"-"$5"-"$6"-"$7"-"$8$9$10$11}'
  fi
}

get_git_context() {
  # Cache git context to avoid repeated git spawns across multiple calls
  if [[ -n "${_GIT_CONTEXT_CACHE:-}" ]]; then
    echo "$_GIT_CONTEXT_CACHE"
    return
  fi
  local branch commit
  branch="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
  commit="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown')"
  local ci_job="${CI_JOB_ID:-${GITHUB_RUN_ID:-${BUILD_ID:-local}}}"
  _GIT_CONTEXT_CACHE="{\"branch\": \"$branch\", \"commit\": \"$commit\", \"ci_job\": \"$ci_job\"}"
  echo "$_GIT_CONTEXT_CACHE"
}

is_expired() {
  local expiry="$1"
  local now_epoch expiry_epoch

  # Convert to epoch seconds for comparison
  if date --version >/dev/null 2>&1; then
    # GNU date
    now_epoch="$(date -u +%s)"
    expiry_epoch="$(date -u -d "$expiry" +%s 2>/dev/null || echo 0)"
  else
    # BSD date (macOS)
    now_epoch="$(date -u +%s)"
    expiry_epoch="$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$expiry" +%s 2>/dev/null || echo 0)"
  fi

  [[ $now_epoch -ge $expiry_epoch ]]
}

find_break_glass_by_id() {
  local id="$1"
  if [[ -f "$BREAK_GLASS_AUDIT" ]]; then
    # Use single jq call to find matching record instead of per-line parsing.
    # Reads entire file, filters for matching id+action in one pass.
    local result
    result="$(jq -c --arg id "$id" 'select(.id == $id and .action == "create")' "$BREAK_GLASS_AUDIT" 2>/dev/null | tail -1)"
    [[ -n "$result" ]] && echo "$result"
  fi
}

get_current_status() {
  local id="$1"

  # Single jq call to check for revoke action (instead of per-line loop)
  if [[ -f "$BREAK_GLASS_AUDIT" ]]; then
    local revoke_found
    revoke_found="$(jq -c --arg id "$id" 'select(.id == $id and .action == "revoke")' "$BREAK_GLASS_AUDIT" 2>/dev/null | head -1)"
    if [[ -n "$revoke_found" ]]; then
      echo "revoked"
      return
    fi
  fi

  # Then find the create record
  local record
  record="$(find_break_glass_by_id "$id")"

  if [[ -z "$record" ]]; then
    echo "not_found"
    return
  fi

  # Extract status and expiry in a single jq call (instead of 2 separate calls)
  local _fields
  _fields="$(echo "$record" | jq -r '[.status, .expiry] | @tsv' 2>/dev/null)"
  local status expiry
  IFS=$'\t' read -r status expiry <<< "$_fields"

  if is_expired "$expiry"; then
    echo "expired"
    return
  fi

  echo "active"
}

# --- Break-Glass Commands ---

break_glass_create() {
  local policy="${1:-}"
  local requirement="${2:-}"
  local reason="${3:-}"
  local approver="${4:-}"
  local expiry_hours="${5:-24}"
  local actor="${6:-$(whoami)@$(hostname 2>/dev/null || echo 'local')}"

  # Validate required fields
  if [[ -z "$policy" ]]; then
    echo "ERROR: --policy is required" >&2
    echo "Usage: qa-policy-engine.sh break-glass create --policy <name> --requirement <FR-XXX-NNN> --reason <text> --approver <email> [--expiry-hours <N>]" >&2
    return 1
  fi

  if [[ -z "$requirement" ]]; then
    echo "ERROR: --requirement is required (format: FR-XXX-NNN)" >&2
    return 1
  fi

  # Validate requirement format
  if ! [[ "$requirement" =~ ^FR-[A-Z]+-[0-9]{3}$ ]]; then
    echo "ERROR: Invalid requirement format. Expected FR-XXX-NNN (e.g., FR-QA-001)" >&2
    return 1
  fi

  if [[ -z "$reason" ]]; then
    echo "ERROR: --reason is required" >&2
    return 1
  fi

  if [[ ${#reason} -lt 10 ]]; then
    echo "ERROR: --reason must be at least 10 characters" >&2
    return 1
  fi

  if [[ -z "$approver" ]]; then
    echo "ERROR: --approver is required (email format)" >&2
    return 1
  fi

  # Validate approver email format
  if ! [[ "$approver" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "ERROR: Invalid approver email format" >&2
    return 1
  fi

  # Generate break-glass ID
  local bg_id
  bg_id="bg-$(generate_uuid)"

  # Calculate expiry timestamp
  local expiry
  if date --version >/dev/null 2>&1; then
    # GNU date
    expiry="$(date -u -d "+${expiry_hours} hours" +%Y-%m-%dT%H:%M:%SZ)"
  else
    # BSD date (macOS)
    expiry="$(date -u -v+${expiry_hours}H +%Y-%m-%dT%H:%M:%SZ)"
  fi

  # Get context
  local context
  context="$(get_git_context)"

  # Create audit record (compact single-line JSON)
  local record
  record="$(jq -n -c \
    --arg id "$bg_id" \
    --arg ts "$now" \
    --arg action "create" \
    --arg policy "$policy" \
    --arg requirement "$requirement" \
    --arg reason "$reason" \
    --arg approver "$approver" \
    --arg expiry "$expiry" \
    --arg status "active" \
    --arg actor "$actor" \
    --argjson context "$context" \
    '{
      id: $id,
      timestamp: $ts,
      action: $action,
      policy: $policy,
      requirement: $requirement,
      reason: $reason,
      approver: $approver,
      expiry: $expiry,
      status: $status,
      actor: $actor,
      context: $context
    }')"

  # Write to audit log
  log_audit "$record"

  # Output result
  echo "BREAK-GLASS CREATED"
  echo "  ID: $bg_id"
  echo "  Policy: $policy"
  echo "  Requirement: $requirement"
  echo "  Approver: $approver"
  echo "  Expiry: $expiry"
  echo "  Status: active"
  echo ""
  echo "Use this ID to validate: qa-policy-engine.sh break-glass validate $bg_id"

  return 0
}

break_glass_validate() {
  local id="${1:-}"
  local actor="${2:-$(whoami)@$(hostname 2>/dev/null || echo 'local')}"

  if [[ -z "$id" ]]; then
    echo "ERROR: Break-glass ID is required" >&2
    echo "Usage: qa-policy-engine.sh break-glass validate <id>" >&2
    return 1
  fi

  # Validate ID format
  if ! [[ "$id" =~ ^bg-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$ ]]; then
    echo "ERROR: Invalid break-glass ID format" >&2
    return 1
  fi

  # Get current status
  local current_status
  current_status="$(get_current_status "$id")"

  local valid="false"
  local failure_reason=""

  case "$current_status" in
    active)
      valid="true"
      ;;
    expired)
      failure_reason="expired"
      ;;
    revoked)
      failure_reason="revoked"
      ;;
    not_found)
      failure_reason="not_found"
      ;;
    *)
      failure_reason="malformed"
      ;;
  esac

  # Get context
  local context
  context="$(get_git_context)"

  # Get original record for context
  local original_record
  original_record="$(find_break_glass_by_id "$id")"

  # Extract all fields from original_record in a single jq call (instead of 5 separate calls)
  local _orig_fields orig_policy orig_requirement orig_reason orig_approver orig_expiry
  if [[ -n "$original_record" ]]; then
    _orig_fields="$(echo "$original_record" | jq -r '[(.policy // "unknown"), (.requirement // "unknown"), (.reason // "unknown"), (.approver // "unknown"), (.expiry // "unknown")] | @tsv' 2>/dev/null)"
    IFS=$'\t' read -r orig_policy orig_requirement orig_reason orig_approver orig_expiry <<< "$_orig_fields"
  else
    orig_policy="unknown"; orig_requirement="unknown"; orig_reason="unknown"
    orig_approver="unknown"; orig_expiry="unknown"
  fi

  # Create validation audit record (compact single-line JSON, single jq call)
  local record
  record="$(jq -n -c \
    --arg id "$id" \
    --arg ts "$now" \
    --arg action "validate" \
    --arg policy "$orig_policy" \
    --arg requirement "$orig_requirement" \
    --arg reason "$orig_reason" \
    --arg approver "$orig_approver" \
    --arg expiry "$orig_expiry" \
    --arg status "$current_status" \
    --arg actor "$actor" \
    --argjson context "$context" \
    --argjson valid "$valid" \
    --arg failure_reason "$failure_reason" \
    '{
      id: $id,
      timestamp: $ts,
      action: $action,
      policy: $policy,
      requirement: $requirement,
      reason: $reason,
      approver: $approver,
      expiry: $expiry,
      status: $status,
      actor: $actor,
      context: $context,
      validation_result: {
        valid: $valid,
        failure_reason: (if $failure_reason == "" then null else $failure_reason end)
      }
    }')"

  # Write to audit log
  log_audit "$record"

  # Output result and return appropriate exit code
  if [[ "$valid" == "true" ]]; then
    echo "BREAK-GLASS VALID: $id"
    echo "  Status: $current_status"
    return 0
  else
    echo "BREAK-GLASS INVALID: $id" >&2
    echo "  Status: $current_status" >&2
    echo "  Reason: $failure_reason" >&2
    return 1
  fi
}

break_glass_list() {
  local filter="${1:-active}"

  if [[ ! -f "$BREAK_GLASS_AUDIT" ]]; then
    echo "No break-glass records found"
    return 0
  fi

  echo "Break-Glass Records (filter: $filter)"
  echo "========================================="

  # Single jq call to extract all create record IDs and fields (instead of per-line parsing)
  local create_records
  create_records="$(jq -r 'select(.action == "create") | [.id, .policy, .requirement, .approver, .expiry] | @tsv' "$BREAK_GLASS_AUDIT" 2>/dev/null | sort -u -t$'\t' -k1,1)"

  if [[ -z "$create_records" ]]; then
    echo "No break-glass records found"
    return 0
  fi

  local count=0
  while IFS=$'\t' read -r id policy requirement approver expiry; do
    [[ -z "$id" ]] && continue

    local status
    status="$(get_current_status "$id")"

    # Apply filter
    if [[ "$filter" != "all" && "$status" != "$filter" ]]; then
      continue
    fi

    count=$((count + 1))

    echo ""
    echo "ID: $id"
    echo "  Policy: $policy"
    echo "  Requirement: $requirement"
    echo "  Approver: $approver"
    echo "  Expiry: $expiry"
    echo "  Status: $status"
  done <<< "$create_records"

  echo ""
  echo "Total: $count record(s)"
}

break_glass_revoke() {
  local id="${1:-}"
  local revocation_reason="${2:-No reason provided}"
  local actor="${3:-$(whoami)@$(hostname 2>/dev/null || echo 'local')}"

  if [[ -z "$id" ]]; then
    echo "ERROR: Break-glass ID is required" >&2
    echo "Usage: qa-policy-engine.sh break-glass revoke <id> [reason]" >&2
    return 1
  fi

  # Validate ID format
  if ! [[ "$id" =~ ^bg-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$ ]]; then
    echo "ERROR: Invalid break-glass ID format" >&2
    return 1
  fi

  # Check if exists
  local original_record
  original_record="$(find_break_glass_by_id "$id")"

  if [[ -z "$original_record" ]]; then
    echo "ERROR: Break-glass record not found: $id" >&2
    return 1
  fi

  # Check current status
  local current_status
  current_status="$(get_current_status "$id")"

  if [[ "$current_status" == "revoked" ]]; then
    echo "WARNING: Break-glass already revoked: $id"
    return 0
  fi

  # Get context
  local context
  context="$(get_git_context)"

  # Extract all fields from original_record in a single jq call (instead of 4 separate calls)
  local _orig_fields orig_policy orig_requirement orig_reason orig_approver orig_expiry
  _orig_fields="$(echo "$original_record" | jq -r '[.policy, .requirement, .reason, .approver, .expiry] | @tsv' 2>/dev/null)"
  IFS=$'\t' read -r orig_policy orig_requirement orig_reason orig_approver orig_expiry <<< "$_orig_fields"

  # Create revocation audit record (compact single-line JSON, single jq call)
  local record
  record="$(jq -n -c \
    --arg id "$id" \
    --arg ts "$now" \
    --arg action "revoke" \
    --arg policy "$orig_policy" \
    --arg requirement "$orig_requirement" \
    --arg reason "$orig_reason" \
    --arg approver "$orig_approver" \
    --arg expiry "$orig_expiry" \
    --arg status "revoked" \
    --arg actor "$actor" \
    --argjson context "$context" \
    --arg revoked_by "$actor" \
    --arg revocation_reason "$revocation_reason" \
    '{
      id: $id,
      timestamp: $ts,
      action: $action,
      policy: $policy,
      requirement: $requirement,
      reason: $reason,
      approver: $approver,
      expiry: $expiry,
      status: $status,
      actor: $actor,
      context: $context,
      revoked_by: $revoked_by,
      revocation_reason: $revocation_reason
    }')"

  # Write to audit log
  log_audit "$record"

  echo "BREAK-GLASS REVOKED: $id"
  echo "  Reason: $revocation_reason"
  echo "  Revoked by: $actor"

  return 0
}

break_glass_usage() {
  cat << 'EOF'
Break-Glass Override System
===========================

Emergency policy bypass with full audit trail.

Commands:
  create     Create a new break-glass override
  validate   Validate an existing break-glass override
  list       List break-glass records
  revoke     Revoke an active break-glass override

Usage:
  qa-policy-engine.sh break-glass create --policy <name> --requirement <FR-XXX-NNN> --reason <text> --approver <email> [--expiry-hours <N>]
  qa-policy-engine.sh break-glass validate <id>
  qa-policy-engine.sh break-glass list [active|expired|revoked|all]
  qa-policy-engine.sh break-glass revoke <id> [reason]

Examples:
  # Create a break-glass for emergency production fix
  qa-policy-engine.sh break-glass create \
    --policy "quality-gate" \
    --requirement "FR-QA-001" \
    --reason "Emergency production fix for critical security vulnerability CVE-2024-1234" \
    --approver "manager@example.com" \
    --expiry-hours 4

  # Validate a break-glass (use in CI gates)
  qa-policy-engine.sh break-glass validate bg-12345678-1234-1234-1234-123456789012

  # List all active break-glass records
  qa-policy-engine.sh break-glass list active

  # Revoke a break-glass
  qa-policy-engine.sh break-glass revoke bg-12345678-1234-1234-1234-123456789012 "No longer needed"

Audit Log: var/break-glass-audit.log
EOF
}

# --- Break-Glass Subcommand Router ---
handle_break_glass() {
  local subcommand="${1:-}"
  shift || true

  case "$subcommand" in
    create)
      # Parse named arguments
      local policy="" requirement="" reason="" approver="" expiry_hours="24"

      while [[ $# -gt 0 ]]; do
        case "$1" in
          --policy)
            policy="$2"
            shift 2
            ;;
          --requirement)
            requirement="$2"
            shift 2
            ;;
          --reason)
            reason="$2"
            shift 2
            ;;
          --approver)
            approver="$2"
            shift 2
            ;;
          --expiry-hours)
            expiry_hours="$2"
            shift 2
            ;;
          *)
            echo "ERROR: Unknown option: $1" >&2
            break_glass_usage
            return 1
            ;;
        esac
      done

      break_glass_create "$policy" "$requirement" "$reason" "$approver" "$expiry_hours"
      ;;
    validate)
      break_glass_validate "$@"
      ;;
    list)
      break_glass_list "$@"
      ;;
    revoke)
      break_glass_revoke "$@"
      ;;
    --help|-h|"")
      break_glass_usage
      ;;
    *)
      echo "ERROR: Unknown break-glass subcommand: $subcommand" >&2
      break_glass_usage
      return 1
      ;;
  esac
}

# --- Main Entry Point ---
main() {
  # Check if this is a break-glass command
  if [[ "${1:-}" == "break-glass" ]]; then
    shift
    handle_break_glass "$@"
    exit $?
  fi

  # Original policy engine logic for stdin-based invocation
  INPUT="$(cat)"
  CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
  PROJECT_DIR="${CWD:-$(pwd)}"
  QUALITY="$PROJECT_DIR/.claude/quality.json"
  AUDIT="$VERIFY_DIR/policy-engine-audit.json"
  POLICIES_REPO="$REPO_ROOT/etc/policies/qa"
  POLICIES_HOME="${HOME}/.claude/policies/qa"

  # Fail-closed: no quality.json = allow (not governed)
  if [[ ! -f "$QUALITY" ]]; then
    echo "POLICY ENGINE: allow (no quality.json)"
    exit 0
  fi

  # Locate policies
  POLICIES=""
  [[ -d "$POLICIES_REPO" ]] && POLICIES="$POLICIES_REPO"
  [[ -d "$POLICIES_HOME" ]] && POLICIES="$POLICIES_HOME $POLICIES"

  # No OPA = fail-closed allow with audit
  if ! command -v opa >/dev/null 2>&1; then
    jq -n --arg ts "$now" --arg ch "warn" --arg msg "opa not installed; policy engine skipped" \
      '{generated_at:$ts,channel:$ch,message:$msg,break_glass:false}' > "$AUDIT"
    echo "POLICY ENGINE: allow (opa not installed, audit recorded)"
    exit 0
  fi

  # No policies = allow
  if [[ -z "$POLICIES" ]] || ! ls $POLICIES/*.rego 1>/dev/null 2>&1; then
    echo "POLICY ENGINE: allow (no policies)"
    exit 0
  fi

  # Eval: run opa test on policies and evaluate actual deny/warn
  denies=0
  warns=0
  eval_denies=0
  eval_warns=0
  policy_errors=""
  policies_found=""

  for pdir in $POLICIES; do
    [[ -d "$pdir" ]] || continue
    policies_found="$policies_found $pdir"

    # Test policies
    if opa test "$pdir" 2>/dev/null; then
      :
    else
      # Policy test failure = warn
      warns=$((warns + 1))
      policy_errors="$policy_errors $pdir (test failed)"
    fi

    # Evaluate policies against quality.json
    if [[ -f "$QUALITY" ]]; then
      # Batch deny+warn evaluation: single opa eval for both, extract counts with jq
      local _eval_result _counts
      _eval_result="$(opa eval 'deny_count: count(data.qa.deny), warn_count: count(data.qa.warn)' --data "$pdir" --input "$QUALITY" -f json 2>/dev/null || echo "")"
      if [[ -n "$_eval_result" ]]; then
        _counts="$(jq -r '[.result[0].expressions[0].value.deny_count // 0, .result[0].expressions[0].value.warn_count // 0] | @tsv' <<< "$_eval_result" 2>/dev/null || echo "0	0")"
        local deny_count warn_count
        IFS=$'\t' read -r deny_count warn_count <<< "$_counts"
      else
        # Fallback: separate calls if batch eval unsupported
        local deny_result deny_count warn_result warn_count
        deny_result="$(opa eval "data.qa.deny" --data "$pdir" --input "$QUALITY" -f json 2>/dev/null || echo "[]")"
        deny_count="$(jq 'length' <<< "$deny_result" 2>/dev/null || echo 0)"
        warn_result="$(opa eval "data.qa.warn" --data "$pdir" --input "$QUALITY" -f json 2>/dev/null || echo "[]")"
        warn_count="$(jq 'length' <<< "$warn_result" 2>/dev/null || echo 0)"
      fi
      eval_denies=$((eval_denies + deny_count))
      eval_warns=$((eval_warns + warn_count))
    fi
  done

  # Use evaluation results if available, otherwise use test results
  if [[ $eval_denies -gt 0 || $eval_warns -gt 0 ]]; then
    denies=$eval_denies
    warns=$eval_warns
  fi

  # Channel: deny, warn, or allow
  channel="allow"
  if [[ $denies -gt 0 ]]; then
    channel="deny"
  elif [[ $warns -gt 0 ]]; then
    channel="warn"
  fi

  # Break-glass audit record (P16.3: full audit with channel)
  jq -n \
    --arg ts "$now" \
    --arg ch "$channel" \
    --argjson d "$denies" \
    --argjson w "$warns" \
    --argjson ed "$eval_denies" \
    --argjson ew "$eval_warns" \
    --arg policies "${policies_found:-none}" \
    --arg errors "${policy_errors:-none}" \
    '{
      generated_at: $ts,
      channel: $ch,
      deny_count: $d,
      warn_count: $w,
      eval_denies: $ed,
      eval_warns: $ew,
      policies_checked: $policies,
      policy_errors: $errors,
      break_glass: false
    }' > "$AUDIT"

  # Output based on channel
  case "$channel" in
    deny)
      echo "POLICY-ENGINE FAIL: $denies policy denial(s)" >&2
      exit 2
      ;;
    warn)
      echo "POLICY ENGINE: allow (warn: $warns)"
      exit 0
      ;;
    *)
      echo "POLICY ENGINE: allow"
      exit 0
      ;;
  esac
}

# Run main if script is executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
