#!/usr/bin/env bash
# qa-verifier-dispute-gate.sh
# N9: Ensure verifier dispute/challenge workflow exists and open disputes are auditable.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/verifier-dispute-gate.json"
DISPUTES="$VERIFY_DIR/disputes.jsonl"
FAIL_CLOSED="${QA_DISPUTE_FAIL_CLOSED:-true}"

mkdir -p "$VERIFY_DIR"

tier="established"
enabled=false
max_open_days=14
if [[ -f "$QFILE" ]]; then
  tier="$(jq -r '.criticality_tier // "established"' "$QFILE" 2>/dev/null || echo established)"
  enabled_cfg="$(jq -r '.governance.reliability.enforce_dispute_gate // false' "$QFILE" 2>/dev/null || echo false)"
  [[ "$enabled_cfg" == "true" ]] && enabled=true
  max_open_days="$(jq -r '.governance.reliability.max_dispute_open_days // 14' "$QFILE" 2>/dev/null || echo 14)"
fi
[[ "$tier" == "critical" ]] && enabled=true
[[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

err=0
warn=0
checks='[]'

# policy text presence
policy_present=false
policy_files=()
[[ -f "$PROJECT_DIR/VERIFICATION_POLICY.md" ]] && policy_files+=("$PROJECT_DIR/VERIFICATION_POLICY.md")
[[ -f "$PROJECT_DIR/RELEASE_CONTRACT.md" ]] && policy_files+=("$PROJECT_DIR/RELEASE_CONTRACT.md")
if (( ${#policy_files[@]} > 0 )) && rg -q -S 'dispute|challenge|appeal|verifier escalation' "${policy_files[@]}" 2>/dev/null; then
  policy_present=true
fi
if [[ "$policy_present" == "true" ]]; then
  checks="$(jq -c '. + [{check:"dispute_policy_text",status:"pass"}]' <<< "$checks")"
else
  if [[ "$enabled" == "true" ]]; then err=$((err+1)); else warn=$((warn+1)); fi
  checks="$(jq -c --arg s "$( [[ "$enabled" == "true" ]] && echo fail || echo warn )" '. + [{check:"dispute_policy_text",status:$s}]' <<< "$checks")"
fi

open_count=0
if [[ -f "$DISPUTES" ]]; then
  open_count="$(jq -s '[.[] | select((.status // "") == "open" or (.status // "") == "under_review")] | length' "$DISPUTES" 2>/dev/null || echo 0)"
else
  : > "$DISPUTES"
fi
checks="$(jq -c --argjson n "$open_count" '. + [{check:"open_disputes",status:"info",count:$n}]' <<< "$checks")"

jq -n --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg tier "$tier" --argjson enabled "$enabled" --argjson err "$err" --argjson warn "$warn" --argjson checks "$checks" --argjson open "$open_count" --argjson max_days "$max_open_days" \
  '{generated_at:$ts,tier:$tier,enabled:$enabled,policy:{max_dispute_open_days:$max_days},open_disputes:$open,error_count:$err,warn_count:$warn,checks:$checks,pass:($err==0)}' > "$REPORT"

echo "DISPUTE GATE: tier=$tier enabled=$enabled open=$open_count err=$err warn=$warn report=$REPORT"
if [[ "$FAIL_CLOSED" == "true" && "$enabled" == "true" && "$err" -gt 0 ]]; then
  echo "DISPUTE GATE FAIL: dispute workflow requirements not satisfied" >&2
  exit 2
fi
exit 0
