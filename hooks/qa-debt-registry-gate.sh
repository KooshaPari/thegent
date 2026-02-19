#!/bin/zsh
# qa-debt-registry-gate.stub.sh
# Validates debt-register.json exists and has valid structure when debt registry enabled.
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
DEBT="$PROJECT_DIR/.claude/verification/debt-register.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/debt-registry-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

[[ -f "$QFILE" ]] || { jq -n --arg ts "$now" '{generated_at:$ts,status:"no_quality_config",pass:true,error_count:0}' > "$REPORT"; echo "DEBT REGISTRY GATE: pass (no quality.json)"; exit 0; }
debt_enabled="$(jq -r '.governance.debt_registry.enforce_gate // false' "$QFILE" 2>/dev/null || echo false)"
tier="$(jq -r '.criticality_tier // "established"' "$QFILE" 2>/dev/null || echo established)"
[[ "$tier" == "critical" ]] && debt_enabled=true

if [[ "$debt_enabled" != "true" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_required",pass:true,error_count:0}' > "$REPORT"
  echo "DEBT REGISTRY GATE: pass (not required)"
  exit 0
fi

if [[ ! -f "$DEBT" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"missing debt-register.json"}' > "$REPORT"
  echo "DEBT-REGISTRY FAIL: missing debt-register.json" >&2
  exit 2
fi

jq -e . "$DEBT" >/dev/null 2>&1 || { jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"invalid JSON"}' > "$REPORT"; echo "DEBT-REGISTRY FAIL: invalid JSON in debt-register.json" >&2; exit 2; }
jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "DEBT REGISTRY GATE: pass"
exit 0
