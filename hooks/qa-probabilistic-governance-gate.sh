#!/bin/zsh
# qa-probabilistic-governance-gate.sh (CDDL-E3)
# Validates statistical acceptance criteria for ML/probabilistic requirements.
# @trace FR-CDDL-003
#
# Usage:
#   qa-probabilistic-governance-gate.sh --check <requirement-id>
#   qa-probabilistic-governance-gate.sh --validate-evidence <evidence-file>
#   qa-probabilistic-governance-gate.sh --validate-acceptance <acceptance-file>
#   qa-probabilistic-governance-gate.sh --validate-all
#
# Gate logic:
#   - Point estimate must meet threshold
#   - Confidence interval must not include failure threshold
#   - Regret bound within tolerance
#
# Exit codes:
#   0 - All checks passed
#   1 - Statistical criteria not met (threshold/CI/regret failure)
#   2 - Invalid format (schema validation failed)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ACCEPTANCE_SCHEMA="$REPO_ROOT/schemas/statistical-acceptance.schema.json"
EVIDENCE_SCHEMA="$REPO_ROOT/schemas/evidence.schema.json"
VERIFY_DIR="${REPO_ROOT}/.claude/verification"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Default thresholds
DEFAULT_THRESHOLD="${STATISTICAL_THRESHOLD:-0.80}"
DEFAULT_REGRET_BOUND="${STATISTICAL_REGRET_BOUND:-0.10}"
DEFAULT_CONFIDENCE_LEVEL="${STATISTICAL_CONFIDENCE_LEVEL:-0.95}"
DEFAULT_MIN_SAMPLE_SIZE="${STATISTICAL_MIN_SAMPLE_SIZE:-100}"

#######################################
# Print usage information
#######################################
usage() {
  cat <<'EOF'
qa-probabilistic-governance-gate.sh - Statistical acceptance criteria validation

Usage:
  qa-probabilistic-governance-gate.sh --check <requirement-id>
    Check statistical acceptance for a specific requirement ID.
    Looks for .claude/verification/statistical-acceptance-<req-id>.json

  qa-probabilistic-governance-gate.sh --validate-evidence <evidence-file>
    Validate an evidence file containing statistical_acceptance data.

  qa-probabilistic-governance-gate.sh --validate-acceptance <acceptance-file>
    Validate a statistical-acceptance.json file.

  qa-probabilistic-governance-gate.sh --validate-all
    Validate all statistical acceptance files in .claude/verification/.

Exit Codes:
  0 - All statistical criteria met
  1 - Statistical criteria not met (threshold/CI/regret failure)
  2 - Invalid format (schema validation failed)

Environment Variables:
  STATISTICAL_THRESHOLD      - Default threshold for pass/fail (default: 0.80)
  STATISTICAL_REGRET_BOUND   - Maximum acceptable regret bound (default: 0.10)
  STATISTICAL_CONFIDENCE_LEVEL - Required confidence level (default: 0.95)
  STATISTICAL_MIN_SAMPLE_SIZE  - Minimum required sample size (default: 100)

Examples:
  # Check a specific requirement
  qa-probabilistic-governance-gate.sh --check FR-ML-001

  # Validate an evidence file with statistical acceptance
  qa-probabilistic-governance-gate.sh --validate-evidence .claude/verification/evidence-FR-ML-001.json

  # Validate a statistical acceptance file
  qa-probabilistic-governance-gate.sh --validate-acceptance out/statistical-acceptance.json
EOF
}

#######################################
# Log a message with timestamp
# Arguments:
#   $1 - Message level (INFO, WARN, ERROR)
#   $2 - Message text
#######################################
log() {
  local level="$1"
  local msg="$2"
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [$level] $msg" >&2
}

