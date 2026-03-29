#!/usr/bin/env bash
# prdset-compile.sh — Compile PRD-set docs into items-index, items-generated, prdset-report.
# Usage: prdset-compile.sh <PROJECT_DIR>
# Output: PROJECT_DIR/contracts/{prdset-report.json,items-index.json,items-generated/*.json}
set -euo pipefail

PROJECT_DIR="${1:-.}"
[[ -d "$PROJECT_DIR" ]] || { echo "prdset-compile: no project dir $PROJECT_DIR" >&2; exit 1; }

JQ_CMD="$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo jq)"
CONTRACTS="$PROJECT_DIR/contracts"
ITEMS_GEN="$CONTRACTS/items-generated"
mkdir -p "$ITEMS_GEN"

SPEC_DOCS=(PRD.md ADR.md FUNCTIONAL_REQUIREMENTS.md PLAN.md USER_JOURNEYS.md RISK_REGISTER.md VERIFICATION_POLICY.md RELEASE_CONTRACT.md)
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Build docs array
docs_arr=""
for doc in "${SPEC_DOCS[@]}"; do
  path="$PROJECT_DIR/$doc"
  exists="false"
  [[ -f "$path" ]] && exists="true"
  esc_path="${path//\\/\\\\}"
  esc_path="${esc_path//\"/\\\"}"
  [[ -n "$docs_arr" ]] && docs_arr="$docs_arr,"
  docs_arr="${docs_arr}{\"doc\":\"$doc\",\"path\":\"$esc_path\",\"exists\":$exists}"
done

# Extract items from markdown: ### ID or ## ID patterns
idx_arr=""
for doc in "${SPEC_DOCS[@]}"; do
  path="$PROJECT_DIR/$doc"
  [[ -f "$path" ]] || continue
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if [[ "$line" =~ ^[#]+\ +([A-Za-z0-9]+-[0-9]+|[A-Za-z0-9_-]{3,}) ]]; then
      id="${BASH_REMATCH[1]}"
      [[ "$id" =~ ^(Overview|Introduction|Summary|References|Appendix|Glossary|Table|Contents)$ ]] && continue
      gen_file="$ITEMS_GEN/${id}.json"
      printf '{"id":"%s","source":"%s","open_questions":[],"decisions":[]}\n' "$id" "$path" > "$gen_file" 2>/dev/null || true
      esc_path="${path//\\/\\\\}"
      esc_path="${esc_path//\"/\\\"}"
      [[ -n "$idx_arr" ]] && idx_arr="$idx_arr,"
      idx_arr="${idx_arr}{\"id\":\"$id\",\"source\":\"$esc_path\"}"
    fi
  done < <(grep -E '^#{1,6}\s+[A-Za-z0-9]' "$path" 2>/dev/null || true)
done

# Write prdset-report.json
printf '{"generated_at":"%s","project_dir":"%s","docs":[%s],"item_count":0,"items":[]}\n' \
  "$now" "$PROJECT_DIR" "$docs_arr" > "$CONTRACTS/prdset-report.json"

# Write items-index.json
printf '[%s]\n' "${idx_arr:-}" > "$CONTRACTS/items-index.json"

exit 0
