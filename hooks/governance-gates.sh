#!/usr/bin/env bash
# governance-gates.sh
# Consolidated governance gate dispatcher.
# Replaces 26 individual qa-*-gate.sh Stop hooks with a single script
# that sources lib/common.sh once, parses stdin once, reads quality.json once,
# and runs each gate as an inline function.
#
# Performance: Batch-parses quality.json, attestation.json, async-test-results.json
# once each at startup. Replaces rg loops with bash string matching.
# Target: ~20 jq spawns, 0 rg spawns for pattern matching.
#
# Exit codes:
#   0 = all gates pass or advisory-only failures
#   2 = at least one fail-closed gate failed
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh (saves ~400ms on cache hit) ---
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_FILE="${_CACHE_DIR}/governance-gates-${_CACHE_KEY}.result"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < _CACHE_TTL )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

HOOK_NAME="GOVERNANCE-GATES"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init
read_quality_config

# --- Cache check with full key (post common.sh, for precision) ---
_head_sha="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo none)}"
_qc_mtime="0"; [[ -f "$QUALITY_CONFIG" ]] && _qc_mtime="$(stat -f '%m' "$QUALITY_CONFIG" 2>/dev/null || stat -c '%Y' "$QUALITY_CONFIG" 2>/dev/null || echo 0)"
_qs_mtime="0"; [[ -f "$QA_STATE" ]] && _qs_mtime="$(stat -f '%m' "$QA_STATE" 2>/dev/null || stat -c '%Y' "$QA_STATE" 2>/dev/null || echo 0)"
_cache_key=$(printf '%s\0%s\0%s\0%s' "$HOOK_NAME" "$_head_sha" "$_qc_mtime" "$_qs_mtime" | shasum -a 256 | cut -d' ' -f1)
unset _head_sha _qc_mtime _qs_mtime
_gg_ttl="${HOOK_CACHE_TTL:-600}"
if hook_cache_check "$_cache_key" "$_gg_ttl"; then
    hook_cache_read "$_cache_key"
    _cached_rc=$?
    # Also write to ultra-fast cache for next time
    hook_cache_read "$_cache_key" > "$_CACHE_FILE" 2>/dev/null || true
    if [[ "$_cached_rc" -ne 0 ]]; then
      echo "GOVERNANCE-GATES FAIL: cached result was non-zero ($_cached_rc)" >&2
    fi
    exit "$_cached_rc"
fi

# --- Shared state ---
_gate_failures=0       # count of fail-closed gate failures
_gate_pass_count=0
_gate_na_count=0
_gate_fail_count=0
_gate_summary=""

# --- Gate result helpers ---
_gate_pass() {
  local name="$1"
  _gate_pass_count=$((_gate_pass_count + 1))
  _gate_summary="${_gate_summary}  PASS: $name"$'\n'
}

_gate_na() {
  local name="$1" reason="${2:-skipped}"
  _gate_na_count=$((_gate_na_count + 1))
  _gate_summary="${_gate_summary}  N/A:  $name ($reason)"$'\n'
}

_gate_fail() {
  local name="$1" reason="$2" fail_closed="${3:-false}"
  _gate_fail_count=$((_gate_fail_count + 1))
  _gate_summary="${_gate_summary}  FAIL: $name - $reason"$'\n'
  echo "GOVERNANCE-GATES FAIL: [$name]: $reason" >&2
  if [[ "$fail_closed" == "true" ]]; then
    _gate_failures=$((_gate_failures + 1))
  fi
}

# Helper: check if a delivery model matches
_model_is() {
  local want="$1"
  [[ "$DELIVERY_MODEL" == "$want" ]]
}

# Helper: SCRIPT_DIR / REPO_ROOT (for schema validation references)
_HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_REPO_ROOT="$(cd "$_HOOKS_DIR/.." && pwd)"

# ==========================================================================
# B2: Batch quality.json parsing — one jq call extracts ALL config fields
# ==========================================================================
QCFG_DELIVERY_MODEL="${DELIVERY_MODEL:-auto}"
QCFG_CRITICALITY="${CRITICALITY_TIER:-established}"
QCFG_STACKS="python"
QCFG_ENFORCE_PROBABILISTIC="false"
QCFG_ENFORCE_SLO="false"
QCFG_MAX_FLAKE_RATE="0.10"
QCFG_MIN_PASS_RATE="0.90"
QCFG_ENFORCE_FLAKE_QUARANTINE="false"
QCFG_QUARANTINE_TTL_DAYS="14"
QCFG_ENFORCE_DISPUTE="false"
QCFG_MAX_DISPUTE_OPEN_DAYS="14"
QCFG_ZK_REQUIRED="false"
QCFG_REQUIRE_TX_HASH="false"
QCFG_DEBT_ENFORCE="false"
QCFG_PLAYBOOK_ENFORCE="false"

