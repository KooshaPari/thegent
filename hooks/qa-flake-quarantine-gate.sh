#!/usr/bin/env bash
# qa-flake-quarantine-gate.sh
# N9: Manage flaky test quarantine ledger and expiry.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/flake-quarantine-gate.json"
RESULTS="$HOME/.claude/.async-test-results.json"
QUAR_DIR="$PROJECT_DIR/.claude/quarantine"
QUAR_FILE="$QUAR_DIR/flaky-tests.json"
FAIL_CLOSED="${QA_FLAKE_QUARANTINE_FAIL_CLOSED:-true}"

mkdir -p "$VERIFY_DIR" "$QUAR_DIR"

tier="established"
enabled=false
ttl_days=14
if [[ -f "$QFILE" ]]; then
  tier="$(jq -r '.criticality_tier // "established"' "$QFILE" 2>/dev/null || echo established)"
  enabled_cfg="$(jq -r '.governance.reliability.enforce_flake_quarantine // false' "$QFILE" 2>/dev/null || echo false)"
  [[ "$enabled_cfg" == "true" ]] && enabled=true
  ttl_days="$(jq -r '.governance.reliability.quarantine_ttl_days // 14' "$QFILE" 2>/dev/null || echo 14)"
fi
[[ "$tier" == "critical" ]] && enabled=true
[[ "${QA_RELIABILITY_REQUIRED:-false}" == "true" ]] && enabled=true

[[ -f "$QUAR_FILE" ]] || echo '{"generated_at":"","entries":[]}' > "$QUAR_FILE"

# determine flaky tests from async results, with tolerant parsing
flaky_tests='[]'
if [[ -f "$RESULTS" ]]; then
  flaky_tests="$(jq -c '
    if (.flaky_tests|type)=="array" then .flaky_tests
    elif (.tests|type)=="array" then [ .tests[] | select((.flaky // false)==true) | (.name // .id // empty) ]
    else [] end | map(select(type=="string" and length>0)) | unique
  ' "$RESULTS" 2>/dev/null || echo '[]')"
fi

now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# macOS date handling
exp_iso="$(date -u -v+${ttl_days}d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "+${ttl_days} days" +%Y-%m-%dT%H:%M:%SZ)"

# upsert active flaky tests
updated="$(jq -c --arg now "$now_iso" --arg exp "$exp_iso" --argjson flaky "$flaky_tests" '
  .entries = (
    (.entries // [])
    | map(if (.status // "active") == "active" then . else . end)
  )
  | reduce $flaky[] as $t (.;
      if any(.entries[]?; .test_id == $t and (.status // "active") == "active") then .
      else .entries += [{test_id:$t,reason:"detected_flaky",introduced_at:$now,expires_at:$exp,owner:"qa-system",status:"active"}] end
    )
  | .generated_at = $now
' "$QUAR_FILE" 2>/dev/null || cat "$QUAR_FILE")"

echo "$updated" > "$QUAR_FILE"

expired_count="$(jq '[.entries[]? | select((.status // "active") == "active" and (.expires_at // "") < "'"$now_iso"'")] | length' "$QUAR_FILE" 2>/dev/null || echo 0)"
active_count="$(jq '[.entries[]? | select((.status // "active") == "active")] | length' "$QUAR_FILE" 2>/dev/null || echo 0)"

err=0
warn=0
checks='[]'
if [[ "$expired_count" -gt 0 ]]; then
  if [[ "$enabled" == "true" ]]; then err=$((err+1)); else warn=$((warn+1)); fi
  checks="$(jq -c --argjson n "$expired_count" --arg s "$( [[ "$enabled" == "true" ]] && echo fail || echo warn )" '. + [{check:"expired_quarantine_entries",status:$s,count:$n}]' <<< "$checks")"
else
  checks="$(jq -c '. + [{check:"expired_quarantine_entries",status:"pass",count:0}]' <<< "$checks")"
fi

checks="$(jq -c --argjson n "$active_count" '. + [{check:"active_quarantine_entries",status:"info",count:$n}]' <<< "$checks")"

jq -n --arg ts "$now_iso" --arg tier "$tier" --argjson enabled "$enabled" --argjson err "$err" --argjson warn "$warn" --argjson checks "$checks" --argjson active "$active_count" --argjson expired "$expired_count" \
  '{generated_at:$ts,tier:$tier,enabled:$enabled,active_count:$active,expired_count:$expired,error_count:$err,warn_count:$warn,checks:$checks,pass:($err==0)}' > "$REPORT"

echo "FLAKE QUARANTINE GATE: tier=$tier enabled=$enabled active=$active_count expired=$expired_count err=$err warn=$warn report=$REPORT"
if [[ "$FAIL_CLOSED" == "true" && "$enabled" == "true" && "$err" -gt 0 ]]; then
  echo "FLAKE QUARANTINE GATE FAIL: expired quarantine entries present" >&2
  exit 2
fi
exit 0
