#!/usr/bin/env zsh
# post-agent-run-vetter.sh - PostAgentRun hook
# Runs governance vetting for an agent run. Blocking: non-zero rejects run.

set -euo pipefail

if [[ -z "${THGENT_RUN_ID:-}" ]]; then
  echo "POST-AGENT-RUN-VETTER FAIL: THGENT_RUN_ID is required" >&2
  exit 1
fi

POLICY="${THGENT_VETTER_POLICY:-default}"

thegent govern vet \
  "${THGENT_RUN_ID}" \
  --policy "${POLICY}"
