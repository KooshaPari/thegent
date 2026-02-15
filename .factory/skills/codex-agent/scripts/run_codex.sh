#!/bin/bash
# Codex Agent - Model: gpt-5.3-codex (STRICT)
# Simple wrapper with JSON output by default
MODEL="gpt-5.3-codex"

# Find codex-subagent script - check both locations
CODEX_SUBAGENT=""
if [[ -f ~/.claude/skills/codex-subagent/scripts/run_codex_subagent.sh ]]; then
  CODEX_SUBAGENT=~/.claude/skills/codex-subagent/scripts/run_codex_subagent.sh
elif [[ -f ~/.factory/skills/codex-subagent/scripts/run_codex_subagent.sh ]]; then
  CODEX_SUBAGENT=~/.factory/skills/codex-subagent/scripts/run_codex_subagent.sh
else
  echo "Error: codex-subagent script not found" >&2
  exit 1
fi

# Default to JSON output for proper stdout capture
# Add --json flag automatically unless user explicitly requests otherwise
HAS_JSON_FLAG=false
for arg in "$@"; do
  if [[ "$arg" == "--json" ]]; then
    HAS_JSON_FLAG=true
    break
  fi
done

# Execute with JSON output by default (unless already present)
if [[ "$HAS_JSON_FLAG" == false ]]; then
  exec "$CODEX_SUBAGENT" "$@" --model "$MODEL" --json
else
  exec "$CODEX_SUBAGENT" "$@" --model "$MODEL"
fi
