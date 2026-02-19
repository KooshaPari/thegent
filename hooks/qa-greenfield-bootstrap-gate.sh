#!/bin/zsh
# qa-greenfield-bootstrap-gate.stub.sh (N7)
# Validates architecture boundary configs per stack (ruff, golangci, oxlint).
# Install via: make install-governance-hooks
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
QFILE="$PROJECT_DIR/.claude/quality.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/greenfield-bootstrap-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

[[ -f "$QFILE" ]] || { jq -n --arg ts "$now" '{generated_at:$ts,status:"no_quality_config",pass:true,error_count:0}' > "$REPORT"; echo "GREENFIELD BOOTSTRAP GATE: pass (no quality.json)"; exit 0; }
model="$(jq -r '.governance.delivery_model // "auto"' "$QFILE" 2>/dev/null || echo auto)"
stacks="$(jq -r '.stacks // ["python"] | .[]' "$QFILE" 2>/dev/null || echo python)"

if [[ "$model" != "greenfield" && "$model" != "hybrid" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"not_greenfield",pass:true,error_count:0}' > "$REPORT"
  echo "GREENFIELD BOOTSTRAP GATE: pass (not greenfield)"
  exit 0
fi

errors=0
missing=""
echo "$stacks" | grep -q python && { [[ -f "$PROJECT_DIR/ruff.toml" ]] || [[ -f "$PROJECT_DIR/pyproject.toml" ]] || { echo "GREENFIELD: missing python lint config (ruff.toml/pyproject.toml)" >&2; errors=$((errors+1)); missing="${missing:+$missing }ruff.toml/pyproject.toml"; }; }
echo "$stacks" | grep -q go && { [[ -f "$PROJECT_DIR/.golangci.yml" ]] || { echo "GREENFIELD: missing .golangci.yml" >&2; errors=$((errors+1)); missing="${missing:+$missing }.golangci.yml"; }; }
echo "$stacks" | grep -qE 'typescript|ts|js' && { [[ -f "$PROJECT_DIR/.oxlintrc.json" ]] || [[ -f "$PROJECT_DIR/eslint.config.js" ]] || [[ -f "$PROJECT_DIR/.eslintrc" ]] || { echo "GREENFIELD: missing ts/js lint config" >&2; errors=$((errors+1)); missing="${missing:+$missing }ts/js lint config"; }; }

if [[ "$errors" -gt 0 ]]; then
  jq -n --arg ts "$now" --argjson e "$errors" --arg m "$missing" '{generated_at:$ts,status:"fail",pass:false,error_count:$e,missing:$m}' > "$REPORT"
  echo "GREENFIELD-BOOTSTRAP FAIL: $errors missing bootstrap artifact(s)" >&2
  exit 2
fi
jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "GREENFIELD BOOTSTRAP GATE: pass"
exit 0
