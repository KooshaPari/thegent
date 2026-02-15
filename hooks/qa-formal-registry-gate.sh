#!/usr/bin/env bash
# qa-formal-registry-gate.stub.sh
# Validates contracts/formal/registry.json structure when present.
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
REGISTRY="$PROJECT_DIR/contracts/formal/registry.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/formal-registry-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$REGISTRY" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "FORMAL REGISTRY GATE: pass (no formal registry)"
  exit 0
fi

# Validate JSON
jq -e . "$REGISTRY" >/dev/null 2>&1 || {
  echo "FORMAL REGISTRY GATE: fail (invalid JSON)" >&2
  jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"Invalid JSON"}' > "$REPORT"
  exit 2
}

# Required: generated_at, items array
jq -e '.generated_at and (.items | type == "array")' "$REGISTRY" >/dev/null 2>&1 || {
  echo "FORMAL REGISTRY GATE: fail (missing generated_at or items)" >&2
  jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"Missing generated_at or items array"}' > "$REPORT"
  exit 2
}

# Each item: id, path, kind
bad_items="$(jq -r '
  [.items[]? | select((.id | type != "string" or length == 0) or (.path | type != "string" or length == 0) or (.kind | type != "string" or length == 0))]
  | length
' "$REGISTRY" 2>/dev/null || echo 0)"
if [[ "${bad_items:-0}" -gt 0 ]]; then
  echo "FORMAL REGISTRY GATE: fail (invalid item shape: $bad_items)" >&2
  jq -n --arg ts "$now" --argjson c "$bad_items" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"Items require id, path, kind"}' > "$REPORT"
  exit 2
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "FORMAL REGISTRY GATE: pass"
exit 0
