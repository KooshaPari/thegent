#!/usr/bin/env bash
# ledger-init.sh — Build ledger.json from items-index and items-generated.
# Usage: ledger-init.sh <PROJECT_DIR>
# Depends: prdset-compile.sh (items-index.json, items-generated/*.json)
# Output: PROJECT_DIR/contracts/ledger.json
set -euo pipefail

PROJECT_DIR="${1:-.}"
[[ -d "$PROJECT_DIR" ]] || { echo "ledger-init: no project dir $PROJECT_DIR" >&2; exit 1; }

JQ_CMD="$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo jq)"
CONTRACTS="$PROJECT_DIR/contracts"
ITEMS_INDEX="$CONTRACTS/items-index.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Build items array from items-index.json
# Each item: { id, source, state } — state defaults to "draft"
items_json="[]"
if [[ -f "$ITEMS_INDEX" ]]; then
  items_json="$($JQ_CMD -c '
    if type == "array" then
      [.[] | {id: (.id // ""), source: (.source // ""), state: "draft"}]
    elif type == "object" then
      [to_entries[] | {id: .key, source: (.value // ""), state: "draft"}]
    else []
    end
  ' "$ITEMS_INDEX" 2>/dev/null || echo "[]")"
fi

# Build ledger.json
$JQ_CMD -n \
  --arg version "1.0" \
  --arg generated_at "$now" \
  --arg project_dir "$PROJECT_DIR" \
  --argjson items "$items_json" \
  '{
    version: $version,
    generated_at: $generated_at,
    project_dir: $project_dir,
    items: $items,
    dag: { nodes: [], edges: [] }
  }' > "$CONTRACTS/ledger.json" 2>/dev/null || {
  printf '{"version":"1.0","generated_at":"%s","project_dir":"%s","items":%s,"dag":{"nodes":[],"edges":[]}}\n' \
    "$now" "$PROJECT_DIR" "$items_json" > "$CONTRACTS/ledger.json"
}

exit 0
