#!/usr/bin/env bash
# dag-compile.sh — Build dag.json from ledger and spec sources.
# Usage: dag-compile.sh <PROJECT_DIR>
# Depends: ledger-init.sh (ledger.json)
# Output: PROJECT_DIR/contracts/dag.json
set -euo pipefail

PROJECT_DIR="${1:-.}"
[[ -d "$PROJECT_DIR" ]] || { echo "dag-compile: no project dir $PROJECT_DIR" >&2; exit 1; }

JQ_CMD="$(command -v jaq 2>/dev/null || command -v jq 2>/dev/null || echo jq)"
CONTRACTS="$PROJECT_DIR/contracts"
LEDGER="$CONTRACTS/ledger.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Source paths (use jq for safe escaping)
sources="$($JQ_CMD -n \
  --arg proj "$PROJECT_DIR" \
  --arg contracts "$CONTRACTS" \
  '{
    plan: ($proj + "/PLAN.md"),
    item_index: ($contracts + "/items-index.json"),
    functional_requirements: ($proj + "/FUNCTIONAL_REQUIREMENTS.md"),
    prd: ($proj + "/PRD.md"),
    adr: ($proj + "/ADR.md"),
    user_journeys: ($proj + "/USER_JOURNEYS.md")
  }' 2>/dev/null || echo '{}')"

# Build nodes and edges from ledger items
nodes_json="[]"
edges_json="[]"
if [[ -f "$LEDGER" ]]; then
  nodes_json="$($JQ_CMD -c '[.items[]? | {id: .id, state: (.state // "draft")}]' "$LEDGER" 2>/dev/null || echo "[]")"
  # No depends_on edges by default; ledger may have dag.edges
  edges_json="$($JQ_CMD -c '.dag.edges // []' "$LEDGER" 2>/dev/null || echo "[]")"
fi

$JQ_CMD -n \
  --arg generated_at "$now" \
  --arg project_dir "$PROJECT_DIR" \
  --argjson sources "$sources" \
  --argjson nodes "$nodes_json" \
  --argjson edges "$edges_json" \
  '{
    generated_at: $generated_at,
    project_dir: $project_dir,
    sources: $sources,
    node_count: ($nodes | length),
    edge_count: ($edges | length),
    spec_edge_count: (($edges | map(select(.type == "depends_on"))) | length),
    nodes: $nodes,
    edges: $edges
  }' > "$CONTRACTS/dag.json" 2>/dev/null || {
  echo "{\"generated_at\":\"$now\",\"project_dir\":\"$PROJECT_DIR\",\"sources\":$sources,\"node_count\":0,\"edge_count\":0,\"spec_edge_count\":0,\"nodes\":[],\"edges\":[]}" > "$CONTRACTS/dag.json"
}

exit 0
