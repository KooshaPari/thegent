#!/bin/zsh
# qa-agent-claim-validator.sh (N10)
# Validates agent-statement.json against schema; enforces claim transitions (observation/claim/decision/risk require evidence).
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCHEMA="$REPO_ROOT/schemas/agent-statement.schema.json"
STMT="$PROJECT_DIR/.claude/verification/agent-statement.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/agent-claim-validator.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$STMT" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "AGENT CLAIM VALIDATOR: pass (no agent-statement.json)"
  exit 0
fi

errors=0

# Schema validation
if [[ -f "$SCHEMA" ]] && [[ -f "$REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
  if ! bash "$REPO_ROOT/scripts/validate-json-schema.sh" "$SCHEMA" "$STMT" 2>/dev/null; then
    echo "AGENT CLAIM VALIDATOR: fail (schema validation)" >&2
    jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"Schema validation failed"}' > "$REPORT"
    exit 2
  fi
fi

# Claim transitions: observation/claim/decision/risk must have evidence
bad_stmts="$(jq -r '
  [.statements[]? | select(.kind | IN("observation","claim","decision","risk")) | select((.evidence | type != "array") or (.evidence | length == 0))]
  | length
' "$STMT" 2>/dev/null || echo 0)"
if [[ "${bad_stmts:-0}" -gt 0 ]]; then
  echo "AGENT CLAIM VALIDATOR: fail (claims without evidence: $bad_stmts)" >&2
  jq -n --arg ts "$now" --argjson c "$bad_stmts" '{generated_at:$ts,status:"fail",pass:false,error_count:$c,error:"Claims/observations/decisions/risks require evidence array"}' > "$REPORT"
  exit 2
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "AGENT CLAIM VALIDATOR: pass"
exit 0
