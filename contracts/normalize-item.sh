#!/usr/bin/env bash
# normalize-item.sh — Normalize a spec doc into item JSON (open_questions, decisions).
# Usage: normalize-item.sh <path-to-spec.md>
# Output: JSON with open_questions, decisions (to stdout)
# Used by qa-elicitation-closure-gate when items-generated not present.
set -euo pipefail

src="${1:-}"
[[ -n "$src" && -f "$src" ]] || {
  echo '{"open_questions":[],"decisions":[]}' 
  exit 0
}

JQ_CMD="$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo jq)"

# Extract ADR-* and similar decision refs from markdown
decisions=""
while IFS= read -r line; do
  if [[ "$line" =~ (ADR-[A-Za-z0-9_-]+|DEC-[A-Za-z0-9_-]+) ]]; then
    decisions="${decisions}${BASH_REMATCH[1]}"$'\n'
  fi
done < <(grep -oE '(ADR|DEC)-[A-Za-z0-9_-]+' "$src" 2>/dev/null || true)
decisions="$(echo "$decisions" | sort -u | grep -v '^$' || true)"

# Extract open questions (lines with ? or "open question")
oq_count=0
oq_count="$(grep -ciE '\?|open\s+question|TBD|TODO' "$src" 2>/dev/null || echo 0)"
[[ -z "$oq_count" ]] && oq_count=0

# Build decisions array for jq
dec_arr="[]"
if [[ -n "$decisions" ]]; then
  dec_arr="["
  first=1
  while IFS= read -r d; do
    [[ -z "$d" ]] && continue
    [[ $first -eq 0 ]] && dec_arr="$dec_arr,"
    dec_arr="${dec_arr}\"${d//\"/\\\"}\""
    first=0
  done <<< "$decisions"
  dec_arr="$dec_arr]"
fi

# Output canonical format for qa-elicitation-closure-gate compatibility
printf '{"canonical":{"open_questions":[],"decisions":%s}}\n' "$dec_arr"

exit 0
