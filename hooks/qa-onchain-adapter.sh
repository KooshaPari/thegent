#!/bin/zsh
# qa-onchain-adapter.sh
# Mandatory on-chain workflow adapter with local anchoring and optional broadcast.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
CLAIM_FILE="$VERIFY_DIR/agent-statement.json"
LEDGER_FILE="$VERIFY_DIR/claim-lifecycle.json"
OUT_FILE="$VERIFY_DIR/onchain-payload.json"
ANCHOR_LEDGER="$VERIFY_DIR/onchain-ledger.jsonl"
FAIL_CLOSED="${QA_ONCHAIN_FAIL_CLOSED:-true}"

if [[ ! -f "$CLAIM_FILE" || ! -f "$LEDGER_FILE" ]]; then
  # Anchor a deterministic no-claim checkpoint so on-chain workflow remains mandatory.
  jq -n \
    --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg project "$PROJECT_DIR" \
    --arg type "no_claim_checkpoint" \
    '{generated_at:$generated_at,project_dir:$project,event_type:$type}' > "$OUT_FILE"
  hash="$(shasum -a 256 "$OUT_FILE" | awk '{print $1}')"
  jq -cn --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg hash "$hash" --arg payload "$OUT_FILE" \
    '{timestamp:$ts,event_type:"no_claim_checkpoint",payload:$payload,sha256:$hash,broadcasted:false}' >> "$ANCHOR_LEDGER"
  echo "ONCHAIN ADAPTER: checkpoint anchored payload=$OUT_FILE sha256=$hash"
  exit 0
fi

item_id="$(jq -r '.item_id // empty' "$CLAIM_FILE")"
next_state="$(jq -r '.next_state // ""' "$LEDGER_FILE")"
spec_hash="$(jq -r '.spec_hash // empty' "$CLAIM_FILE")"

state_id=""
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

jq -n \
  --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg project "$PROJECT_DIR" \
  --arg item_id "$item_id" \
  --arg spec_hash "$spec_hash" \
  --arg next_state "$next_state" \
  --argjson state_id "${state_id:-null}" \
  '{
    generated_at:$generated_at,
    project_dir:$project,
    item_id:$item_id,
    spec_hash:$spec_hash,
    next_state:$next_state,
    state_id:$state_id
  }' > "$OUT_FILE"

hash="$(shasum -a 256 "$OUT_FILE" | awk '{print $1}')"
broadcasted=false
tx_hash=""

# Optional broadcast with foundry cast
if [[ "${QA_ONCHAIN_BROADCAST:-false}" == "true" ]]; then
  : "${QA_ONCHAIN_RPC_URL:?missing QA_ONCHAIN_RPC_URL}"
  : "${QA_ONCHAIN_CONTRACT:?missing QA_ONCHAIN_CONTRACT}"
  : "${QA_ONCHAIN_PRIVATE_KEY:?missing QA_ONCHAIN_PRIVATE_KEY}"
  if ! command -v cast >/dev/null 2>&1; then
    echo "ONCHAIN ADAPTER: cast not installed"
    [[ "$FAIL_CLOSED" == "true" ]] && { echo "ONCHAIN ADAPTER FAIL: cast (foundry) not installed for on-chain broadcast" >&2; exit 2; } || exit 0
  fi
  if [[ -z "$item_id" || -z "$state_id" ]]; then
    echo "ONCHAIN ADAPTER: missing item/state payload"
    [[ "$FAIL_CLOSED" == "true" ]] && { echo "ONCHAIN ADAPTER FAIL: missing item_id or state_id in on-chain payload" >&2; exit 2; } || exit 0
  fi

  out="$(
    cast send "$QA_ONCHAIN_CONTRACT" \
    "transition(bytes32,uint8)" \
    "$item_id" "$state_id" \
    --rpc-url "$QA_ONCHAIN_RPC_URL" \
    --private-key "$QA_ONCHAIN_PRIVATE_KEY" 2>&1
  )"
  broadcasted=true
  tx_hash="$(printf '%s' "$out" | rg -o -m1 '0x[a-fA-F0-9]{64}' || true)"
  echo "ONCHAIN ADAPTER: broadcast complete"
fi

jq -cn \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg hash "$hash" \
  --arg payload "$OUT_FILE" \
  --arg item_id "$item_id" \
  --arg spec_hash "$spec_hash" \
  --arg next_state "$next_state" \
  --argjson state_id "${state_id:-null}" \
  --argjson broadcasted "$broadcasted" \
  --arg tx_hash "$tx_hash" \
  '{timestamp:$ts,event_type:"transition_anchor",payload:$payload,sha256:$hash,item_id:$item_id,spec_hash:$spec_hash,next_state:$next_state,state_id:$state_id,broadcasted:$broadcasted,tx_hash:$tx_hash}' >> "$ANCHOR_LEDGER"

echo "ONCHAIN ADAPTER: payload=$OUT_FILE sha256=$hash ledger=$ANCHOR_LEDGER"

exit 0
