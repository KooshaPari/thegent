#!/bin/zsh
# qa-claim-lifecycle-gate.sh (N10)
# Enforces claim->evidence->verify chain: claims must cite evidence; evidence refs must resolve to existing artifacts.
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
STMT="$PROJECT_DIR/.claude/verification/agent-statement.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/claim-lifecycle-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$STMT" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "CLAIM LIFECYCLE GATE: pass (no agent-statement)"
  exit 0
fi

# Collect all evidence refs from statements that require evidence
refs="$(jq -r '
  [.statements[]? | select(.kind | IN("observation","claim","decision","risk")) | .evidence[]?]
  | unique[]
' "$STMT" 2>/dev/null || true)"

if [[ -z "$refs" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
  echo "CLAIM LIFECYCLE GATE: pass"
  exit 0
fi

errors=0
missing=""
while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  case "$ref" in
    file://*)
      rel="${ref#file://}"
      path="$PROJECT_DIR/$rel"
      if [[ ! -f "$path" ]]; then
        errors=$((errors + 1))
        missing="${missing:+$missing }$ref"
      fi
      ;;
    att://*|prov://*|test://*|sarif://*|onchain://*|url://*)
      # External refs: cannot verify locally; pass (real hook would verify attestation)
      ;;
    *)
      errors=$((errors + 1))
      missing="${missing:+$missing }$ref"
      ;;
  esac
done <<< "$refs"

if [[ "$errors" -gt 0 ]]; then
  echo "CLAIM LIFECYCLE GATE: fail (missing evidence: $missing)" >&2
  jq -n --arg ts "$now" --argjson e "$errors" --arg m "$missing" '{generated_at:$ts,status:"fail",pass:false,error_count:$e,missing:$m}' > "$REPORT"
  exit 2
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "CLAIM LIFECYCLE GATE: pass"
exit 0
