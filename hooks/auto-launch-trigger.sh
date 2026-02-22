#!/bin/zsh
# hooks/auto-launch-trigger.sh
# Triggered by task-completed.sh when workstream item completes
# Triggers auto-launch system to check for next items

set -euo pipefail

SESSION_ID="${SESSION_ID:-}"
EXIT_CODE="${EXIT_CODE:-0}"
ITEM_ID="${WORKSTREAM_ITEM_ID:-}"

if [[ -z "$SESSION_ID" ]]; then
  exit 0
fi

# Emit event to auto-launch system
# Use Python to call AutoLaunchSystem.handle_completion
# Run in background to avoid blocking hook execution
python3 <<EOF &
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(os.getenv('PWD', os.getcwd()))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from thegent.planning.auto_launch import AutoLaunchSystem
    from thegent.config import ThegentSettings

    settings = ThegentSettings()
    system = AutoLaunchSystem(settings)
    system.handle_completion('$SESSION_ID', $EXIT_CODE)
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.error(f'Auto-launch trigger error: {e}', exc_info=True)
EOF

exit 0
