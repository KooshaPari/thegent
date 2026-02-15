#!/usr/bin/env bash
# qa-evidence-recorder.sh (PostToolUse — optimized)
# Records gate outputs into .claude/evidence/ for audit trail.
# Runs after gates; aggregates pass/fail into evidence ledger.
# OPTIMIZED: Skip common.sh when dispatched. Only process files changed since last run.
set -euo pipefail

HOOK_NAME="EVIDENCE-RECORDER"

# Stderr message on unexpected failure (set -e)
trap 'echo "EVIDENCE-RECORDER FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # Env vars already set: PROJECT_DIR, VERIFY_DIR, etc.
  printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
else
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init  # sets PROJECT_DIR, VERIFY_DIR, $now, reads stdin
fi

# Fast path: no verification directory or no JSON files → nothing to record
[[ -d "${VERIFY_DIR:-}" ]] || exit 0
compgen -G "${VERIFY_DIR}/*.json" >/dev/null 2>&1 || { echo "EVIDENCE RECORDER: recorded 0 gate(s) to evidence/"; exit 0; }

EVIDENCE_DIR="${PROJECT_DIR:-.}/.claude/evidence"
mkdir -p "$EVIDENCE_DIR"

ledger="$EVIDENCE_DIR/evidence-ledger.jsonl"
summary="$EVIDENCE_DIR/latest-run.json"

# --- Incremental: only process files newer than last run ---
_LAST_RUN_MARKER="$EVIDENCE_DIR/.last-run-ts"
_NEW_FILES=()
if [[ -f "$_LAST_RUN_MARKER" ]]; then
  while IFS= read -r f; do
    [[ -f "$f" ]] && _NEW_FILES+=("$f")
  done < <(find "$VERIFY_DIR" -maxdepth 1 -name '*.json' -newer "$_LAST_RUN_MARKER" 2>/dev/null)
  # Nothing new since last run
  if [[ ${#_NEW_FILES[@]} -eq 0 ]]; then
    echo "EVIDENCE RECORDER: recorded 0 gate(s) (no new results)"
    exit 0
  fi
else
  # First run: process all
  _NEW_FILES=("$VERIFY_DIR"/*.json)
fi

# Update marker
touch "$_LAST_RUN_MARKER"

# Process with single jq call on only the new files
jq_output="$(jq -nc --arg now "$now" '
  [inputs | {
    gate: (.gate // (input_filename | split("/")[-1] | rtrimstr(".json"))),
    pass: (.pass // (.status == "pass") // false),
    recorded_at: (.generated_at // $now)
  }] |
  {recorded_at: $now, gates: ., pass_count: [.[] | select(.pass) | .gate] | length, total: length},
  .[]
' "${_NEW_FILES[@]}" 2>/dev/null)" || true

if [[ -n "$jq_output" ]]; then
  {
    IFS= read -r summary_line
    printf '%s\n' "$summary_line" > "$summary"
    count=0
    while IFS= read -r entry; do
      printf '%s\n' "$entry" >> "$ledger"
      count=$((count + 1))
    done
    echo "EVIDENCE RECORDER: recorded ${count} gate(s) to $EVIDENCE_DIR"
  } <<< "$jq_output"
else
  echo "EVIDENCE RECORDER: recorded 0 gate(s) to $EVIDENCE_DIR"
fi

exit 0
