#!/bin/zsh
# Hook: Stop
# Purpose: Reconcile teammate delegation status on session completion.

HOOK_NAME="TEAMMATE-RECONCILE"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Exit code of the session
EXIT_CODE=$(echo "$INPUT" | jq -r '.exit_code // 0')

# Update TeammateManager if this session corresponds to a delegation
export EXIT_CODE
export SESSION_ID

python3 -c "
from thegent.governance.teammates import TeammateManager
from thegent.config import ThegentSettings
from pathlib import Path
import os

settings = ThegentSettings()
mgr = TeammateManager(settings.cache_dir / 'teammates.json')

session_id = os.environ.get('SESSION_ID')
exit_code_str = os.environ.get('EXIT_CODE', '0')
try:
    exit_code = int(exit_code_str)
except ValueError:
    exit_code = 0

if session_id and session_id.startswith('DEL-'):
    status = 'completed' if exit_code == 0 else 'failed'
    summary = 'Completed successfully' if exit_code == 0 else f'Failed with exit code {exit_code}'
    if mgr.update_status(session_id, status, summary=summary):
        print(f'TEAMMATE-RECONCILE: Updated delegation {session_id} to {status}')
"

exit 0
