#!/usr/bin/env bash
# qa-dag-dependency-gate.sh
# WBS-A1: Enforce PLAN.md dependency transitions — no task marked done if predecessors incomplete.
# Reads dag.json edges (depends_on) and ledger.json item states; fails on violation.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"
DAG="$PROJECT_DIR/contracts/dag.json"
LEDGER="$PROJECT_DIR/contracts/ledger.json"
VERIFY_DIR="$PROJECT_DIR/.claude/verification"
REPORT="$VERIFY_DIR/dag-dependency-gate.json"
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$VERIFY_DIR"

if [[ ! -f "$DAG" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"no_dag",pass:true,error_count:0}' > "$REPORT"
  echo "DAG DEPENDENCY GATE: no_dag (skip)"
  exit 0
fi

if [[ ! -f "$LEDGER" ]]; then
  jq -n --arg ts "$now" '{generated_at:$ts,status:"no_ledger",pass:true,error_count:0}' > "$REPORT"
  echo "DAG DEPENDENCY GATE: no_ledger (skip)"
  exit 0
fi

# Build map: item_id -> state from ledger
declare -A state
while IFS= read -r line; do
  id="$(jq -r '.id // empty' <<< "$line" 2>/dev/null)"
  s="$(jq -r '.state // empty' <<< "$line" 2>/dev/null)"
  [[ -n "$id" ]] && state[$id]="$s"
done < <(jq -c '.items[]?' "$LEDGER" 2>/dev/null || true)

# Consider done: released, accepted, verified (depends on project convention)
done_states="released accepted verified done completed"

is_done() {
  local s="${1:-}"
  [[ -z "$s" ]] && return 1
  for d in $done_states; do
    [[ "$s" == "$d" ]] && return 0
  done
  return 1
}

# Extract depends_on edges from dag.json (type=depends_on: from=predecessor, to=successor)
violations=0
while IFS= read -r edge; do
  from="$(jq -r '.from // empty' <<< "$edge")"
  to="$(jq -r '.to // empty' <<< "$edge")"
  typ="$(jq -r '.type // empty' <<< "$edge")"
  [[ "$typ" != "depends_on" ]] && continue
  [[ -z "$from" || -z "$to" ]] && continue

  # Only check when both nodes exist in ledger
  [[ -z "${state[$to]+x}" ]] && continue
  [[ -z "${state[$from]+x}" ]] && continue
  to_state="${state[$to]}"
  from_state="${state[$from]}"
  if is_done "$to_state"; then
    if ! is_done "$from_state"; then
      echo "DAG violation: $to (state=$to_state) depends on $from (state=$from_state)" >&2
      violations=$((violations + 1))
    fi
  fi
done < <(jq -c '.edges[]? | select(.type=="depends_on")' "$DAG" 2>/dev/null || true)

if [[ "$violations" -gt 0 ]]; then
  jq -n --arg ts "$now" --argjson v "$violations" '{generated_at:$ts,status:"fail",pass:false,error_count:$v}' > "$REPORT"
  echo "DAG-DEPENDENCY FAIL: $violations DAG violation(s) found" >&2
  exit 2
fi

jq -n --arg ts "$now" '{generated_at:$ts,status:"pass",pass:true,error_count:0}' > "$REPORT"
echo "DAG DEPENDENCY GATE: pass"
exit 0
