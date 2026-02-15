#!/usr/bin/env bash
# qa-onchain-transition-gate.sh
# Validates onchain transition receipts: when onchain-ledger.jsonl exists and has transition_anchor events, tx_hash must match 0x[64 hex].
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
LEDGER="$PROJECT_DIR/.claude/verification/onchain-ledger.jsonl"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/onchain-transition-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$LEDGER" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "ONCHAIN TRANSITION GATE: pass (no onchain-ledger)"
  exit 0
fi

# Check if onchain is applicable
tx_required=false
[[ -f "$QFILE" ]] && tx_required="$(jq -r '.governance.onchain.require_tx_hash // false' "$QFILE" 2>/dev/null || echo false)"

# Validate transition_anchor events: tx_hash must match 0x + 64 hex chars (JSONL: one JSON per line)
bad_tx="$(jq -n '[inputs | select(.event_type?=="transition_anchor") | select((.tx_hash // "") | test("^0x[a-fA-F0-9]{64}$") | not)] | length' < "$LEDGER" 2>/dev/null || echo 0)"

# When tx_hash required and we have transition_anchor events, enforce format
if [[ "$tx_required" == "true" ]] && [[ "${bad_tx:-0}" -gt 0 ]]; then
  echo "ONCHAIN TRANSITION GATE: fail (invalid tx_hash for transition_anchor: $bad_tx)" >&2
  jq -n --arg ts "$now" --argjson c "$bad_tx" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"transition_anchor events require tx_hash 0x[64 hex]"}' > "$REPORT"
  exit 2
fi

# When ledger exists, validate all transition_anchor tx_hash format (even if not required)
if [[ "${bad_tx:-0}" -gt 0 ]]; then
  echo "ONCHAIN TRANSITION GATE: warn ($bad_tx transition_anchor with invalid tx_hash)" >&2
  jq -n --arg ts "$now" --argjson c "$bad_tx" '{generated_at:$ts,status:"warn",pass:true,error_count:$c,warning:"Some transition_anchor events have invalid tx_hash"}' > "$REPORT"
else
  jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
fi
echo "ONCHAIN TRANSITION GATE: pass"
exit 0
