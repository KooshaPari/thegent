#!/bin/zsh
# qa-artifact-quality-gate.stub.sh
# Validates artifact freshness, non-placeholder in critical artifacts (assurance-case, rolling-wave, privacy-proof).
# Install via: make install-governance-hooks
set -euo pipefail

# Ensure jq/jaq is in PATH
export PATH="${HOME}/.local/bin:${PATH}"
JQ_CMD=$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo 'jq')

INPUT="$(cat)"
CWD="$($JQ_CMD -r '.cwd // empty' <<< "$INPUT" 2>/dev/null || echo "")"
PROJECT_DIR="${CWD:-$(pwd)}"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/artifact-quality-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

files=()
[[ -f "$PROJECT_DIR/contracts/assurance-case.json" ]] && files+=("$PROJECT_DIR/contracts/assurance-case.json")
[[ -f "$PROJECT_DIR/contracts/rolling-wave.json" ]] && files+=("$PROJECT_DIR/contracts/rolling-wave.json")
[[ -f "$VERIFY_DIR/privacy-proof.json" ]] && files+=("$VERIFY_DIR/privacy-proof.json")

if [[ "${#files[@]}" -eq 0 ]]; then
  $JQ_CMD -n --arg ts "$now" '{generated_at:$ts,status:"no_artifacts",pass:true,error_count:0}' > "$REPORT"
  echo "ARTIFACT QUALITY GATE: pass (no critical artifacts)"
  exit 0
fi

errors=0
bad_files=""
for path in "${files[@]}"; do
  [[ -f "$path" ]] || continue
  if rg -q -i 'placeholder|bootstrap|todo|tbd' "$path" 2>/dev/null; then
    echo "ARTIFACT QUALITY: placeholder in $path" >&2
    errors=$((errors + 1))
    bad_files="${bad_files:+$bad_files,}$(basename "$path")"
  fi
done

if [[ "$errors" -gt 0 ]]; then
  $JQ_CMD -n --arg ts "$now" --argjson e "$errors" --arg f "$bad_files" '{generated_at:$ts,status:"fail",pass:false,error_count:$e,bad_files:$f}' > "$REPORT"
  echo "ARTIFACT-QUALITY FAIL: $errors artifact(s) contain placeholder content" >&2
  exit 2
fi
$JQ_CMD -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "ARTIFACT QUALITY GATE: pass"
exit 0
