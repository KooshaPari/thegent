#!/usr/bin/env bash
# session-start-research-inject.sh — Inject recent research context into agent session
# @trace FR-RES-060
# Fetches recent research items from the research store and displays them to the agent.
# Advisory only; must exit 0. Target <500ms.
set -euo pipefail

# Skip if research_engine not available or disabled
[[ "${THGENT_RESEARCH_INJECT_ON_SESSION_START:-0}" == "1" ]] || exit 0

PROJECT_DIR="${PROJECT_DIR:-.}"
RESEARCH_DB="$HOME/.thegent/research.db"

# If no research DB, exit gracefully
[[ -f "$RESEARCH_DB" ]] || exit 0

# Only run if Python + research_engine available
if ! python3 -c "import research_engine.session_hook" 2>/dev/null; then
    exit 0
fi

# Inject session context via research_engine
python3 << 'EOF'
import sys
from pathlib import Path

try:
    from research_engine.store import ResearchStore
    from research_engine.session_hook import inject_session_context

    db_path = Path.home() / ".thegent" / "research.db"
    if db_path.exists():
        store = ResearchStore(str(db_path))
        output = inject_session_context(store)
        if output:
            print(output)
except Exception as e:
    # Silent fail if research_engine not properly installed
    pass

sys.exit(0)
EOF

exit 0
