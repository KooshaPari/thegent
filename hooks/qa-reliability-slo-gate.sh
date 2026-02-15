#!/usr/bin/env bash
# qa-reliability-slo-gate.sh
# N9: Reliability SLO gate with progressive enforcement.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/reliability-slo-gate.json"
RESULTS="$HOME/.claude/.async-test-results.json"
FAIL_CLOSED="${QA_RELIABILITY_SLO_FAIL_CLOSED:-true}"

mkdir -p "$VERIFY_DIR"

tier="established"
enabled=false
max_flake="0.10"
min_pass="0.90"
if [[ -f "$QFILE" ]]; then
  tier="$(jq -r '.criticality_tier // "established"' "$QFILE" 2>/dev/null || echo established)"
  enabled_cfg="$(jq -r '.governance.reliability.enforce_slo_gate // false' "$QFILE" 2>/dev/null || echo false)"
  [[ "$enabled_cfg" == "true" ]] && enabled=true
  max_flake="$(jq -r '.governance.reliability.max_flake_rate // 0.10' "$QFILE" 2>/dev/null || echo 0.10)"
  min_pass="$(jq -r '.governance.reliability.min_pass_rate // 0.90' "$QFILE" 2>/dev/null || echo 0.90)"
fi
[[ "$tier" == "critical" ]] && enabled=true
[[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

if [[ ! -f "$RESULTS" ]]; then
  jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tier "$tier" --argjson enabled "$enabled" \
    '{generated_at:$ts,tier:$tier,enabled:$enabled,status:"no_results",error_count:0,warn_count:0,pass:true}' > "$REPORT"
  echo "RELIABILITY SLO GATE: no async results"
  exit 0
fi

total="$(jq '.total // 0' "$RESULTS" 2>/dev/null || echo 0)"
failed="$(jq '.failed // 0' "$RESULTS" 2>/dev/null || echo 0)"
flaky="$(jq '.flaky // 0' "$RESULTS" 2>/dev/null || echo 0)"

if [[ "$total" -le 0 ]]; then
  jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tier "$tier" --argjson enabled "$enabled" \
    '{generated_at:$ts,tier:$tier,enabled:$enabled,status:"empty_results",error_count:0,warn_count:1,pass:true}' > "$REPORT"
  echo "RELIABILITY SLO GATE: total=0"
  exit 0
fi

flake_rate="$(awk -v f="$flaky" -v t="$total" 'BEGIN { printf "%.4f", (t==0?0:f/t) }')"
pass_rate="$(awk -v f="$failed" -v t="$total" 'BEGIN { printf "%.4f", (t==0?1:(t-f)/t) }')"

err=0
warn=0
checks='[]'

if awk -v x="$flake_rate" -v y="$max_flake" 'BEGIN{exit !(x>y)}'; then
  if [[ "$enabled" == "true" ]]; then err=$((err+1)); else warn=$((warn+1)); fi
  checks="$(jq -c --arg v "$flake_rate" --arg t "$max_flake" --arg s "$( [[ "$enabled" == "true" ]] && echo fail || echo warn )" '. + [{check:"max_flake_rate",status:$s,value:$v,threshold:$t}]' <<< "$checks")"
else
  checks="$(jq -c --arg v "$flake_rate" --arg t "$max_flake" '. + [{check:"max_flake_rate",status:"pass",value:$v,threshold:$t}]' <<< "$checks")"
fi

if awk -v x="$pass_rate" -v y="$min_pass" 'BEGIN{exit !(x<y)}'; then
  if [[ "$enabled" == "true" ]]; then err=$((err+1)); else warn=$((warn+1)); fi
  checks="$(jq -c --arg v "$pass_rate" --arg t "$min_pass" --arg s "$( [[ "$enabled" == "true" ]] && echo fail || echo warn )" '. + [{check:"min_pass_rate",status:$s,value:$v,threshold:$t}]' <<< "$checks")"
else
  checks="$(jq -c --arg v "$pass_rate" --arg t "$min_pass" '. + [{check:"min_pass_rate",status:"pass",value:$v,threshold:$t}]' <<< "$checks")"
fi

jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tier "$tier" --argjson enabled "$enabled" \
  --argjson err "$err" --argjson warn "$warn" --argjson total "$total" --argjson failed "$failed" --argjson flaky "$flaky" \
  --arg flake_rate "$flake_rate" --arg pass_rate "$pass_rate" --argjson checks "$checks" \
  '{generated_at:$ts,tier:$tier,enabled:$enabled,metrics:{total:$total,failed:$failed,flaky:$flaky,flake_rate:($flake_rate|tonumber),pass_rate:($pass_rate|tonumber)},error_count:$err,warn_count:$warn,checks:$checks,pass:($err==0)}' > "$REPORT"

echo "RELIABILITY SLO GATE: tier=$tier enabled=$enabled err=$err warn=$warn report=$REPORT"
if [[ "$FAIL_CLOSED" == "true" && "$enabled" == "true" && "$err" -gt 0 ]]; then
  echo "RELIABILITY SLO GATE FAIL: $err SLO check(s) failed" >&2
  exit 2
fi
exit 0