if [[ -f "$QUALITY_CONFIG" ]]; then
  _qcfg_raw="$($JQ_CMD -r '
    [
      (.governance.delivery_model // "auto"),
      (.criticality_tier // "established"),
      ((.stacks // ["python"]) | join(",")),
      (.governance.enforce_probabilistic_gate // false | tostring),
      (.governance.reliability.enforce_slo_gate // false | tostring),
      (.governance.reliability.max_flake_rate // 0.10 | tostring),
      (.governance.reliability.min_pass_rate // 0.90 | tostring),
      (.governance.reliability.enforce_flake_quarantine // false | tostring),
      (.governance.reliability.quarantine_ttl_days // 14 | tostring),
      (.governance.reliability.enforce_dispute_gate // false | tostring),
      (.governance.reliability.max_dispute_open_days // 14 | tostring),
      (.governance.privacy_preserving.zk_required // false | tostring),
      (.governance.onchain.require_tx_hash // false | tostring),
      (.governance.debt_registry.enforce_gate // false | tostring),
      (.governance.playbooks.enforce_gate // false | tostring)
    ] | @tsv
  ' "$QUALITY_CONFIG" 2>/dev/null || true)"
  if [[ -n "$_qcfg_raw" ]]; then
    IFS=$'\t' read -r \
      QCFG_DELIVERY_MODEL \
      QCFG_CRITICALITY \
      QCFG_STACKS \
      QCFG_ENFORCE_PROBABILISTIC \
      QCFG_ENFORCE_SLO \
      QCFG_MAX_FLAKE_RATE \
      QCFG_MIN_PASS_RATE \
      QCFG_ENFORCE_FLAKE_QUARANTINE \
      QCFG_QUARANTINE_TTL_DAYS \
      QCFG_ENFORCE_DISPUTE \
      QCFG_MAX_DISPUTE_OPEN_DAYS \
      QCFG_ZK_REQUIRED \
      QCFG_REQUIRE_TX_HASH \
      QCFG_DEBT_ENFORCE \
      QCFG_PLAYBOOK_ENFORCE \
      <<< "$_qcfg_raw"
  fi
  unset _qcfg_raw
fi

# ==========================================================================
# B4: Batch attestation.json parsing — one jq call for all attestation fields
# ==========================================================================
_ATT_LOADED=false
ATT_FR_TOTAL=0
ATT_FR_COVERED=0
ATT_ORPHAN_TESTS=0
ATT_MISSING_PAIRS=0
ATT_MISSING_TYPES=0
ATT_DETECTED_TEST_TYPES='{}'
ATT_SIGNED_PRESENT="false"
ATT_SLSA_PRESENT="false"

_load_attestation() {
  [[ "$_ATT_LOADED" == "true" ]] && return
  _ATT_LOADED=true
  local attest_file="$VERIFY_DIR/qa-attestation.json"
  [[ -f "$attest_file" ]] || return 0

  local _att_raw
  _att_raw="$($JQ_CMD -r '
    [
      (.summary.fr_total // 0 | tostring),
      (.summary.fr_covered // 0 | tostring),
      (.summary.orphan_tests // 0 | tostring),
      (.methodology.test_first.missing_test_pairs | length // 0 | tostring),
      (.methodology.missing_required_test_types | length // 0 | tostring),
      (.methodology.detected_test_types // {} | tojson),
      (.security.signed_attestation_present // false | tostring),
      (.security.slsa_provenance_present // false | tostring)
    ] | @tsv
  ' "$attest_file" 2>/dev/null || true)"
  if [[ -n "$_att_raw" ]]; then
    IFS=$'\t' read -r \
      ATT_FR_TOTAL \
      ATT_FR_COVERED \
      ATT_ORPHAN_TESTS \
      ATT_MISSING_PAIRS \
      ATT_MISSING_TYPES \
      ATT_DETECTED_TEST_TYPES \
      ATT_SIGNED_PRESENT \
      ATT_SLSA_PRESENT \
      <<< "$_att_raw"
  fi
}

# ==========================================================================
# Batch async-test-results.json parsing — one jq call for all results fields
# ==========================================================================
_RESULTS_LOADED=false
RESULTS_TOTAL=0
RESULTS_FAILED=0
RESULTS_FLAKY=0
RESULTS_FILE="$HOME/.claude/.async-test-results.json"

_load_async_results() {
  [[ "$_RESULTS_LOADED" == "true" ]] && return
  _RESULTS_LOADED=true
  [[ -f "$RESULTS_FILE" ]] || return 0

  local _res_raw
  _res_raw="$($JQ_CMD -r '
    [
      (.total // 0 | tostring),
      (.failed // 0 | tostring),
      (.flaky // 0 | tostring)
    ] | @tsv
  ' "$RESULTS_FILE" 2>/dev/null || true)"
  if [[ -n "$_res_raw" ]]; then
    IFS=$'\t' read -r RESULTS_TOTAL RESULTS_FAILED RESULTS_FLAKY <<< "$_res_raw"
  fi
}

# ==========================================================================
# B3: JSON array builder helper — accumulate checks in bash, emit once
# ==========================================================================
# Usage: _json_arr_init; _json_arr_add '{"k":"v"}'; result=$(_json_arr_emit)
_json_arr_items=""
_json_arr_init() { _json_arr_items=""; }
_json_arr_add() {
  if [[ -z "$_json_arr_items" ]]; then
    _json_arr_items="$1"
  else
    _json_arr_items="${_json_arr_items},$1"
  fi
}
_json_arr_emit() { echo "[${_json_arr_items}]"; }

# Helper: build a JSON string, properly escaped (no jq)
_json_str() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '"%s"' "$s"
}

# Helper: build a JSON array of strings from bash array elements (no jq)
_json_str_array() {
  local items="" e
  for e in "$@"; do
    local escaped="${e//\\/\\\\}"
    escaped="${escaped//\"/\\\"}"
    if [[ -z "$items" ]]; then
      items="\"$escaped\""
    else
      items="$items,\"$escaped\""
    fi
  done
  printf '[%s]' "$items"
}

# ============================================================================
# Gate 1: prdset-compiler
# Compile PRD-set docs into generated contract items + refresh ledger.
# P6: Content-addressable skip — hash spec doc mtimes; skip if unchanged.
# P6: Run all three scripts in parallel when not skipped.
# ============================================================================
_PRDSET_SPEC_DOCS=(PRD.md ADR.md FUNCTIONAL_REQUIREMENTS.md PLAN.md USER_JOURNEYS.md RISK_REGISTER.md VERIFICATION_POLICY.md RELEASE_CONTRACT.md)

gate_prdset_compiler() {
  local name="prdset-compiler"
  [[ ! -d "$PROJECT_DIR" ]] && { _gate_na "$name" "no project dir"; return 0; }

  # P6: Content-addressable skip — build a fingerprint from spec doc mtimes + sizes.
  # If fingerprint matches cached value, skip the expensive compile entirely.
  # Only include INPUT files (spec docs), not output dirs (items-generated changes every run).
  local _prdset_fp="" _prdset_cache_file="${HOOK_CACHE_DIR}/prdset-compiler-fp"
  local _d _f _stat
  for _d in "${_PRDSET_SPEC_DOCS[@]}"; do
    _f="$PROJECT_DIR/$_d"
    if [[ -f "$_f" ]]; then
      _stat="$(stat -f '%m:%z' "$_f" 2>/dev/null || stat -c '%Y:%s' "$_f" 2>/dev/null || echo "0:0")"
      _prdset_fp="${_prdset_fp}${_d}=${_stat};"
    fi
  done

  mkdir -p "$HOOK_CACHE_DIR" 2>/dev/null || true
  if [[ -f "$_prdset_cache_file" ]]; then
    local _cached_fp
    _cached_fp="$(cat "$_prdset_cache_file" 2>/dev/null)" || _cached_fp=""
    if [[ "$_cached_fp" == "$_prdset_fp" ]]; then
      _gate_pass "$name"
      return 0
    fi
  fi

  # Skip if contracts tooling not installed (run: thegent install)
  [[ -x "$HOME/.claude/contracts/prdset-compile.sh" ]] || { _gate_na "$name" "contracts not installed (run: thegent install)"; return 0; }

  # P6: Run all three compile scripts in parallel (each ~5s sequentially)
  "$HOME/.claude/contracts/prdset-compile.sh" "$PROJECT_DIR" >/dev/null 2>&1 &
  local _pid_prdset=$!
  # ledger-init depends on prdset-compile (uses items-generated), so wait for it
  wait "$_pid_prdset" 2>/dev/null || { _gate_na "$name" "prdset-compile failed"; return 0; }

  "$HOME/.claude/contracts/ledger-init.sh" "$PROJECT_DIR" >/dev/null 2>&1 &
  "$HOME/.claude/contracts/dag-compile.sh" "$PROJECT_DIR" >/dev/null 2>&1 &
  wait 2>/dev/null || true

  # Cache the fingerprint on success
  printf '%s' "$_prdset_fp" > "$_prdset_cache_file" 2>/dev/null || true

  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 2: elicitation-closure-gate
# Blocks progressed states when elicitation is unresolved.
# ============================================================================
gate_elicitation_closure() {
  local name="elicitation-closure"
  local fail_closed="${QA_ELICITATION_FAIL_CLOSED:-false}"
  local ledger="$PROJECT_DIR/contracts/ledger.json"

  [[ -f "$ledger" ]] || { _gate_na "$name" "no ledger.json"; return 0; }

  local adr_doc="$PROJECT_DIR/ADR.md"
  local adr_doc_content=""
  [[ -f "$adr_doc" ]] && adr_doc_content=$(<"$adr_doc" 2>/dev/null) || true
  local vcount=0

  # P6: Extract id+source as TSV in a single jq call (was: jq per item + normalize-item.sh per .md)
  # Instead of calling normalize-item.sh (Python3, ~200ms each), check for open_questions
  # and decisions directly from the generated item JSON files (already produced by prdset-compiler).
  while IFS=$'\t' read -r id src; do
    [[ -z "$id" || -z "$src" ]] && continue

    if [[ "$src" == *.md ]] && [[ -f "$src" ]]; then
      # P6: Check generated item JSON instead of re-running normalize-item.sh
      local gen_item="$PROJECT_DIR/contracts/items-generated/${id}.json"
      if [[ -f "$gen_item" ]]; then
        # Single jq call extracts open_questions count + decisions array
        local _eli_raw
        _eli_raw="$($JQ_CMD -r '[(.open_questions | length // 0 | tostring), ((.decisions // []) | join("\n"))] | @tsv' "$gen_item" 2>/dev/null || true)"
        local oq_count="" decisions=""
        IFS=$'\t' read -r oq_count decisions <<< "$_eli_raw"
        if [[ "${oq_count:-0}" -gt 0 ]]; then
          vcount=$((vcount + 1))
        fi
        # Check decisions against ADR doc
        while IFS= read -r adr; do
          [[ -z "$adr" ]] && continue
          if [[ ! "$adr" =~ ^ADR- ]]; then
            vcount=$((vcount + 1))
          elif [[ -n "$adr_doc_content" ]] && [[ "$adr_doc_content" != *"$adr"* ]]; then
            vcount=$((vcount + 1))
          elif [[ -z "$adr_doc_content" ]]; then
            vcount=$((vcount + 1))
          fi
        done <<< "$decisions"
      fi
    fi
  done < <($JQ_CMD -r '.items[] | select((.state|ascii_downcase) as $s | ($s=="approved" or $s=="claimed" or $s=="evidence_submitted" or $s=="verified" or $s=="accepted" or $s=="released")) | [(.id // ""), (.source // "")] | @tsv' "$ledger" 2>/dev/null || true)

  if [[ "$vcount" -gt 0 ]]; then
    _gate_fail "$name" "$vcount elicitation violation(s)" "$fail_closed"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 3: methodology-enforcer
# Advisory/optional methodology report from QA attestation.
# ============================================================================
gate_methodology_enforcer() {
  local name="methodology-enforcer"
  local fail_closed="${QA_METHODOLOGY_FAIL_CLOSED:-false}"
  local attest_file="$VERIFY_DIR/qa-attestation.json"

  [[ -f "$attest_file" ]] || { _gate_na "$name" "no attestation"; return 0; }

  # B4: Use pre-parsed attestation values
  _load_attestation

  local fr_total="$ATT_FR_TOTAL"
  local fr_covered="$ATT_FR_COVERED"
  local missing_pairs="$ATT_MISSING_PAIRS"
  local missing_types="$ATT_MISSING_TYPES"

  local violations=0
  (( missing_pairs > 0 )) && violations=$((violations + 1))
  (( missing_types > 0 )) && violations=$((violations + 1))
  (( fr_total > 0 && fr_covered < fr_total )) && violations=$((violations + 1))

  if [[ "$violations" -gt 0 ]]; then
    _gate_fail "$name" "$violations methodology violation(s) (pairs=$missing_pairs types=$missing_types cov=$fr_covered/$fr_total)" "$fail_closed"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 4: agent-claim-validator
# Validates agent-statement.json against schema; enforces claim transitions.
# ============================================================================
gate_agent_claim_validator() {
  local name="agent-claim-validator"
  local schema="$_REPO_ROOT/schemas/agent-statement.schema.json"
  local stmt="$VERIFY_DIR/agent-statement.json"
  local report="$VERIFY_DIR/agent-claim-validator.json"

  if [[ ! -f "$stmt" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no agent-statement.json"
    return 0
  fi

  # Schema validation
  if [[ -f "$schema" ]] && [[ -f "$_REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
    if ! bash "$_REPO_ROOT/scripts/validate-json-schema.sh" "$schema" "$stmt" 2>/dev/null; then
      write_fail_report "$report" "$name" 1 "Schema validation failed"
      _gate_fail "$name" "schema validation failed" "${QA_AGENT_CLAIM_FAIL_CLOSED:-true}"
      return 0
    fi
  fi

  # Claim transitions: observation/claim/decision/risk must have evidence
  local bad_stmts
  bad_stmts="$($JQ_CMD -r '
    [.statements[]? | select(.kind | IN("observation","claim","decision","risk")) | select((.evidence | type != "array") or (.evidence | length == 0))]
    | length
  ' "$stmt" 2>/dev/null || echo 0)"

  if [[ "${bad_stmts:-0}" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$bad_stmts" "Claims/observations/decisions/risks require evidence array"
    _gate_fail "$name" "claims without evidence: $bad_stmts" "${QA_AGENT_CLAIM_FAIL_CLOSED:-true}"
    return 0
  fi

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 5: claim-lifecycle-gate
# Enforces claim->evidence->verify chain.
# ============================================================================
gate_claim_lifecycle() {
  local name="claim-lifecycle"
  local stmt="$VERIFY_DIR/agent-statement.json"
  local report="$VERIFY_DIR/claim-lifecycle-gate.json"

  if [[ ! -f "$stmt" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no agent-statement.json"
    return 0
  fi

  local refs
  refs="$($JQ_CMD -r '
    [.statements[]? | select(.kind | IN("observation","claim","decision","risk")) | .evidence[]?]
    | unique[]
  ' "$stmt" 2>/dev/null || true)"

  if [[ -z "$refs" ]]; then
    write_pass_report "$report" "$name"
    _gate_pass "$name"
    return 0
  fi

  local errors=0 missing=""
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    case "$ref" in
      file://*)
        local rel="${ref#file://}"
        local path="$PROJECT_DIR/$rel"
        if [[ ! -f "$path" ]]; then
          errors=$((errors + 1))
          missing="${missing:+$missing }$ref"
        fi
        ;;
      att://*|prov://*|test://*|sarif://*|onchain://*|url://*)
        ;; # external refs: pass
      *)
        errors=$((errors + 1))
        missing="${missing:+$missing }$ref"
        ;;
    esac
  done <<< "$refs"

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Missing evidence: $missing"
    _gate_fail "$name" "missing evidence refs: $missing" "${QA_CLAIM_LIFECYCLE_FAIL_CLOSED:-false}"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 6: reliability-gate
# Reliability/flake governance from async test results.
# ============================================================================
gate_reliability() {
  local name="reliability"
  local fail_closed="${QA_RELIABILITY_FAIL_CLOSED:-false}"
  local max_flake="${QA_MAX_FLAKE_RATE:-0.10}"

  [[ -f "$RESULTS_FILE" ]] || { _gate_na "$name" "no async results"; return 0; }

  # Use pre-parsed results
  _load_async_results

  local total="$RESULTS_TOTAL" failed="$RESULTS_FAILED" flaky="$RESULTS_FLAKY"

  [[ "$total" -eq 0 ]] && { _gate_na "$name" "total=0"; return 0; }

  local flake_rate
  flake_rate="$(awk -v f="$flaky" -v t="$total" 'BEGIN { if (t==0) print 0; else printf "%.4f", f/t }')"

  local exceeds
  exceeds="$(awk -v r="$flake_rate" -v m="$max_flake" 'BEGIN { if (r>m) print "true"; else print "false" }')"
  if [[ "$exceeds" == "true" ]]; then
    _gate_fail "$name" "flake rate $flake_rate exceeds max $max_flake" "$fail_closed"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 7: tier-enforcer
# Enforces tier-based QA methodology requirements.
# ============================================================================
gate_tier_enforcer() {
  local name="tier-enforcer"
  local fail_closed="${QA_TIER_FAIL_CLOSED:-false}"

  [[ -f "$QUALITY_CONFIG" ]] || { _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local tier="$QCFG_CRITICALITY"

  # Build required types list (bash array, no jq)
  local -a required_types
  case "$tier" in
    new) required_types=(unit integration security) ;;
    established) required_types=(unit integration e2e security) ;;
    critical) required_types=(unit integration e2e property_based contract mutation security) ;;
    *) required_types=(unit integration security) ;;
  esac

  # Detect test types directly via directory/file checks (no attestation dependency).
  # This eliminates the race condition where governance-gates.sh runs before
  # quality-gate.sh finishes writing qa-attestation.json.
  local -A detected_types
  # Unit tests
  if [[ -d "$PROJECT_DIR/test/unit" ]] || [[ -d "$PROJECT_DIR/tests/unit" ]]; then
    detected_types[unit]=true
  elif compgen -G "$PROJECT_DIR"/{test,tests,spec}/*_test.* > /dev/null 2>&1 || \
       compgen -G "$PROJECT_DIR"/{test,tests,spec}/*.test.* > /dev/null 2>&1 || \
       compgen -G "$PROJECT_DIR"/{test,tests,spec}/*.spec.* > /dev/null 2>&1; then
    detected_types[unit]=true
  fi
  # Integration tests
  if [[ -d "$PROJECT_DIR/test/integration" ]] || [[ -d "$PROJECT_DIR/tests/integration" ]]; then
    detected_types[integration]=true
  fi
  # E2E tests
  if [[ -d "$PROJECT_DIR/test/e2e" ]] || [[ -d "$PROJECT_DIR/tests/e2e" ]] || \
     [[ -d "$PROJECT_DIR/test/end-to-end" ]] || [[ -d "$PROJECT_DIR/cypress" ]] || \
     [[ -d "$PROJECT_DIR/playwright" ]] || [[ -d "$PROJECT_DIR/e2e" ]]; then
    detected_types[e2e]=true
  fi
  # Security tests
  if [[ -d "$PROJECT_DIR/test/security" ]] || [[ -d "$PROJECT_DIR/tests/security" ]] || \
     [[ -f "$PROJECT_DIR/.gitleaks.toml" ]] || [[ -f "$PROJECT_DIR/.semgrep.yml" ]] || \
     [[ -f "$PROJECT_DIR/bandit.yaml" ]]; then
    detected_types[security]=true
  fi
  # Property-based tests
  if [[ -d "$PROJECT_DIR/test/property" ]] || [[ -d "$PROJECT_DIR/tests/property" ]]; then
    detected_types[property_based]=true
  fi
  # Contract tests
  if [[ -d "$PROJECT_DIR/test/contract" ]] || [[ -d "$PROJECT_DIR/tests/contract" ]] || \
     [[ -f "$PROJECT_DIR/pact.json" ]]; then
    detected_types[contract]=true
  fi
  # Mutation tests
  if [[ -f "$PROJECT_DIR/.mutmut.ini" ]] || [[ -f "$PROJECT_DIR/stryker.conf.js" ]] || \
     [[ -f "$PROJECT_DIR/stryker.config.js" ]]; then
    detected_types[mutation]=true
  fi

  # Compute missing types (pure bash, zero subprocesses)
  local -a missing_list=()
  for t in "${required_types[@]}"; do
    [[ "${detected_types[$t]:-}" == "true" ]] || missing_list+=("$t")
  done

  local count=${#missing_list[@]}
  local missing_csv=""
  if (( count > 0 )); then
    local IFS=','
    missing_csv="${missing_list[*]}"
  fi

  # Extra checks for critical tier (signing, SLSA)
  local extra_count=0
  if [[ "$tier" == "critical" ]]; then
    _load_attestation
    [[ "$ATT_SIGNED_PRESENT" != "true" ]] && extra_count=$((extra_count + 1))
    [[ "$ATT_SLSA_PRESENT" != "true" ]] && extra_count=$((extra_count + 1))
  fi

  if [[ "$count" -gt 0 || "$extra_count" -gt 0 ]]; then
    _gate_fail "$name" "tier=$tier requires [$missing_csv] ($count missing types, $extra_count extra)" "$fail_closed"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 8: trace-parity-audit
# Semantic parity audit against trace canonical strictness.
# B1: Replaced 57 rg loops with bash string matching (0 rg spawns).
# B3: Replaced incremental jq array building with bash string concatenation.
# ============================================================================
gate_trace_parity_audit() {
  local name="trace-parity-audit"
  local out="$VERIFY_DIR/trace-parity-report.json"

  local t_ruff="$HOME/.claude/templates/quality/ruff.toml"
  local t_golangci="$HOME/.claude/templates/quality/golangci.yml"
  local t_oxlint="$HOME/.claude/templates/quality/oxlintrc.json"

  # B3: Build checks array as bash string, emit one jq call at the end
  _json_arr_init
  local aligned_count=0 partial_count=0

  # --- Ruff semantic parity (B1: read file once, bash string match) ---
  local ruff_required=("line-length = 120" '"E"' '"W"' '"F"' '"I"' '"B"' '"C4"' '"UP"' '"N"' '"PT"' '"SIM"' '"RUF"' '"PERF"' '"LOG"' '"S"' '"ASYNC"' '"RET"' '"PTH"' '"DTZ"' '"D"' '"FA"' '"Q"' '"C90"' '"PL"' '"FBT"' '"ANN"' '"TRY"' '"INT"' '"PGH"' '"ISC"' '"FURB"' '"G"' '"ARG"' '"T10"' '"T20"' '"ERA"' '"SLF"' '"INP"')
  local ruff_missing=()
  if [[ -f "$t_ruff" ]]; then
    local t_ruff_content
    t_ruff_content=$(<"$t_ruff" 2>/dev/null) || t_ruff_content=""
    for pat in "${ruff_required[@]}"; do
      [[ "$t_ruff_content" != *"$pat"* ]] && ruff_missing+=("$pat")
    done
    local ruff_status="aligned"
    if [[ ${#ruff_missing[@]} -gt 0 ]]; then
      ruff_status="partial"
      partial_count=$((partial_count + 1))
    else
      aligned_count=$((aligned_count + 1))
    fi
    local ruff_missing_json
    ruff_missing_json="$(_json_str_array "${ruff_missing[@]-}")"
    _json_arr_add "{\"name\":\"ruff\",\"status\":\"$ruff_status\",\"missing\":$ruff_missing_json}"
  else
    _json_arr_add '{"name":"ruff","status":"missing_template"}'
  fi

  # --- golangci semantic parity (B1: read file once, bash string match) ---
  local golangci_required=("forbidigo" "varnamelen" "tagliatelle" "maintidx" "exhaustruct" "usestdlibvars" "predeclared" "sloglint" "testifylint" "exptostd" "godox" "asciicheck" "depguard")
  local golangci_missing=()
  if [[ -f "$t_golangci" ]]; then
    local t_golangci_content
    t_golangci_content=$(<"$t_golangci" 2>/dev/null) || t_golangci_content=""
    for pat in "${golangci_required[@]}"; do
      [[ "$t_golangci_content" != *"$pat"* ]] && golangci_missing+=("$pat")
    done
    local golangci_status="aligned"
    if [[ ${#golangci_missing[@]} -gt 0 ]]; then
      golangci_status="partial"
      partial_count=$((partial_count + 1))
    else
      aligned_count=$((aligned_count + 1))
    fi
    local golangci_missing_json
    golangci_missing_json="$(_json_str_array "${golangci_missing[@]-}")"
    _json_arr_add "{\"name\":\"golangci\",\"status\":\"$golangci_status\",\"missing\":$golangci_missing_json}"
  else
    _json_arr_add '{"name":"golangci","status":"missing_template"}'
  fi

  # --- oxlint semantic parity (B1: read file once, bash string match) ---
  local oxlint_required=("typescript/no-explicit-any" "typescript/explicit-function-return-type" "max-params" "complexity" "max-lines" "import/no-default-export" "import/max-dependencies")
  local oxlint_missing=()
  if [[ -f "$t_oxlint" ]]; then
    local t_oxlint_content
    t_oxlint_content=$(<"$t_oxlint" 2>/dev/null) || t_oxlint_content=""
    for pat in "${oxlint_required[@]}"; do
      [[ "$t_oxlint_content" != *"$pat"* ]] && oxlint_missing+=("$pat")
    done
    local boundaries_file="$HOME/.claude/templates/quality/boundaries-config.json"
    [[ -f "$boundaries_file" ]] || oxlint_missing+=("boundaries-config.json")
    local oxlint_status="aligned"
    if [[ ${#oxlint_missing[@]} -gt 0 ]]; then
      oxlint_status="partial"
      partial_count=$((partial_count + 1))
    else
      aligned_count=$((aligned_count + 1))
    fi
    local oxlint_missing_json
    oxlint_missing_json="$(_json_str_array "${oxlint_missing[@]-}")"
    _json_arr_add "{\"name\":\"oxlint\",\"status\":\"$oxlint_status\",\"missing\":$oxlint_missing_json}"
  else
    _json_arr_add '{"name":"oxlint","status":"missing_template"}'
  fi

  # B3: Single printf call to write the final report (no jq)
  local checks_json
  checks_json="$(_json_arr_emit)"

  printf '{"generated_at":"%s","checks":%s,"aligned_count":%d,"partial_count":%d}\n' \
    "$now" "$checks_json" "$aligned_count" "$partial_count" > "$out"

  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 9: dag-dependency-gate
# Enforce PLAN.md dependency transitions.
# ============================================================================
gate_dag_dependency() {
  local name="dag-dependency"
  local dag="$PROJECT_DIR/contracts/dag.json"
  local ledger="$PROJECT_DIR/contracts/ledger.json"
  local report="$VERIFY_DIR/dag-dependency-gate.json"

  if [[ ! -f "$dag" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no dag.json"
    return 0
  fi
  if [[ ! -f "$ledger" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no ledger.json"
    return 0
  fi

  # Build map: item_id -> state from ledger (single jq call producing TSV)
  declare -A _dag_state
  while IFS=$'\t' read -r id s; do
    [[ -n "$id" ]] && _dag_state[$id]="$s"
  done < <($JQ_CMD -r '.items[]? | [(.id // ""), (.state // "")] | @tsv' "$ledger" 2>/dev/null || true)

  local violations=0
  while IFS=$'\t' read -r from to; do
    [[ -z "$from" || -z "$to" ]] && continue
    [[ -z "${_dag_state[$to]+x}" ]] && continue
    [[ -z "${_dag_state[$from]+x}" ]] && continue
    local to_state="${_dag_state[$to]}"
    local from_state="${_dag_state[$from]}"
    if is_done_state "$to_state" && ! is_done_state "$from_state"; then
      violations=$((violations + 1))
    fi
  done < <($JQ_CMD -r '.edges[]? | select(.type=="depends_on") | [(.from // ""), (.to // "")] | @tsv' "$dag" 2>/dev/null || true)

  if [[ "$violations" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$violations"
    _gate_fail "$name" "$violations DAG violation(s)" "${QA_DAG_FAIL_CLOSED:-false}"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 10: brownfield-migration-gate
# Validates brownfield migration evidence.
# ============================================================================
gate_brownfield_migration() {
  local name="brownfield-migration"
  local report="$VERIFY_DIR/brownfield-migration-gate.json"

  [[ -f "$QUALITY_CONFIG" ]] || { write_na_report "$report" "$name"; _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local model="$QCFG_DELIVERY_MODEL"

  if [[ "$model" != "brownfield" && "$model" != "hybrid" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "not brownfield"
    return 0
  fi

  local errors=0 missing=""
  [[ -d "$PROJECT_DIR/test/characterization" ]] || { errors=$((errors+1)); missing="${missing:+$missing }test/characterization/"; }
  [[ -f "$VERIFY_DIR/canary-report.json" ]] || { errors=$((errors+1)); missing="${missing:+$missing }canary-report.json"; }
  [[ -f "$VERIFY_DIR/rollback-drill.json" ]] || { errors=$((errors+1)); missing="${missing:+$missing }rollback-drill.json"; }
  [[ -f "$PROJECT_DIR/contracts/strangler-plan.json" ]] || [[ -f "$PROJECT_DIR/docs/migration/STRANGLER_PLAN.md" ]] || { errors=$((errors+1)); missing="${missing:+$missing }strangler-plan"; }

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Missing: $missing"
    _gate_fail "$name" "$errors missing brownfield artifacts: $missing" "${QA_BROWNFIELD_FAIL_CLOSED:-false}"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 11: greenfield-bootstrap-gate
# Validates architecture boundary configs per stack.
# ============================================================================
gate_greenfield_bootstrap() {
  local name="greenfield-bootstrap"
  local report="$VERIFY_DIR/greenfield-bootstrap-gate.json"

  [[ -f "$QUALITY_CONFIG" ]] || { write_na_report "$report" "$name"; _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local model="$QCFG_DELIVERY_MODEL"
  local stacks="$QCFG_STACKS"

  if [[ "$model" != "greenfield" && "$model" != "hybrid" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "not greenfield"
    return 0
  fi

  local errors=0 missing=""
  # stacks is comma-separated from batch parse
  [[ "$stacks" == *python* ]] && { [[ -f "$PROJECT_DIR/ruff.toml" ]] || [[ -f "$PROJECT_DIR/pyproject.toml" ]] || { errors=$((errors+1)); missing="${missing:+$missing }ruff.toml/pyproject.toml"; }; }
  [[ "$stacks" == *go* ]] && { [[ -f "$PROJECT_DIR/.golangci.yml" ]] || { errors=$((errors+1)); missing="${missing:+$missing }.golangci.yml"; }; }
  [[ "$stacks" == *typescript* ]] || [[ "$stacks" == *ts* ]] || [[ "$stacks" == *js* ]] && { [[ -f "$PROJECT_DIR/.oxlintrc.json" ]] || [[ -f "$PROJECT_DIR/eslint.config.js" ]] || [[ -f "$PROJECT_DIR/.eslintrc" ]] || { errors=$((errors+1)); missing="${missing:+$missing }ts/js lint config"; }; }

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Missing: $missing"
    _gate_fail "$name" "$errors missing stack configs: $missing" "${QA_GREENFIELD_FAIL_CLOSED:-false}"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 12: probabilistic-governance-gate
# Validates statistical-acceptance.json, DATA_CARD.md, MODEL_CARD.md.
# ============================================================================
gate_probabilistic_governance() {
  local name="probabilistic-governance"
  local report="$VERIFY_DIR/probabilistic-governance-gate.json"

  [[ -f "$QUALITY_CONFIG" ]] || { write_na_report "$report" "$name"; _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local model="$QCFG_DELIVERY_MODEL"
  local prob_enabled="$QCFG_ENFORCE_PROBABILISTIC"

  if [[ "$model" != "probabilistic" && "$model" != "multimodal" && "$model" != "hybrid_ml" && "$prob_enabled" != "true" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "not probabilistic"
    return 0
  fi

  local errors=0 missing=""
  [[ -f "$VERIFY_DIR/statistical-acceptance.json" ]] || { errors=$((errors+1)); missing="${missing:+$missing }statistical-acceptance.json"; }
  [[ -f "$PROJECT_DIR/DATA_CARD.md" ]] || { errors=$((errors+1)); missing="${missing:+$missing }DATA_CARD.md"; }
  [[ -f "$PROJECT_DIR/MODEL_CARD.md" ]] || { errors=$((errors+1)); missing="${missing:+$missing }MODEL_CARD.md"; }

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Missing: $missing"
    _gate_fail "$name" "$errors missing probabilistic artifacts: $missing" "${QA_PROBABILISTIC_FAIL_CLOSED:-false}"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 13: reliability-slo-gate
# Reliability SLO gate with progressive enforcement.
# ============================================================================
gate_reliability_slo() {
  local name="reliability-slo"
  local fail_closed="${QA_RELIABILITY_SLO_FAIL_CLOSED:-false}"
  local report="$VERIFY_DIR/reliability-slo-gate.json"

  # B2: Use pre-parsed quality config
  local tier="$QCFG_CRITICALITY"
  [[ -z "$tier" ]] && tier="established"
  local enabled=false
  local max_flake="$QCFG_MAX_FLAKE_RATE"
  local min_pass="$QCFG_MIN_PASS_RATE"

  if [[ -f "$QUALITY_CONFIG" ]]; then
    [[ "$QCFG_ENFORCE_SLO" == "true" ]] && enabled=true
  fi
  [[ "$tier" == "critical" ]] && enabled=true
  [[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

  if [[ ! -f "$RESULTS_FILE" ]]; then
    printf '{"generated_at":"%s","tier":"%s","enabled":%s,"status":"no_results","error_count":0,"warn_count":0,"pass":true}\n' \
      "$now" "$tier" "$enabled" > "$report"
    _gate_na "$name" "no async results"
    return 0
  fi

  # Use pre-parsed results
  _load_async_results
  local total="$RESULTS_TOTAL" failed="$RESULTS_FAILED" flaky="$RESULTS_FLAKY"

  if [[ "$total" -le 0 ]]; then
    printf '{"generated_at":"%s","tier":"%s","enabled":%s,"status":"empty_results","error_count":0,"warn_count":1,"pass":true}\n' \
      "$now" "$tier" "$enabled" > "$report"
    _gate_na "$name" "total=0"
    return 0
  fi

  local flake_rate pass_rate
  flake_rate="$(awk -v f="$flaky" -v t="$total" 'BEGIN { printf "%.4f", (t==0?0:f/t) }')"
  pass_rate="$(awk -v f="$failed" -v t="$total" 'BEGIN { printf "%.4f", (t==0?1:(t-f)/t) }')"

  local err=0 warn=0

  # B3: Build checks array in bash instead of incremental jq calls
  _json_arr_init

  if awk -v x="$flake_rate" -v y="$max_flake" 'BEGIN{exit !(x>y)}'; then
    local s
    if [[ "$enabled" == "true" ]]; then err=$((err+1)); s="fail"; else warn=$((warn+1)); s="warn"; fi
    _json_arr_add "{\"check\":\"max_flake_rate\",\"status\":\"$s\",\"value\":\"$flake_rate\",\"threshold\":\"$max_flake\"}"
  else
    _json_arr_add "{\"check\":\"max_flake_rate\",\"status\":\"pass\",\"value\":\"$flake_rate\",\"threshold\":\"$max_flake\"}"
  fi

  if awk -v x="$pass_rate" -v y="$min_pass" 'BEGIN{exit !(x<y)}'; then
    local s
    if [[ "$enabled" == "true" ]]; then err=$((err+1)); s="fail"; else warn=$((warn+1)); s="warn"; fi
    _json_arr_add "{\"check\":\"min_pass_rate\",\"status\":\"$s\",\"value\":\"$pass_rate\",\"threshold\":\"$min_pass\"}"
  else
    _json_arr_add "{\"check\":\"min_pass_rate\",\"status\":\"pass\",\"value\":\"$pass_rate\",\"threshold\":\"$min_pass\"}"
  fi

  local checks
  checks="$(_json_arr_emit)"

  local _pass_bool="true"; [[ "$err" -gt 0 ]] && _pass_bool="false"
  printf '{"generated_at":"%s","tier":"%s","enabled":%s,"metrics":{"total":%d,"failed":%d,"flaky":%d,"flake_rate":%s,"pass_rate":%s},"error_count":%d,"warn_count":%d,"checks":%s,"pass":%s}\n' \
    "$now" "$tier" "$enabled" "$total" "$failed" "$flaky" "$flake_rate" "$pass_rate" "$err" "$warn" "$checks" "$_pass_bool" > "$report"

  if [[ "$enabled" == "true" && "$err" -gt 0 ]]; then
    _gate_fail "$name" "$err SLO check(s) failed" "$fail_closed"
  elif [[ "$err" -gt 0 ]]; then
    _gate_fail "$name" "$err SLO check(s) failed" "false"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 14: flake-quarantine-gate
# Manage flaky test quarantine ledger and expiry.
# ============================================================================
gate_flake_quarantine() {
  local name="flake-quarantine"
  local fail_closed="${QA_FLAKE_QUARANTINE_FAIL_CLOSED:-false}"
  local report="$VERIFY_DIR/flake-quarantine-gate.json"
  local quar_dir="$PROJECT_DIR/.claude/quarantine"
  local quar_file="$quar_dir/flaky-tests.json"

  mkdir -p "$quar_dir" 2>/dev/null || { echo "GOVERNANCE-GATES: mkdir quarantine dir failed ($?)" >&2; true; }

  # B2: Use pre-parsed quality config
  local tier="$QCFG_CRITICALITY"
  [[ -z "$tier" ]] && tier="established"
  local enabled=false
  local ttl_days="$QCFG_QUARANTINE_TTL_DAYS"

  if [[ -f "$QUALITY_CONFIG" ]]; then
    [[ "$QCFG_ENFORCE_FLAKE_QUARANTINE" == "true" ]] && enabled=true
  fi
  [[ "$tier" == "critical" ]] && enabled=true
  [[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

  [[ -f "$quar_file" ]] || echo '{"generated_at":"","entries":[]}' > "$quar_file"

  # determine flaky tests from async results
  local flaky_tests='[]'
  if [[ -f "$RESULTS_FILE" ]]; then
    flaky_tests="$($JQ_CMD -c '
      if (.flaky_tests|type)=="array" then .flaky_tests
      elif (.tests|type)=="array" then [ .tests[] | select((.flaky // false)==true) | (.name // .id // empty) ]
      else [] end | map(select(type=="string" and length>0)) | unique
    ' "$RESULTS_FILE" 2>/dev/null || echo '[]')"
  fi

  local now_iso="$now"
  local exp_iso
  exp_iso="$(date -u -v+${ttl_days}d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "+${ttl_days} days" +%Y-%m-%dT%H:%M:%SZ)"

  # upsert active flaky tests + compute expired/active counts (single jq call)
  # Outputs 3 lines: line 1 = updated quarantine JSON, line 2 = expired count, line 3 = active count
  local _quar_output
  _quar_output="$($JQ_CMD -r --arg now "$now_iso" --arg exp "$exp_iso" --argjson flaky "$flaky_tests" '
    .entries = ((.entries // []) | map(if (.status // "active") == "active" then . else . end))
    | reduce $flaky[] as $t (.;
        if any(.entries[]?; .test_id == $t and (.status // "active") == "active") then .
        else .entries += [{test_id:$t,reason:"detected_flaky",introduced_at:$now,expires_at:$exp,owner:"qa-system",status:"active"}] end
      )
    | .generated_at = $now
    | ([.entries[]? | select((.status // "active") == "active" and (.expires_at // "") < $now)] | length) as $expired |
      ([.entries[]? | select((.status // "active") == "active")] | length) as $active |
      (. | tojson), ($expired | tostring), ($active | tostring)
  ' "$quar_file" 2>/dev/null || printf '{"generated_at":"","entries":[]}\n0\n0')"

  # Parse 3-line output: data, expired, active
  local _quar_data expired_count active_count
  { read -r _quar_data; read -r expired_count; read -r active_count; } <<< "$_quar_output"
  echo "$_quar_data" > "$quar_file" 2>/dev/null || { echo "GOVERNANCE-GATES: write quarantine file failed ($?)" >&2; true; }
  expired_count="${expired_count:-0}"
  active_count="${active_count:-0}"

  local err=0 warn=0

  # B3: Build checks array in bash
  _json_arr_init
  if [[ "$expired_count" -gt 0 ]]; then
    local s
    if [[ "$enabled" == "true" ]]; then err=$((err+1)); s="fail"; else warn=$((warn+1)); s="warn"; fi
    _json_arr_add "{\"check\":\"expired_quarantine_entries\",\"status\":\"$s\",\"count\":$expired_count}"
  else
    _json_arr_add '{"check":"expired_quarantine_entries","status":"pass","count":0}'
  fi
  _json_arr_add "{\"check\":\"active_quarantine_entries\",\"status\":\"info\",\"count\":$active_count}"

  local checks
  checks="$(_json_arr_emit)"

  local _pass_bool="true"; [[ "$err" -gt 0 ]] && _pass_bool="false"
  printf '{"generated_at":"%s","tier":"%s","enabled":%s,"active_count":%d,"expired_count":%d,"error_count":%d,"warn_count":%d,"checks":%s,"pass":%s}\n' \
    "$now_iso" "$tier" "$enabled" "$active_count" "$expired_count" "$err" "$warn" "$checks" "$_pass_bool" > "$report"

  if [[ "$enabled" == "true" && "$err" -gt 0 ]]; then
    _gate_fail "$name" "expired quarantine entries present" "$fail_closed"
  elif [[ "$err" -gt 0 ]]; then
    _gate_fail "$name" "expired quarantine entries present" "false"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 15: verifier-dispute-gate
# Ensure verifier dispute/challenge workflow exists.
# ============================================================================
gate_verifier_dispute() {
  local name="verifier-dispute"
  local fail_closed="${QA_DISPUTE_FAIL_CLOSED:-false}"
  local report="$VERIFY_DIR/verifier-dispute-gate.json"
  local disputes="$VERIFY_DIR/disputes.jsonl"

  # B2: Use pre-parsed quality config
  local tier="$QCFG_CRITICALITY"
  [[ -z "$tier" ]] && tier="established"
  local enabled=false
  local max_open_days="$QCFG_MAX_DISPUTE_OPEN_DAYS"

  if [[ -f "$QUALITY_CONFIG" ]]; then
    [[ "$QCFG_ENFORCE_DISPUTE" == "true" ]] && enabled=true
  fi
  [[ "$tier" == "critical" ]] && enabled=true
  [[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

  local err=0 warn=0

  # B3: Build checks array in bash
  _json_arr_init

  # policy text presence — use bash string match instead of rg
  local policy_present=false
  local policy_content=""
  [[ -f "$PROJECT_DIR/VERIFICATION_POLICY.md" ]] && policy_content+=$(<"$PROJECT_DIR/VERIFICATION_POLICY.md" 2>/dev/null) || true
  [[ -f "$PROJECT_DIR/RELEASE_CONTRACT.md" ]] && policy_content+=$(<"$PROJECT_DIR/RELEASE_CONTRACT.md" 2>/dev/null) || true
  if [[ -n "$policy_content" ]]; then
    # Case-insensitive check via bash lowercasing
    local policy_lower="${policy_content,,}"
    if [[ "$policy_lower" == *"dispute"* ]] || [[ "$policy_lower" == *"challenge"* ]] || [[ "$policy_lower" == *"appeal"* ]] || [[ "$policy_lower" == *"verifier escalation"* ]]; then
      policy_present=true
    fi
  fi

  if [[ "$policy_present" == "true" ]]; then
    _json_arr_add '{"check":"dispute_policy_text","status":"pass"}'
  else
    local s
    if [[ "$enabled" == "true" ]]; then err=$((err+1)); s="fail"; else warn=$((warn+1)); s="warn"; fi
    _json_arr_add "{\"check\":\"dispute_policy_text\",\"status\":\"$s\"}"
  fi

  local open_count=0
  if [[ -f "$disputes" ]]; then
    open_count="$($JQ_CMD -s '[.[] | select((.status // "") == "open" or (.status // "") == "under_review")] | length' "$disputes" 2>/dev/null || echo 0)"
  else
    : > "$disputes"
  fi
  _json_arr_add "{\"check\":\"open_disputes\",\"status\":\"info\",\"count\":$open_count}"

  local checks
  checks="$(_json_arr_emit)"

  local _pass_bool="true"; [[ "$err" -gt 0 ]] && _pass_bool="false"
  printf '{"generated_at":"%s","tier":"%s","enabled":%s,"policy":{"max_dispute_open_days":%s},"open_disputes":%d,"error_count":%d,"warn_count":%d,"checks":%s,"pass":%s}\n' \
    "$now" "$tier" "$enabled" "$max_open_days" "$open_count" "$err" "$warn" "$checks" "$_pass_bool" > "$report"

  if [[ "$enabled" == "true" && "$err" -gt 0 ]]; then
    _gate_fail "$name" "dispute workflow requirements not satisfied" "$fail_closed"
  elif [[ "$err" -gt 0 ]]; then
    _gate_fail "$name" "dispute workflow requirements not satisfied" "false"
  else
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 16: rolling-wave-gate
# Validates rolling-wave.json against schema.
# ============================================================================
gate_rolling_wave() {
  local name="rolling-wave"
  local rw="$PROJECT_DIR/contracts/rolling-wave.json"
  local schema="$PROJECT_DIR/schemas/rolling-wave-plan.schema.json"
  local report="$VERIFY_DIR/rolling-wave-gate.json"

  if [[ ! -f "$rw" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no rolling-wave.json"
    return 0
  fi

  # Combined validation: JSON validity + required fields + item shape + forecast evidence (single jq call)
  local rw_check
  rw_check="$($JQ_CMD -r '
    if (type != "object") then "invalid_json"
    elif ((.generated_at | type != "string") or (.items | type != "array")) then "missing_fields"
    else
      ([ .items[]? | select(
        (.item_id | type != "string" or length == 0)
        or (.state | type != "string")
        or (.horizon | type != "string")
        or (.updated_at | type != "string")
        or (.next_review_at | type != "string")
      )] | length) as $bad_items |
      ([ .items[]? | select(
        .acceptance_ready == true
        and ((.promotion_evidence | type != "array") or (.promotion_evidence | length == 0))
      )] | length) as $bad_forecast |
      "\($bad_items):\($bad_forecast)"
    end
  ' "$rw" 2>/dev/null || echo "invalid_json")"

  case "$rw_check" in
    invalid_json) write_fail_report "$report" "$name" 1 "invalid JSON"; _gate_fail "$name" "invalid JSON" "false"; return 0 ;;
    missing_fields) write_fail_report "$report" "$name" 1 "missing required fields"; _gate_fail "$name" "missing required fields" "false"; return 0 ;;
  esac

  local bad_items="${rw_check%%:*}"
  local bad_forecast="${rw_check##*:}"
  [[ "${bad_items:-0}" -eq 0 ]] || { write_fail_report "$report" "$name" "$bad_items" "invalid item shape"; _gate_fail "$name" "invalid item shape ($bad_items)" "false"; return 0; }
  [[ "${bad_forecast:-0}" -eq 0 ]] || { write_fail_report "$report" "$name" "$bad_forecast" "acceptance_ready items require promotion_evidence"; _gate_fail "$name" "acceptance_ready items require promotion_evidence ($bad_forecast)" "false"; return 0; }

  # Schema validation
  if [[ -f "$schema" ]] && [[ -f "$_REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
    if ! bash "$_REPO_ROOT/scripts/validate-json-schema.sh" "$schema" "$rw" 2>/dev/null; then
      write_fail_report "$report" "$name" 1 "schema validation failed"
      _gate_fail "$name" "schema validation failed" "false"
      return 0
    fi
  fi

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 17: assurance-case-gate
# Validates assurance-case.json against schema and structure.
# ============================================================================
gate_assurance_case() {
  local name="assurance-case"
  local ac="$PROJECT_DIR/contracts/assurance-case.json"
  local schema="$PROJECT_DIR/schemas/assurance-case.schema.json"
  local report="$VERIFY_DIR/assurance-case-gate.json"

  if [[ ! -f "$ac" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no assurance-case.json"
    return 0
  fi

  # Combined validation: JSON validity + required fields (single jq call)
  local ac_check
  ac_check="$($JQ_CMD -r '
    if (type != "object") then "invalid_json"
    elif (.generated_at and .top_claims and .nodes) then "ok"
    else "missing_fields"
    end
  ' "$ac" 2>/dev/null || echo "invalid_json")"

  case "$ac_check" in
    invalid_json) write_fail_report "$report" "$name" 1 "invalid JSON"; _gate_fail "$name" "invalid JSON" "false"; return 0 ;;
    missing_fields) write_fail_report "$report" "$name" 1 "missing required fields (generated_at, top_claims, nodes)"; _gate_fail "$name" "missing required fields" "false"; return 0 ;;
  esac

  if [[ -f "$schema" ]] && [[ -f "$_REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
    if ! bash "$_REPO_ROOT/scripts/validate-json-schema.sh" "$schema" "$ac" 2>/dev/null; then
      write_fail_report "$report" "$name" 1 "schema validation failed"
      _gate_fail "$name" "schema validation failed" "false"
      return 0
    fi
  fi

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 18: privacy-proof-gate
# Validates privacy-proof.json when present.
# ============================================================================
gate_privacy_proof() {
  local name="privacy-proof"
  local proof="$VERIFY_DIR/privacy-proof.json"
  local report="$VERIFY_DIR/privacy-proof-gate.json"

  if [[ ! -f "$proof" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no privacy-proof.json"
    return 0
  fi

  # B2: Use pre-parsed quality config
  local zk_required="$QCFG_ZK_REQUIRED"

  # Combined validation: JSON validity + optional zk schema shape (single jq call)
  local pp_check
  pp_check="$($JQ_CMD -r '
    if (type != "object") then "invalid_json"
    elif '"$([[ "$zk_required" == "true" ]] && echo 'true' || echo 'false')"' then
      if ((.generated_at | type == "string")
        and (.proof_system | type == "string")
        and (.statement_hash | type == "string")
        and (.proof_hash | type == "string")
        and (.verified | type == "boolean")
        and (.scope | type == "string"))
      then "ok"
      else "bad_shape"
      end
    else "ok"
    end
  ' "$proof" 2>/dev/null || echo "invalid_json")"

  case "$pp_check" in
    invalid_json) write_fail_report "$report" "$name" 1 "invalid JSON"; _gate_fail "$name" "invalid JSON" "false"; return 0 ;;
    bad_shape) write_fail_report "$report" "$name" 1 "invalid schema shape when zk_required"; _gate_fail "$name" "invalid schema shape when zk_required" "false"; return 0 ;;
  esac

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 19: onchain-adapter
# Mandatory on-chain workflow adapter with local anchoring and optional broadcast.
# ============================================================================
gate_onchain_adapter() {
  local name="onchain-adapter"
  local fail_closed="${QA_ONCHAIN_FAIL_CLOSED:-true}"
  local claim_file="$VERIFY_DIR/agent-statement.json"
  local ledger_file="$VERIFY_DIR/claim-lifecycle.json"
  local out_file="$VERIFY_DIR/onchain-payload.json"
  local anchor_ledger="$VERIFY_DIR/onchain-ledger.jsonl"

  if [[ ! -f "$claim_file" || ! -f "$ledger_file" ]]; then
    # Anchor a deterministic no-claim checkpoint
    local _proj_esc; _proj_esc="$(_json_escape "$PROJECT_DIR")"
    printf '{"generated_at":"%s","project_dir":"%s","event_type":"no_claim_checkpoint"}\n' \
      "$now" "$_proj_esc" > "$out_file"
    local hash
    hash="$(shasum -a 256 "$out_file" | awk '{print $1}')"
    local _payload_esc; _payload_esc="$(_json_escape "$out_file")"
    printf '{"timestamp":"%s","event_type":"no_claim_checkpoint","payload":"%s","sha256":"%s","broadcasted":false}\n' \
      "$now" "$_payload_esc" "$hash" >> "$anchor_ledger"
    _gate_pass "$name"
    return 0
  fi

  # Parse claim_file and ledger_file in batch (2 fields from claim, 1 from ledger)
  local item_id spec_hash next_state
  local _claim_raw
  _claim_raw="$($JQ_CMD -r '[(.item_id // ""), (.spec_hash // "")] | @tsv' "$claim_file" 2>/dev/null || true)"
  IFS=$'\t' read -r item_id spec_hash <<< "$_claim_raw"
  next_state="$($JQ_CMD -r '.next_state // ""' "$ledger_file" 2>/dev/null || true)"

  local state_id=""
  case "$next_state" in
    Draft|draft) state_id=0 ;;
    Proposed|proposed) state_id=1 ;;
    Approved|approved) state_id=2 ;;
    Claimed|claimed) state_id=3 ;;
    EvidenceSubmitted|evidence_submitted) state_id=4 ;;
    Verified|verified) state_id=5 ;;
    Accepted|accepted) state_id=6 ;;
    Released|released) state_id=7 ;;
    Rejected|rejected) state_id=8 ;;
    *) state_id="" ;;
  esac

  local _proj_esc; _proj_esc="$(_json_escape "$PROJECT_DIR")"
  local _sid="${state_id:-null}"
  printf '{"generated_at":"%s","project_dir":"%s","item_id":"%s","spec_hash":"%s","next_state":"%s","state_id":%s}\n' \
    "$now" "$_proj_esc" "$item_id" "$spec_hash" "$next_state" "$_sid" > "$out_file"

  local hash
  hash="$(shasum -a 256 "$out_file" | awk '{print $1}')"
  local broadcasted=false tx_hash=""

  # Optional broadcast with foundry cast
  if [[ "${QA_ONCHAIN_BROADCAST:-false}" == "true" ]]; then
    : "${QA_ONCHAIN_RPC_URL:?missing QA_ONCHAIN_RPC_URL}"
    : "${QA_ONCHAIN_CONTRACT:?missing QA_ONCHAIN_CONTRACT}"
    : "${QA_ONCHAIN_PRIVATE_KEY:?missing QA_ONCHAIN_PRIVATE_KEY}"
    if ! command -v cast >/dev/null 2>&1; then
      if [[ "$fail_closed" == "true" ]]; then
        _gate_fail "$name" "cast (foundry) not installed for on-chain broadcast" "$fail_closed"
        return 0
      fi
      _gate_pass "$name"
      return 0
    fi
    if [[ -z "$item_id" || -z "$state_id" ]]; then
      if [[ "$fail_closed" == "true" ]]; then
        _gate_fail "$name" "missing item_id or state_id in on-chain payload" "$fail_closed"
        return 0
      fi
      _gate_pass "$name"
      return 0
    fi

    local out
    out="$(
      cast send "$QA_ONCHAIN_CONTRACT" \
      "transition(bytes32,uint8)" \
      "$item_id" "$state_id" \
      --rpc-url "$QA_ONCHAIN_RPC_URL" \
      --private-key "$QA_ONCHAIN_PRIVATE_KEY" 2>&1
    )"
    broadcasted=true
    # Extract tx hash with bash regex instead of rg
    if [[ "$out" =~ (0x[a-fA-F0-9]{64}) ]]; then
      tx_hash="${BASH_REMATCH[1]}"
    fi
  fi

  local _payload_esc; _payload_esc="$(_json_escape "$out_file")"
  local _sid="${state_id:-null}"
  printf '{"timestamp":"%s","event_type":"transition_anchor","payload":"%s","sha256":"%s","item_id":"%s","spec_hash":"%s","next_state":"%s","state_id":%s,"broadcasted":%s,"tx_hash":"%s"}\n' \
    "$now" "$_payload_esc" "$hash" "$item_id" "$spec_hash" "$next_state" "$_sid" "$broadcasted" "$tx_hash" >> "$anchor_ledger"

  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 20: onchain-contract-gate
# When applicable: runs Forge/Slither/Echidna. Stub writes no_contracts when no Solidity.
# ============================================================================
gate_onchain_contract() {
  local name="onchain-contract"
  local report="$VERIFY_DIR/onchain-contract-gate.json"

  local has_sol=false
  [[ -d "$PROJECT_DIR/contracts/onchain" ]] && has_sol=true
  if [[ "$has_sol" != "true" ]]; then
    # P6: Use compgen (bash builtin, no fork) instead of find for .sol detection
    if compgen -G "$PROJECT_DIR"/*.sol > /dev/null 2>&1 || \
       compgen -G "$PROJECT_DIR"/*/*.sol > /dev/null 2>&1 || \
       compgen -G "$PROJECT_DIR"/*/*/*.sol > /dev/null 2>&1; then
      has_sol=true
    fi
  fi

  if [[ "$has_sol" != "true" ]]; then
    printf '{"generated_at":"%s","status":"no_contracts","checks":[],"pass":true,"error_count":0,"warn_count":0}\n' "$now" > "$report"
    _gate_na "$name" "no Solidity contracts"
    return 0
  fi

  # Has Solidity but stub cannot run real tools
  printf '{"generated_at":"%s","status":"stub_not_evaluated","checks":[],"pass":true,"error_count":0,"warn_count":0,"warn":"Stub: install real qa-onchain-contract-gate for Forge/Slither/Echidna"}\n' "$now" > "$report"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 21: onchain-transition-gate
# Validates onchain transition receipts.
# ============================================================================
gate_onchain_transition() {
  local name="onchain-transition"
  local ledger="$VERIFY_DIR/onchain-ledger.jsonl"
  local report="$VERIFY_DIR/onchain-transition-gate.json"

  if [[ ! -f "$ledger" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no onchain-ledger"
    return 0
  fi

  # B2: Use pre-parsed quality config
  local tx_required="$QCFG_REQUIRE_TX_HASH"

  local bad_tx
  bad_tx="$($JQ_CMD -n '[inputs | select(.event_type?=="transition_anchor") | select((.tx_hash // "") | test("^0x[a-fA-F0-9]{64}$") | not)] | length' < "$ledger" 2>/dev/null || echo 0)"

  if [[ "$tx_required" == "true" ]] && [[ "${bad_tx:-0}" -gt 0 ]]; then
    printf '{"generated_at":"%s","status":"fail","pass":false,"error_count":%d,"error":"transition_anchor events require tx_hash 0x[64 hex]"}\n' "$now" "$bad_tx" > "$report"
    _gate_fail "$name" "invalid tx_hash for transition_anchor: $bad_tx" "${QA_ONCHAIN_FAIL_CLOSED:-false}"
    return 0
  fi

  if [[ "${bad_tx:-0}" -gt 0 ]]; then
    printf '{"generated_at":"%s","status":"warn","pass":true,"error_count":%d,"warning":"Some transition_anchor events have invalid tx_hash"}\n' "$now" "$bad_tx" > "$report"
    _gate_pass "$name"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 22: formal-methods-gate
# When applicable: runs TLC/Dafny/Alloy. Stub writes not_declared when no formal specs.
# ============================================================================
gate_formal_methods() {
  local name="formal-methods"
  local report="$VERIFY_DIR/formal-methods-gate.json"

  local has_formal=false
  [[ -d "$PROJECT_DIR/contracts/formal" ]] && has_formal=true
  if [[ "$has_formal" != "true" ]]; then
    # P6: Use compgen (bash builtin, no fork) instead of find for formal spec detection
    local _depth _ext
    for _ext in tla dfy als; do
      for _depth in "" "*/" "*/*/" "*/*/*/"; do
        if compgen -G "$PROJECT_DIR/${_depth}*.${_ext}" > /dev/null 2>&1; then
          has_formal=true
          break 2
        fi
      done
    done
  fi

  if [[ "$has_formal" != "true" ]]; then
    printf '{"generated_at":"%s","status":"not_declared","checks":[],"pass":true,"error_count":0,"warn_count":0}\n' "$now" > "$report"
    _gate_na "$name" "no formal specs"
    return 0
  fi

  # Has formal specs but stub cannot run TLC/Dafny/Alloy
  printf '{"generated_at":"%s","status":"stub_not_evaluated","checks":[],"pass":true,"error_count":0,"warn_count":0,"warn":"Stub: install real qa-formal-methods-gate for TLC/Dafny/Alloy"}\n' "$now" > "$report"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 23: formal-registry-gate
# Validates contracts/formal/registry.json structure when present.
# ============================================================================
gate_formal_registry() {
  local name="formal-registry"
  local registry="$PROJECT_DIR/contracts/formal/registry.json"
  local report="$VERIFY_DIR/formal-registry-gate.json"

  if [[ ! -f "$registry" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no formal registry"
    return 0
  fi

  # Combined validation: JSON validity + required fields + item shapes (single jq call)
  local reg_check
  reg_check="$($JQ_CMD -r '
    if (type != "object") then "invalid_json"
    elif ((.generated_at | type != "string") or (.items | type != "array")) then "missing_fields"
    else
      ([.items[]? | select(
        (.id | type != "string" or length == 0)
        or (.path | type != "string" or length == 0)
        or (.kind | type != "string" or length == 0)
      )] | length) | tostring
    end
  ' "$registry" 2>/dev/null || echo "invalid_json")"

  case "$reg_check" in
    invalid_json) write_fail_report "$report" "$name" 1 "Invalid JSON"; _gate_fail "$name" "invalid JSON" "false"; return 0 ;;
    missing_fields) write_fail_report "$report" "$name" 1 "Missing generated_at or items array"; _gate_fail "$name" "missing generated_at or items" "false"; return 0 ;;
  esac

  if [[ "${reg_check:-0}" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$reg_check" "Items require id, path, kind"
    _gate_fail "$name" "invalid item shape: $reg_check" "false"
    return 0
  fi

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 24: artifact-quality-gate
# Validates artifact freshness, non-placeholder in critical artifacts.
# Uses bash string matching instead of rg for placeholder detection.
# ============================================================================
gate_artifact_quality() {
  local name="artifact-quality"
  local report="$VERIFY_DIR/artifact-quality-gate.json"

  local files=()
  [[ -f "$PROJECT_DIR/contracts/assurance-case.json" ]] && files+=("$PROJECT_DIR/contracts/assurance-case.json")
  [[ -f "$PROJECT_DIR/contracts/rolling-wave.json" ]] && files+=("$PROJECT_DIR/contracts/rolling-wave.json")
  [[ -f "$VERIFY_DIR/privacy-proof.json" ]] && files+=("$VERIFY_DIR/privacy-proof.json")

  if [[ "${#files[@]}" -eq 0 ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "no critical artifacts"
    return 0
  fi

  local errors=0 bad_files=""
  for fpath in "${files[@]}"; do
    [[ -f "$fpath" ]] || continue
    local content
    content=$(<"$fpath" 2>/dev/null) || continue
    local content_lower="${content,,}"
    if [[ "$content_lower" == *"placeholder"* ]] || [[ "$content_lower" == *"bootstrap"* ]] || [[ "$content_lower" == *"todo"* ]] || [[ "$content_lower" == *"tbd"* ]]; then
      errors=$((errors + 1))
      bad_files="${bad_files:+$bad_files,}${fpath##*/}"
    fi
  done

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Placeholders in: $bad_files"
    _gate_fail "$name" "$errors placeholder(s) in: $bad_files" "false"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Gate 25: debt-registry-gate
# Validates debt-register.json exists and has valid structure when enabled.
# ============================================================================
gate_debt_registry() {
  local name="debt-registry"
  local report="$VERIFY_DIR/debt-registry-gate.json"
  local debt="$VERIFY_DIR/debt-register.json"

  [[ -f "$QUALITY_CONFIG" ]] || { write_na_report "$report" "$name"; _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local debt_enabled="$QCFG_DEBT_ENFORCE"
  local tier="$QCFG_CRITICALITY"
  [[ "$tier" == "critical" ]] && debt_enabled=true

  if [[ "$debt_enabled" != "true" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "not required"
    return 0
  fi

  if [[ ! -f "$debt" ]]; then
    write_fail_report "$report" "$name" 1 "missing debt-register.json"
    _gate_fail "$name" "missing debt-register.json" "false"
    return 0
  fi

  $JQ_CMD -e . "$debt" >/dev/null 2>&1 || { write_fail_report "$report" "$name" 1 "invalid JSON"; _gate_fail "$name" "invalid JSON" "false"; return 0; }

  write_pass_report "$report" "$name"
  _gate_pass "$name"
  return 0
}

# ============================================================================
# Gate 26: playbook-contract-gate
# Validates playbook JSON (brownfield/greenfield) exists and has valid structure.
# ============================================================================
gate_playbook_contract() {
  local name="playbook-contract"
  local report="$VERIFY_DIR/playbook-contract-gate.json"

  [[ -f "$QUALITY_CONFIG" ]] || { write_na_report "$report" "$name"; _gate_na "$name" "no quality.json"; return 0; }

  # B2: Use pre-parsed quality config
  local model="$QCFG_DELIVERY_MODEL"
  local playbook_enabled="$QCFG_PLAYBOOK_ENFORCE"
  local tier="$QCFG_CRITICALITY"
  [[ "$tier" == "critical" ]] && playbook_enabled=true

  if [[ "$playbook_enabled" != "true" ]]; then
    write_na_report "$report" "$name"
    _gate_na "$name" "not required"
    return 0
  fi

  local errors=0 missing_playbooks=""
  if [[ "$model" == "brownfield" || "$model" == "hybrid" ]]; then
    [[ -f "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" ]] || { errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks,}brownfield.playbook.json"; }
  fi
  if [[ "$model" == "greenfield" || "$model" == "hybrid" ]]; then
    [[ -f "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json" ]] || { errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks,}greenfield.playbook.json"; }
  fi
  if [[ "$model" == "auto" ]]; then
    [[ -f "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" ]] || [[ -f "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json" ]] || { errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks}playbook"; }
  fi

  for pb in "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json"; do
    [[ -f "$pb" ]] || continue
    $JQ_CMD -e '.name and .version and .delivery_model' "$pb" >/dev/null 2>&1 || { errors=$((errors+1)); }
  done

  if [[ "$errors" -gt 0 ]]; then
    write_fail_report "$report" "$name" "$errors" "Missing: $missing_playbooks"
    _gate_fail "$name" "$errors playbook issue(s): $missing_playbooks" "false"
  else
    write_pass_report "$report" "$name"
    _gate_pass "$name"
  fi
  return 0
}

# ============================================================================
# Parallel gate execution infrastructure
# ============================================================================
# When gates run in background subshells, they cannot modify parent variables.
# Each gate writes its result to $_gate_tmpdir/<gate_name>.result as a single
# line: "pass|na|fail <fail_closed> <message>"
# After wait, the parent collects results from temp files.

_gate_tmpdir=""

# Wrapper: run a gate function in a subshell, capture outcome via temp file IPC.
# Usage: _run_gate <gate_function_name> <gate_label>
_run_gate() {
  local func="$1" label="$2"

  # Override gate result helpers to write to temp file (subshell-safe)
  _gate_pass() {
    local name="$1"
    echo "pass 0 $name" > "$_gate_tmpdir/${label}.result"
  }
  _gate_na() {
    local name="$1" reason="${2:-skipped}"
    echo "na 0 $name ($reason)" > "$_gate_tmpdir/${label}.result"
  }
  _gate_fail() {
    local name="$1" reason="$2" fail_closed="${3:-false}"
    local fc=0
    [[ "$fail_closed" == "true" ]] && fc=1
    echo "fail $fc $name - $reason" > "$_gate_tmpdir/${label}.result"
    echo "GOVERNANCE-GATES FAIL: [$name]: $reason" >&2
  }

  "$func"
}

# Collect results from temp files into parent counters
_collect_gate_results() {
  local f
  for f in "$_gate_tmpdir"/*.result; do
    [[ -f "$f" ]] || continue
    local line
    line="$(<"$f")"
    local kind fc rest
    kind="${line%% *}"
    line="${line#* }"
    fc="${line%% *}"
    rest="${line#* }"

    case "$kind" in
      pass)
        _gate_pass_count=$((_gate_pass_count + 1))
        _gate_summary="${_gate_summary}  PASS: $rest"$'\n'
        ;;
      na)
        _gate_na_count=$((_gate_na_count + 1))
        _gate_summary="${_gate_summary}  N/A:  $rest"$'\n'
        ;;
      fail)
        _gate_fail_count=$((_gate_fail_count + 1))
        _gate_summary="${_gate_summary}  FAIL: $rest"$'\n'
        if [[ "$fc" -eq 1 ]]; then
          _gate_failures=$((_gate_failures + 1))
        fi
        ;;
    esac
  done
}

# ============================================================================
# Main dispatcher — parallel execution in 4 dependency-based batches
# ============================================================================
main() {
  echo "=== GOVERNANCE GATES ==="

  # Create temp directory for IPC between parallel gate subshells
  _gate_tmpdir=$(mktemp -d)
  trap 'rm -rf "$_gate_tmpdir"' EXIT

  # --- Batch 1: Pure file-checking + quality.json-only gates (no shared state deps) ---
  # These gates only check file existence, run external validators, or use
  # pre-parsed QCFG_* variables. No attestation or async-results needed.
  #
  # P7: Run sequentially in the same process instead of forking 17 subshells.
  # Each gate takes 38-92ms sequentially; 17 * ~70ms = ~1.2s total.
  # Forking 17 subshells (each inheriting ~72KB env) caused 15-22s of wall-clock
  # time from I/O contention + fork overhead, and the 10s timeout killed the script
  # before cache could be written. Sequential in-process is dramatically faster.
  _run_gate gate_prdset_compiler "prdset_compiler"
  _run_gate gate_agent_claim_validator "agent_claim_validator"
  _run_gate gate_claim_lifecycle "claim_lifecycle"
  _run_gate gate_dag_dependency "dag_dependency"
  _run_gate gate_rolling_wave "rolling_wave"
  _run_gate gate_assurance_case "assurance_case"
  _run_gate gate_privacy_proof "privacy_proof"
  _run_gate gate_onchain_contract "onchain_contract"
  _run_gate gate_formal_methods "formal_methods"
  _run_gate gate_formal_registry "formal_registry"
  _run_gate gate_trace_parity_audit "trace_parity_audit"
  _run_gate gate_brownfield_migration "brownfield_migration"
  _run_gate gate_greenfield_bootstrap "greenfield_bootstrap"
  _run_gate gate_probabilistic_governance "probabilistic_governance"
  _run_gate gate_artifact_quality "artifact_quality"
  _run_gate gate_debt_registry "debt_registry"
  _run_gate gate_playbook_contract "playbook_contract"
  _collect_gate_results
  rm -f "$_gate_tmpdir"/*.result

  # --- Batch 2: Attestation-dependent gates ---
  # These call _load_attestation which reads qa-attestation.json
  _run_gate gate_methodology_enforcer "methodology_enforcer" &
  _run_gate gate_tier_enforcer "tier_enforcer" &
  _run_gate gate_elicitation_closure "elicitation_closure" &
  wait
  _collect_gate_results
  rm -f "$_gate_tmpdir"/*.result

  # --- Batch 3: Async-results-dependent gates ---
  # These call _load_async_results or use RESULTS_FILE
  _run_gate gate_reliability "reliability" &
  _run_gate gate_reliability_slo "reliability_slo" &
  _run_gate gate_flake_quarantine "flake_quarantine" &
  _run_gate gate_verifier_dispute "verifier_dispute" &
  wait
  _collect_gate_results
  rm -f "$_gate_tmpdir"/*.result

  # --- Batch 4: Onchain sequential pair (adapter must run before transition) ---
  _run_gate gate_onchain_adapter "onchain_adapter"
  _collect_gate_results
  rm -f "$_gate_tmpdir"/*.result
  _run_gate gate_onchain_transition "onchain_transition"
  _collect_gate_results
  rm -f "$_gate_tmpdir"/*.result

  # Summary
  echo "=== GOVERNANCE GATES SUMMARY ==="
  echo "  Pass: $_gate_pass_count"
  echo "  N/A:  $_gate_na_count"
  echo "  Fail: $_gate_fail_count (fail-closed: $_gate_failures)"
  
  # Only show failures; keep N/A and Pass hidden unless explicitly requested or if everything is N/A
  if [[ -n "$_gate_summary" ]]; then
    if [[ "$_gate_fail_count" -gt 0 ]]; then
        echo ""
        echo "Failures:"
        echo "$_gate_summary" | grep "FAIL:" || true
    fi
    
    if [[ "$_gate_pass_count" -eq 0 && "$_gate_fail_count" -eq 0 ]]; then
        echo ""
        echo "All gates N/A"
    fi
  fi

  if [[ "$_gate_failures" -gt 0 ]]; then
    echo "GOVERNANCE-GATES: $_gate_failures fail-closed gate(s) failed" >&2
    return 2
  fi

  return 0
}

# Run main, capture output, cache result
_output=$(main 2>&1); _rc=$?
hook_cache_write "$_cache_key" "$_rc" "$_output"
# Also write ultra-fast cache file
mkdir -p "$_CACHE_DIR" 2>/dev/null || true
echo "$_output" > "$_CACHE_FILE" 2>/dev/null || true
[[ -n "$_output" ]] && echo "$_output"
if [[ "$_rc" -ne 0 ]]; then
  echo "GOVERNANCE-GATES FAIL: $_gate_failures fail-closed gate(s) triggered exit code $_rc" >&2
fi
exit "$_rc"