#######################################
# Validate JSON against a schema
# Arguments:
#   $1 - Schema file path
#   $2 - Instance file path
# Returns:
#   0 - Valid
#   2 - Invalid
#######################################
validate_schema() {
  local schema="$1"
  local instance="$2"

  if [[ ! -f "$schema" ]]; then
    log "WARN" "Schema not found: $schema, skipping schema validation"
    return 0
  fi

  if [[ ! -f "$instance" ]]; then
    log "ERROR" "Instance file not found: $instance"
    return 2
  fi

  if bash "$REPO_ROOT/scripts/validate-json-schema.sh" "$schema" "$instance" 2>/dev/null; then
    return 0
  else
    return 2
  fi
}

#######################################
# Compare a value against a threshold using comparator
# Arguments:
#   $1 - Point estimate value
#   $2 - Threshold value
#   $3 - Comparator (">=", ">", "<=", "<", "==")
# Returns:
#   0 - Comparison true
#   1 - Comparison false
#######################################
compare_values() {
  local value="$1"
  local threshold="$2"
  local comparator="$3"

  case "$comparator" in
    ">=")
      if [[ $(echo "$value >= $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    ">")
      if [[ $(echo "$value > $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    "<=")
      if [[ $(echo "$value <= $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    "<")
      if [[ $(echo "$value < $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    "==")
      if [[ $(echo "$value == $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    *)
      return 1
      ;;
  esac
}

#######################################
# Check if confidence interval includes failure threshold
# For >= comparator: CI lower bound must be >= threshold
# For <= comparator: CI upper bound must be <= threshold
# Arguments:
#   $1 - CI lower bound
#   $2 - CI upper bound
#   $3 - Threshold
#   $4 - Comparator
# Returns:
#   0 - CI is safe (does not include failure)
#   1 - CI includes failure zone
#######################################
check_confidence_interval() {
  local ci_lower="$1"
  local ci_upper="$2"
  local threshold="$3"
  local comparator="$4"

  case "$comparator" in
    ">="|">")
      # For ">= threshold", CI lower must be >= threshold
      # If CI lower < threshold, we can't be confident we meet threshold
      if [[ $(echo "$ci_lower >= $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    "<="|"<")
      # For "<= threshold", CI upper must be <= threshold
      if [[ $(echo "$ci_upper <= $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    "==")
      # For exact match, check if threshold is within CI
      if [[ $(echo "$ci_lower <= $threshold && $ci_upper >= $threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        return 0
      else
        return 1
      fi
      ;;
    *)
      return 1
      ;;
  esac
}

#######################################
# Validate statistical acceptance criteria
# Arguments:
#   $1 - JSON file path containing statistical_acceptance data
#   $2 - "acceptance" for standalone file, "evidence" for embedded in evidence
# Outputs:
#   JSON report to stdout
# Returns:
#   0 - All criteria met
#   1 - Criteria not met
#   2 - Invalid format
#######################################
validate_statistical_acceptance() {
  local file_path="$1"
  local file_type="${2:-acceptance}"
  local resolved_path

  # Resolve path
  if [[ "$file_path" != /* ]]; then
    resolved_path="$REPO_ROOT/$file_path"
  else
    resolved_path="$file_path"
  fi

  if [[ ! -f "$resolved_path" ]]; then
    log "ERROR" "File not found: $resolved_path"
    jq -n --arg ts "$now" --arg f "$resolved_path" \
      '{generated_at:$ts,status:"not_found",pass:false,error_count:1,errors:["File not found: " + $f]}'
    return 2
  fi

  local errors=()
  local warnings=()

  # Validate schema
  local schema_to_use
  if [[ "$file_type" == "evidence" ]]; then
    schema_to_use="$EVIDENCE_SCHEMA"
  else
    schema_to_use="$ACCEPTANCE_SCHEMA"
  fi

  if ! validate_schema "$schema_to_use" "$resolved_path"; then
    log "ERROR" "Schema validation failed: $resolved_path"
    jq -n --arg ts "$now" --arg f "$resolved_path" \
      '{generated_at:$ts,status:"invalid_format",pass:false,error_count:1,errors:["Schema validation failed: " + $f]}'
    return 2
  fi

  # Extract statistical acceptance data
  local sa_data
  if [[ "$file_type" == "evidence" ]]; then
    sa_data="$(jq -c '.statistical_acceptance // empty' "$resolved_path" 2>/dev/null || echo "")"
    if [[ -z "$sa_data" || "$sa_data" == "null" ]]; then
      log "WARN" "No statistical_acceptance found in evidence file: $resolved_path"
      jq -n --arg ts "$now" --arg f "$resolved_path" \
        '{generated_at:$ts,status:"no_statistical_data",pass:true,error_count:0,warnings:["No statistical_acceptance in evidence file"]}'
      return 0
    fi
  else
    sa_data="$(jq -c '.' "$resolved_path" 2>/dev/null || echo "")"
  fi

  # Extract fields
  local metric_type point_estimate ci_lower ci_upper ci_level threshold comparator
  local sample_size regret_bound passes_threshold p_value requirement_id

  metric_type="$(echo "$sa_data" | jq -r '.metric_type // .metric // "unknown"')"
  point_estimate="$(echo "$sa_data" | jq -r '.point_estimate // .observed // 0')"
  ci_lower="$(echo "$sa_data" | jq -r '.confidence_interval.lower // 0')"
  ci_upper="$(echo "$sa_data" | jq -r '.confidence_interval.upper // 0')"
  ci_level="$(echo "$sa_data" | jq -r '.confidence_interval.level // .confidence_level // 0.95')"
  threshold="$(echo "$sa_data" | jq -r '.threshold // empty')"
  if [[ -z "$threshold" ]]; then
    threshold="$DEFAULT_THRESHOLD"
  fi
  comparator="$(echo "$sa_data" | jq -r '.comparator // ">="')"
  sample_size="$(echo "$sa_data" | jq -r '.sample_size // 0')"
  regret_bound="$(echo "$sa_data" | jq -r '.regret_bound // empty')"
  if [[ -z "$regret_bound" ]]; then
    regret_bound="$DEFAULT_REGRET_BOUND"
  fi
  passes_threshold="$(echo "$sa_data" | jq -r '.passes_threshold // .pass // false')"
  p_value="$(echo "$sa_data" | jq -r '.p_value // empty')"
  requirement_id="$(echo "$sa_data" | jq -r '.requirement_id // "unknown"')"

  local criteria_failed=0
  local criteria_met=0

  # === Gate 1: Point estimate must meet threshold ===
  if compare_values "$point_estimate" "$threshold" "$comparator"; then
    criteria_met=$((criteria_met + 1))
    log "INFO" "Point estimate check passed: $point_estimate $comparator $threshold"
  else
    criteria_failed=$((criteria_failed + 1))
    errors+=("Point estimate $point_estimate does not meet threshold: $comparator $threshold")
    log "ERROR" "Point estimate check failed: $point_estimate $comparator $threshold"
  fi

  # === Gate 2: Confidence interval must not include failure threshold ===
  if check_confidence_interval "$ci_lower" "$ci_upper" "$threshold" "$comparator"; then
    criteria_met=$((criteria_met + 1))
    log "INFO" "Confidence interval check passed: [$ci_lower, $ci_upper] safe for threshold $threshold"
  else
    criteria_failed=$((criteria_failed + 1))
    errors+=("Confidence interval [$ci_lower, $ci_upper] includes failure threshold $threshold")
    log "ERROR" "Confidence interval check failed: [$ci_lower, $ci_upper] vs threshold $threshold"
  fi

  # === Gate 3: Regret bound within tolerance ===
  local regret_tolerance="$DEFAULT_REGRET_BOUND"
  local regret_check
  regret_check="$(echo "$regret_bound <= $regret_tolerance" | bc -l 2>/dev/null || echo "0")"
  if [[ "$regret_check" -eq 1 ]]; then
    criteria_met=$((criteria_met + 1))
    log "INFO" "Regret bound check passed: $regret_bound <= $regret_tolerance"
  else
    criteria_failed=$((criteria_failed + 1))
    errors+=("Regret bound $regret_bound exceeds tolerance $regret_tolerance")
    log "ERROR" "Regret bound check failed: $regret_bound > $regret_tolerance"
  fi

  # === Gate 4: Sample size sufficiency (warning only) ===
  if [[ "$sample_size" -lt "$DEFAULT_MIN_SAMPLE_SIZE" ]]; then
    warnings+=("Sample size $sample_size is below recommended minimum $DEFAULT_MIN_SAMPLE_SIZE")
    log "WARN" "Sample size below minimum: $sample_size < $DEFAULT_MIN_SAMPLE_SIZE"
  else
    log "INFO" "Sample size check passed: $sample_size >= $DEFAULT_MIN_SAMPLE_SIZE"
  fi

  # === Gate 5: Confidence level sufficiency ===
  local ci_level_check
  ci_level_check="$(echo "$ci_level >= $DEFAULT_CONFIDENCE_LEVEL" | bc -l 2>/dev/null || echo "0")"
  if [[ "$ci_level_check" -eq 1 ]]; then
    log "INFO" "Confidence level check passed: $ci_level >= $DEFAULT_CONFIDENCE_LEVEL"
  else
    warnings+=("Confidence level $ci_level is below recommended $DEFAULT_CONFIDENCE_LEVEL")
    log "WARN" "Confidence level below recommended: $ci_level < $DEFAULT_CONFIDENCE_LEVEL"
  fi

  # === Gate 6: P-value check (if provided) ===
  if [[ -n "$p_value" && "$p_value" != "null" ]]; then
    local pval_check
    pval_check="$(echo "$p_value < 0.05" | bc -l 2>/dev/null || echo "0")"
    if [[ "$pval_check" -eq 1 ]]; then
      log "INFO" "P-value check passed: $p_value < 0.05 (statistically significant)"
    else
      warnings+=("P-value $p_value is not statistically significant at 0.05 level")
      log "WARN" "P-value not significant: $p_value >= 0.05"
    fi
  fi

  # Verify passes_threshold field matches actual gate result
  local actual_pass="true"
  if [[ $criteria_failed -gt 0 ]]; then
    actual_pass="false"
  fi

  if [[ "$passes_threshold" == "true" && "$actual_pass" == "false" ]]; then
    errors+=("passes_threshold=true but gate checks failed")
    log "ERROR" "Inconsistency: passes_threshold=true but actual checks failed"
  elif [[ "$passes_threshold" == "false" && "$actual_pass" == "true" ]]; then
    warnings+=("passes_threshold=false but gate checks passed")
    log "WARN" "Inconsistency: passes_threshold=false but actual checks passed"
  fi

  # Generate report
  local status="pass"
  local pass="true"
  local error_count=${#errors[@]}
  local warning_count=${#warnings[@]}

  if [[ $criteria_failed -gt 0 ]]; then
    status="criteria_not_met"
    pass="false"
  fi

  local errors_json warnings_json
  if [[ ${#errors[@]} -eq 0 ]]; then
    errors_json="[]"
  else
    errors_json="$(printf '%s\n' "${errors[@]}" | jq -R . | jq -s .)"
  fi
  if [[ ${#warnings[@]} -eq 0 ]]; then
    warnings_json="[]"
  else
    warnings_json="$(printf '%s\n' "${warnings[@]}" | jq -R . | jq -s .)"
  fi

  jq -n \
    --arg ts "$now" \
    --arg status "$status" \
    --arg pass "$pass" \
    --argjson error_count "$error_count" \
    --argjson warning_count "$warning_count" \
    --argjson errors "$errors_json" \
    --argjson warnings "$warnings_json" \
    --arg file "$resolved_path" \
    --arg requirement_id "$requirement_id" \
    --arg metric_type "$metric_type" \
    --argjson point_estimate "$point_estimate" \
    --argjson threshold "$threshold" \
    --arg comparator "$comparator" \
    --argjson ci_lower "$ci_lower" \
    --argjson ci_upper "$ci_upper" \
    --argjson ci_level "$ci_level" \
    --argjson sample_size "$sample_size" \
    --argjson regret_bound "$regret_bound" \
    --argjson criteria_met "$criteria_met" \
    --argjson criteria_failed "$criteria_failed" \
    '{
      generated_at: $ts,
      status: $status,
      pass: ($pass == "true"),
      error_count: $error_count,
      warning_count: $warning_count,
      errors: $errors,
      warnings: $warnings,
      file: $file,
      requirement_id: $requirement_id,
      metrics: {
        metric_type: $metric_type,
        point_estimate: $point_estimate,
        threshold: $threshold,
        comparator: $comparator,
        confidence_interval: {
          lower: $ci_lower,
          upper: $ci_upper,
          level: $ci_level
        },
        sample_size: $sample_size,
        regret_bound: $regret_bound
      },
      gates: {
        criteria_met: $criteria_met,
        criteria_failed: $criteria_failed
      }
    }'

  if [[ $criteria_failed -gt 0 ]]; then
    return 1
  fi

  return 0
}

#######################################
# Check statistical acceptance for a specific requirement
# Arguments:
#   $1 - Requirement ID (e.g., FR-ML-001)
# Returns:
#   0 - Criteria met
#   1 - Criteria not met
#   2 - Not found or invalid
#######################################
check_requirement() {
  local requirement_id="$1"
  local acceptance_file="$VERIFY_DIR/statistical-acceptance-${requirement_id}.json"

  if [[ ! -f "$acceptance_file" ]]; then
    # Try alternate locations
    acceptance_file="$VERIFY_DIR/statistical-acceptance.json"

    if [[ ! -f "$acceptance_file" ]]; then
      log "ERROR" "No statistical acceptance file found for requirement: $requirement_id"
      jq -n --arg ts "$now" --arg req "$requirement_id" \
        '{generated_at:$ts,status:"not_found",pass:false,error_count:1,errors:["No statistical acceptance for requirement: " + $req]}'
      return 2
    fi

    # Check if the file contains the requested requirement
    local file_req_id
    file_req_id="$(jq -r '.requirement_id // empty' "$acceptance_file" 2>/dev/null || echo "")"
    if [[ -n "$file_req_id" && "$file_req_id" != "$requirement_id" ]]; then
      log "WARN" "Statistical acceptance file has different requirement_id: $file_req_id (expected: $requirement_id)"
    fi
  fi

  log "INFO" "Checking statistical acceptance for requirement: $requirement_id"
  validate_statistical_acceptance "$acceptance_file" "acceptance"
}

#######################################
# Validate all statistical acceptance files
# Returns:
#   0 - All valid
#   1 - Some criteria not met
#   2 - Some invalid format
#######################################
validate_all() {
  local total_errors=0
  local total_warnings=0
  local all_pass="true"
  local exit_code=0
  local reports=()
  local files_checked=0

  mkdir -p "$VERIFY_DIR"

  # Find statistical-acceptance*.json files
  local acceptance_files=()
  while IFS= read -r -d '' f; do
    acceptance_files+=("$f")
  done < <(find "$VERIFY_DIR" -name "statistical-acceptance*.json" -type f -print0 2>/dev/null)

  # Also find evidence files that might contain statistical_acceptance
  while IFS= read -r -d '' f; do
    acceptance_files+=("$f")
  done < <(find "$VERIFY_DIR" -name "evidence*.json" -type f -print0 2>/dev/null)

  if [[ ${#acceptance_files[@]} -eq 0 ]]; then
    log "INFO" "No statistical acceptance files found in $VERIFY_DIR"
    jq -n --arg ts "$now" --arg dir "$VERIFY_DIR" \
      '{generated_at:$ts,status:"no_files",pass:true,error_count:0,files_checked:0,verification_dir:$dir}'
    return 0
  fi

  log "INFO" "Found ${#acceptance_files[@]} statistical acceptance file(s) to validate"

  for file in "${acceptance_files[@]}"; do
    log "INFO" "Validating: $file"

    local file_type="acceptance"
    if [[ "$(basename "$file")" == evidence* ]]; then
      file_type="evidence"
    fi

    local report
    report="$(validate_statistical_acceptance "$file" "$file_type")" || true
    local rc=$?
    # Need to check the status field in report since || true sets rc to 0
    local report_status
    report_status="$(echo "$report" | jq -r '.status // "unknown"')"
    if [[ "$report_status" != "pass" && "$report_status" != "no_statistical_data" ]]; then
      all_pass="false"
      if [[ "$report_status" == "invalid_format" ]]; then
        exit_code=2
      elif [[ "$report_status" == "criteria_not_met" ]] && [[ $exit_code -ne 2 ]]; then
        exit_code=1
      fi
    fi

    reports+=("$report")
    files_checked=$((files_checked + 1))

    local file_errors file_warnings
    file_errors="$(echo "$report" | jq -r '.error_count // 0')"
    file_warnings="$(echo "$report" | jq -r '.warning_count // 0')"
    total_errors=$((total_errors + file_errors))
    total_warnings=$((total_warnings + file_warnings))
  done

  # Aggregate report
  local reports_json
  reports_json="$(printf '%s\n' "${reports[@]}" | jq -s .)"

  local status="pass"
  if [[ "$exit_code" -eq 1 ]]; then
    status="criteria_not_met"
  elif [[ "$exit_code" -eq 2 ]]; then
    status="invalid_format"
  fi

  jq -n \
    --arg ts "$now" \
    --arg status "$status" \
    --arg pass "$all_pass" \
    --argjson total_errors "$total_errors" \
    --argjson total_warnings "$total_warnings" \
    --argjson reports "$reports_json" \
    --argjson files_checked "$files_checked" \
    --arg verification_dir "$VERIFY_DIR" \
    '{
      generated_at: $ts,
      status: $status,
      pass: ($pass == "true"),
      total_errors: $total_errors,
      total_warnings: $total_warnings,
      files_checked: $files_checked,
      verification_dir: $verification_dir,
      reports: $reports
    }'

  return $exit_code
}

#######################################
# Hook mode (reads stdin JSON input)
# Used when called as a governance hook
#######################################
hook_mode() {
  INPUT="$(cat)"
  CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
  PROJECT_DIR="${CWD:-$(pwd)}"
  local project_verify_dir="$PROJECT_DIR/.claude/verification"
  local qfile="$PROJECT_DIR/.claude/quality.json"
  local report_file="$project_verify_dir/probabilistic-governance-gate.json"

  mkdir -p "$project_verify_dir"

  # Check if probabilistic governance is enabled
  if [[ -f "$qfile" ]]; then
    local model prob_enabled
    model="$(jq -r '.governance.delivery_model // "auto"' "$qfile" 2>/dev/null || echo auto)"
    prob_enabled="$(jq -r '.governance.enforce_probabilistic_gate // false' "$qfile" 2>/dev/null || echo false)"

    if [[ "$model" != "probabilistic" && "$model" != "multimodal" && "$model" != "hybrid_ml" && "$prob_enabled" != "true" ]]; then
      jq -n --arg ts "$now" '{generated_at:$ts,status:"not_applicable",pass:true,error_count:0}' > "$report_file"
      echo "PROBABILISTIC GOVERNANCE GATE: not_applicable (skip)"
      exit 0
    fi
  fi

  # Run validation
  local errors=0
  local missing=""

  # Check for required artifacts
  if [[ ! -f "$project_verify_dir/statistical-acceptance.json" ]]; then
    # Try to find any statistical-acceptance files
    local found_sa
    found_sa="$(find "$project_verify_dir" -name "statistical-acceptance*.json" -type f 2>/dev/null | head -1)"
    if [[ -z "$found_sa" ]]; then
      echo "PROBABILISTIC: missing statistical-acceptance.json" >&2
      errors=$((errors + 1))
      missing="${missing:+$missing }statistical-acceptance.json"
    fi
  fi

  # Check for DATA_CARD.md if probabilistic
  if [[ ! -f "$PROJECT_DIR/DATA_CARD.md" ]]; then
    echo "PROBABILISTIC: missing DATA_CARD.md" >&2
    errors=$((errors + 1))
    missing="${missing:+$missing }DATA_CARD.md"
  fi

  # Check for MODEL_CARD.md if probabilistic
  if [[ ! -f "$PROJECT_DIR/MODEL_CARD.md" ]]; then
    echo "PROBABILISTIC: missing MODEL_CARD.md" >&2
    errors=$((errors + 1))
    missing="${missing:+$missing }MODEL_CARD.md"
  fi

  if [[ "$errors" -gt 0 ]]; then
    jq -n --arg ts "$now" --argjson e "$errors" --arg m "$missing" \
      '{generated_at:$ts,status:"fail",pass:false,error_count:$e,missing:$m}' > "$report_file"
    echo "PROBABILISTIC-GOVERNANCE FAIL: $errors missing artifact(s)" >&2
    exit 2
  fi

  # Validate statistical acceptance files
  local sa_files=()
  while IFS= read -r f; do
    sa_files+=("$f")
  done < <(find "$project_verify_dir" -name "statistical-acceptance*.json" -type f 2>/dev/null)

  local criteria_errors=0
  for sa_file in "${sa_files[@]}"; do
    if ! validate_statistical_acceptance "$sa_file" "acceptance" >/dev/null 2>&1; then
      criteria_errors=$((criteria_errors + 1))
      echo "PROBABILISTIC: criteria not met in $sa_file" >&2
    fi
  done

  if [[ "$criteria_errors" -gt 0 ]]; then
    jq -n --arg ts "$now" --argjson e "$criteria_errors" \
      '{generated_at:$ts,status:"criteria_not_met",pass:false,error_count:$e}' > "$report_file"
    echo "PROBABILISTIC-GOVERNANCE FAIL: $criteria_errors file(s) did not meet criteria" >&2
    exit 1
  fi

  jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$report_file"
  echo "PROBABILISTIC GOVERNANCE GATE: pass"
  exit 0
}

#######################################
# Main entry point
#######################################
main() {
  if [[ $# -lt 1 ]]; then
    # Check if we're being called as a hook (stdin has JSON with 'cwd' key)
    if [[ -t 0 ]]; then
      usage
      exit 2
    else
      hook_mode
    fi
    return
  fi

  local command="$1"
  shift

  case "$command" in
    --check)
      if [[ $# -lt 1 ]]; then
        log "ERROR" "Missing requirement-id argument"
        usage
        exit 2
      fi
      check_requirement "$1"
      ;;

    --validate-evidence)
      if [[ $# -lt 1 ]]; then
        log "ERROR" "Missing evidence file argument"
        usage
        exit 2
      fi
      validate_statistical_acceptance "$1" "evidence"
      ;;

    --validate-acceptance)
      if [[ $# -lt 1 ]]; then
        log "ERROR" "Missing acceptance file argument"
        usage
        exit 2
      fi
      validate_statistical_acceptance "$1" "acceptance"
      ;;

    --validate-all)
      validate_all
      ;;

    -h|--help|help)
      usage
      exit 0
      ;;

    *)
      log "ERROR" "Unknown command: $command"
      usage
      exit 2
      ;;
  esac
}

main "$@"
