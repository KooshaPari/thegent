#!/usr/bin/env bash
# Award XP to agents for successful task completions.
# Part of AgilePlus & Gardener Integration (Phase 5).

set -euo pipefail

# Parse arguments
AGENT=""
AMOUNT=0
REASON=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent)
      AGENT="$2"
      shift 2
      ;;
    --amount)
      AMOUNT="$2"
      shift 2
      ;;
    --reason)
      REASON="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "$AGENT" || $AMOUNT -eq 0 ]]; then
  echo "Usage: $0 --agent <agent> --amount <amount> [--reason <reason>]"
  exit 1
fi

# 1. Update the database (WorkstreamDB)
DB_PATH=".thegent/sessions/workstream.db"
if [[ ! -f "$DB_PATH" ]]; then
  DB_PATH="workstream.db"
fi

if [[ -f "$DB_PATH" ]]; then
  sqlite3 "$DB_PATH" <<EOF
INSERT INTO reputation (agent_id, trust_score, entries_count, last_updated, xp, level)
VALUES ('$AGENT', 1.0, 1, CURRENT_TIMESTAMP, $AMOUNT, 1)
ON CONFLICT(agent_id) DO UPDATE SET
  xp = xp + $AMOUNT,
  trust_score = trust_score + ($AMOUNT / 1000.0),
  entries_count = entries_count + 1,
  last_updated = CURRENT_TIMESTAMP,
  level = 1 + (xp + $AMOUNT) / 100;
EOF
fi

# 2. Log the event
echo "[XP] Awarded $AMOUNT XP to $AGENT ($REASON)" >> "logs/xp_awards.log"

# 3. Notify the dashboard (via event resource if needed)
# For now, just a simple log is enough.
