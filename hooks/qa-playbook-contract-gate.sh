#!/bin/zsh
# qa-playbook-contract-gate.stub.sh (N14)
# Validates playbook JSON (brownfield/greenfield) exists and has valid structure.
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/playbook-contract-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

[[ -f "$QFILE" ]] || { jq -n --arg ts "$now" '{generated_at:$ts,status:"no_quality_config",pass:true,error_count:0}' > "$REPORT"; echo "PLAYBOOK CONTRACT GATE: pass (no quality.json)"; exit 0; }
model="$(jq -r '.governance.delivery_model // "auto"' "$QFILE" 2>/dev/null || echo auto)"
playbook_enabled="$(jq -r '.governance.playbooks.enforce_gate // false' "$QFILE" 2>/dev/null || echo false)"
tier="$(jq -r '.criticality_tier // "established"' "$QFILE" 2>/dev/null || echo established)"
[[ "$tier" == "critical" ]] && playbook_enabled=true

if [[ "$playbook_enabled" != "true" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_required",pass:true,error_count:0}' > "$REPORT"
  echo "PLAYBOOK CONTRACT GATE: pass (not required)"
  exit 0
fi

errors=0
missing_playbooks=""
if [[ "$model" == "brownfield" || "$model" == "hybrid" ]]; then
  [[ -f "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" ]] || { echo "PLAYBOOK: missing brownfield.playbook.json" >&2; errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks,}brownfield.playbook.json"; }
fi
if [[ "$model" == "greenfield" || "$model" == "hybrid" ]]; then
  [[ -f "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json" ]] || { echo "PLAYBOOK: missing greenfield.playbook.json" >&2; errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks,}greenfield.playbook.json"; }
fi
if [[ "$model" == "auto" ]]; then
  [[ -f "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" ]] || [[ -f "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json" ]] || { echo "PLAYBOOK: no playbook found" >&2; errors=$((errors+1)); missing_playbooks="${missing_playbooks:+$missing_playbooks}playbook"; }
fi

for pb in "$PROJECT_DIR/contracts/playbooks/brownfield.playbook.json" "$PROJECT_DIR/contracts/playbooks/greenfield.playbook.json"; do
  [[ -f "$pb" ]] || continue
  jq -e '.name and .version and .delivery_model' "$pb" >/dev/null 2>&1 || { echo "PLAYBOOK: invalid structure in $(basename "$pb")" >&2; errors=$((errors+1)); }
done

if [[ "$errors" -gt 0 ]]; then
  jq -n --arg ts "$now" --argjson e "$errors" --arg m "$missing_playbooks" '{generated_at:$ts,status:"fail",pass:false,error_count:$e,missing:$m}' > "$REPORT"
  echo "PLAYBOOK-CONTRACT FAIL: $errors playbook issue(s)" >&2
  exit 2
fi
jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "PLAYBOOK CONTRACT GATE: pass"
exit 0
