#!/usr/bin/env bash
# qa-brownfield-migration-gate.stub.sh (N6)
# Validates brownfield migration evidence: characterization, canary, rollback, strangler.
# Install via: make install-governance-hooks
set -euo pipefail

_exit_trap() {
  local r=$?
  if [[ $r -ne 0 ]]; then
    echo "BROWNFIELD MIGRATION GATE: unexpected exit $r" >&2
  fi
}
trap _exit_trap EXIT

INPUT="$(cat)" || true
INPUT="${INPUT:-{}}"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT" 2>/dev/null || echo "")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/brownfield-migration-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

[[ -f "$QFILE" ]] || { jq -n --arg ts "$now" '{generated_at:$ts,status:"no_quality_config",pass:true,error_count:0}' > "$REPORT"; echo "BROWNFIELD MIGRATION GATE: pass (no quality.json)"; exit 0; }
model="$(jq -r '.governance.delivery_model // "auto"' "$QFILE" 2>/dev/null || echo auto)"

if [[ "$model" != "brownfield" && "$model" != "hybrid" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_brownfield",pass:true,error_count:0}' > "$REPORT"
  echo "BROWNFIELD MIGRATION GATE: pass (not brownfield)"
  exit 0
fi

errors=0
missing=""
[[ -d "$PROJECT_DIR/test/characterization" ]] || { echo "BROWNFIELD: missing test/characterization/" >&2; errors=$((errors+1)); missing="${missing:+$missing }test/characterization/"; }
[[ -f "$PROJECT_DIR/.claude/verification/canary-report.json" ]] || { echo "BROWNFIELD: missing canary-report.json" >&2; errors=$((errors+1)); missing="${missing:+$missing }canary-report.json"; }
[[ -f "$PROJECT_DIR/.claude/verification/rollback-drill.json" ]] || { echo "BROWNFIELD: missing rollback-drill.json" >&2; errors=$((errors+1)); missing="${missing:+$missing }rollback-drill.json"; }
[[ -f "$PROJECT_DIR/contracts/strangler-plan.json" ]] || [[ -f "$PROJECT_DIR/docs/migration/STRANGLER_PLAN.md" ]] || { echo "BROWNFIELD: missing strangler plan" >&2; errors=$((errors+1)); missing="${missing:+$missing }strangler-plan"; }

if [[ "$errors" -gt 0 ]]; then
  jq -n --arg ts "$now" --argjson e "$errors" --arg m "$missing" '{generated_at:$ts,status:"fail",pass:false,error_count:$e,missing:$m}' > "$REPORT"
  echo "BROWNFIELD MIGRATION GATE: fail ($errors missing)" >&2
  exit 2
fi
jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "BROWNFIELD MIGRATION GATE: pass"
exit 0
