#!/bin/zsh
# qa-trace-parity-audit.sh
# Semantic parity audit against trace canonical strictness.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
OUT="$PROJECT_DIR/.claude/verification/trace-parity-report.json"
mkdir -p "$PROJECT_DIR/.claude/verification"

T_RUFF="/Users/kooshapari/.claude/templates/quality/ruff.toml"
T_GOLANGCI="/Users/kooshapari/.claude/templates/quality/golangci.yml"
T_OXLINT="/Users/kooshapari/.claude/templates/quality/oxlintrc.json"

checks='[]'

# Ruff semantic parity
ruff_required=("line-length = 120" '"E"' '"W"' '"F"' '"I"' '"B"' '"C4"' '"UP"' '"N"' '"PT"' '"SIM"' '"RUF"' '"PERF"' '"LOG"' '"S"' '"ASYNC"' '"RET"' '"PTH"' '"DTZ"' '"D"' '"FA"' '"Q"' '"C90"' '"PL"' '"FBT"' '"ANN"' '"TRY"' '"INT"' '"PGH"' '"ISC"' '"FURB"' '"G"' '"ARG"' '"T10"' '"T20"' '"ERA"' '"SLF"' '"INP"')
ruff_missing=()
if [[ -f "$T_RUFF" ]]; then
  for pat in "${ruff_required[@]}"; do
    rg -q -F "$pat" "$T_RUFF" || ruff_missing+=("$pat")
  done
  ruff_status="aligned"
  [[ ${#ruff_missing[@]} -gt 0 ]] && ruff_status="partial"
  checks="$(jq -c --arg status "$ruff_status" --argjson missing "$(printf '%s\n' "${ruff_missing[@]-}" | sed '/^$/d' | jq -R . | jq -s .)" '. + [{name:"ruff",status:$status,missing:$missing}]' <<< "$checks")"
else
  checks="$(jq -c '. + [{name:"ruff",status:"missing_template"}]' <<< "$checks")"
fi

# golangci semantic parity
golangci_required=("forbidigo" "varnamelen" "tagliatelle" "maintidx" "exhaustruct" "usestdlibvars" "predeclared" "sloglint" "testifylint" "exptostd" "godox" "asciicheck" "depguard")
golangci_missing=()
if [[ -f "$T_GOLANGCI" ]]; then
  for pat in "${golangci_required[@]}"; do
    rg -q -F "$pat" "$T_GOLANGCI" || golangci_missing+=("$pat")
  done
  golangci_status="aligned"
  [[ ${#golangci_missing[@]} -gt 0 ]] && golangci_status="partial"
  checks="$(jq -c --arg status "$golangci_status" --argjson missing "$(printf '%s\n' "${golangci_missing[@]-}" | sed '/^$/d' | jq -R . | jq -s .)" '. + [{name:"golangci",status:$status,missing:$missing}]' <<< "$checks")"
else
  checks="$(jq -c '. + [{name:"golangci",status:"missing_template"}]' <<< "$checks")"
fi

# oxlint semantic parity
oxlint_required=("typescript/no-explicit-any" "typescript/explicit-function-return-type" "max-params" "complexity" "max-lines" "import/no-default-export" "import/max-dependencies")
oxlint_missing=()
if [[ -f "$T_OXLINT" ]]; then
  for pat in "${oxlint_required[@]}"; do
    rg -q -F "$pat" "$T_OXLINT" || oxlint_missing+=("$pat")
  done
  boundaries_file="/Users/kooshapari/.claude/templates/quality/boundaries-config.json"
  [[ -f "$boundaries_file" ]] || oxlint_missing+=("boundaries-config.json")
  oxlint_status="aligned"
  [[ ${#oxlint_missing[@]} -gt 0 ]] && oxlint_status="partial"
  checks="$(jq -c --arg status "$oxlint_status" --argjson missing "$(printf '%s\n' "${oxlint_missing[@]-}" | sed '/^$/d' | jq -R . | jq -s .)" '. + [{name:"oxlint",status:$status,missing:$missing}]' <<< "$checks")"
else
  checks="$(jq -c '. + [{name:"oxlint",status:"missing_template"}]' <<< "$checks")"
fi

aligned_count="$(jq '[.[] | select(.status=="aligned")] | length' <<< "$checks")"
partial_count="$(jq '[.[] | select(.status=="partial")] | length' <<< "$checks")"

jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson checks "$checks" \
  --argjson aligned "$aligned_count" \
  --argjson partial "$partial_count" \
  '{generated_at:$ts,checks:$checks,aligned_count:$aligned,partial_count:$partial}' > "$OUT"

echo "TRACE PARITY AUDIT: $OUT"
jq -r '.checks[] | "- \(.name): \(.status)"' "$OUT"
exit 0
