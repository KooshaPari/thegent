#!/usr/bin/env zsh
# session-start-pending-notice.sh — SessionStart hook
# If pending-handoff.md exists with deferred prompts, echo a notice.
# Advisory only; must exit 0. Target <80ms.
set -euo pipefail

# Skip if system is resource-strapped (fork failures)
[[ "${THEGENT_HOOKS_MINIMAL:-0}" == "1" ]] && exit 0

_PD="${PROJECT_DIR:-.}"
STATE_DIR="${STATE_DIR:-$HOME/.claude}"
PROJ_HANDOFF="$_PD/docs/research/pending-handoff.md"
GLOBAL_HANDOFF="$STATE_DIR/pending-handoff.md"

N=0
HANDOFF=""
if [[ -f "$PROJ_HANDOFF" ]]; then
  N=$(grep -c -E '^[0-9]+\.\s' "$PROJ_HANDOFF" 2>/dev/null || echo 0)
  HANDOFF="docs/research/pending-handoff.md"
fi
if [[ $N -eq 0 && -f "$GLOBAL_HANDOFF" ]]; then
  N=$(grep -c -E '^[0-9]+\.\s' "$GLOBAL_HANDOFF" 2>/dev/null || echo 0)
  HANDOFF="${HOME}/.claude/pending-handoff.md"
fi

if [[ $N -gt 0 && -n "$HANDOFF" ]]; then
  echo "PENDING: $N deferred prompt(s) from last session. See $HANDOFF. Run thegent_do_next to surface them."
fi

exit 0
