#!/usr/bin/env bash
# qa-privacy-proof-gate.stub.sh (N13)
# Validates privacy-proof.json when present. Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
PROOF="$PROJECT_DIR/.claude/verification/privacy-proof.json"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/privacy-proof-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$PROOF" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "PRIVACY PROOF GATE: pass (no privacy-proof.json)"
  exit 0
fi

jq -e . "$PROOF" >/dev/null 2>&1 || { jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"invalid JSON"}' > "$REPORT"; echo "PRIVACY-PROOF FAIL: invalid JSON in privacy-proof.json" >&2; exit 2; }

zk_required=false
[[ -f "$QFILE" ]] && zk_required="$(jq -r '.governance.privacy_preserving.zk_required // false' "$QFILE" 2>/dev/null || echo false)"
if [[ "$zk_required" == "true" ]]; then
  jq -e '
    (.generated_at | type == "string")
    and (.proof_system | type == "string")
    and (.statement_hash | type == "string")
    and (.proof_hash | type == "string")
    and (.verified | type == "boolean")
    and (.scope | type == "string")
  ' "$PROOF" >/dev/null 2>&1 || { jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"invalid schema shape when zk_required"}' > "$REPORT"; echo "PRIVACY-PROOF FAIL: invalid schema shape when zk_required" >&2; exit 2; }
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "PRIVACY PROOF GATE: pass"
exit 0
