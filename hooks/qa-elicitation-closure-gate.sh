#!/bin/zsh
# qa-elicitation-closure-gate.sh
# Blocks progressed states when elicitation is unresolved.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
LEDGER="$PROJECT_DIR/contracts/ledger.json"
FAIL_CLOSED="${QA_ELICITATION_FAIL_CLOSED:-true}"

[[ -f "$LEDGER" ]] || exit 0
command -v jq >/dev/null 2>&1 || exit 0

ADR_DOC="$PROJECT_DIR/ADR.md"
violations='[]'

# states that require elicitation closure
jq -c '.items[] | select((.state|ascii_downcase) as $s | ($s=="approved" or $s=="claimed" or $s=="evidence_submitted" or $s=="verified" or $s=="accepted" or $s=="released"))' "$LEDGER" |
while IFS= read -r item; do
  id="$(jq -r '.id' <<< "$item")"
  src="$(jq -r '.source' <<< "$item")"

  # only check markdown-backed items where open_questions/decisions are available
  if [[ "$src" == *.md ]] && [[ -f "$src" ]]; then
    norm="$($HOME/.claude/contracts/normalize-item.sh "$src" 2>/dev/null || true)"
    [[ -z "$norm" ]] && continue

    oq_count="$(jq '.canonical.open_questions | length // 0' <<< "$norm")"
    if [[ "$oq_count" -gt 0 ]]; then
      violations="$(jq -c --arg id "$id" --arg issue "open_questions_not_empty" '. + [{id:$id,issue:$issue}]' <<< "$violations")"
    fi

    # decisions must reference ADR-* and exist in ADR.md
    while IFS= read -r adr; do
      [[ -z "$adr" ]] && continue
      if [[ ! "$adr" =~ ^ADR- ]]; then
        violations="$(jq -c --arg id "$id" --arg issue "decision_not_adr_ref" --arg ref "$adr" '. + [{id:$id,issue:$issue,ref:$ref}]' <<< "$violations")"
      elif [[ -f "$ADR_DOC" ]] && ! rg -q -N "$adr" "$ADR_DOC"; then
        violations="$(jq -c --arg id "$id" --arg issue "adr_ref_missing_in_adr_md" --arg ref "$adr" '. + [{id:$id,issue:$issue,ref:$ref}]' <<< "$violations")"
      fi
    done < <(jq -r '.canonical.decisions[]? // empty' <<< "$norm")
  fi
done

vcount="$(jq 'length' <<< "$violations")"
echo "ELICITATION GATE: violations=$vcount"
if [[ "$vcount" -gt 0 ]]; then
  jq -r '.[] | "- \(.id): \(.issue)\(if .ref then " (" + .ref + ")" else "" end)"' <<< "$violations"
fi

if [[ "$FAIL_CLOSED" == "true" && "$vcount" -gt 0 ]]; then
  echo "ELICITATION CLOSURE GATE FAIL: $vcount elicitation violation(s) found" >&2
  exit 2
fi

exit 0
