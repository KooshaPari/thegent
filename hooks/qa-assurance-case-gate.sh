#!/usr/bin/env bash
# qa-assurance-case-gate.stub.sh (N12)
# Validates assurance-case.json against schema and structure. Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
AC="$PROJECT_DIR/contracts/assurance-case.json"
SCHEMA="$PROJECT_DIR/schemas/assurance-case.schema.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/assurance-case-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$AC" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_present",pass:true,error_count:0}' > "$REPORT"
  echo "ASSURANCE CASE GATE: pass (no assurance-case.json)"
  exit 0
fi

jq -e . "$AC" >/dev/null 2>&1 || { jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"invalid JSON"}' > "$REPORT"; echo "ASSURANCE-CASE FAIL: invalid JSON in assurance-case.json" >&2; exit 2; }
jq -e '.generated_at and .top_claims and .nodes' "$AC" >/dev/null 2>&1 || { jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"missing required fields (generated_at, top_claims, nodes)"}' > "$REPORT"; echo "ASSURANCE-CASE FAIL: missing required fields (generated_at, top_claims, nodes)" >&2; exit 2; }

# Schema validation - fail hard if schema validation fails
if [[ -f "$SCHEMA" ]] && [[ -f "$REPO_ROOT/scripts/validate-json-schema.sh" ]]; then
  if ! bash "$REPO_ROOT/scripts/validate-json-schema.sh" "$SCHEMA" "$AC" 2>/dev/null; then
    jq -n --arg ts "$now" '{generated_at:$ts,status:"fail",pass:false,error_count:1,error:"schema validation failed"}' > "$REPORT"
    echo "ASSURANCE CASE GATE: fail (schema validation)" >&2
    exit 2
  fi
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "ASSURANCE CASE GATE: pass"
exit 0
