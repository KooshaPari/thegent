#!/usr/bin/env bash
# hooks/post-commit-worklog.sh
# Write a WorklogEntry for every git commit.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DOCS_ROOT="${THEGENT_ROOT}/docs"
DB_PATH="${HOME}/.thegent/docs-engine/index.db"

SHA=$(git -C "${THEGENT_ROOT}" rev-parse HEAD 2>/dev/null || echo "unknown")
MSG=$(git -C "${THEGENT_ROOT}" log -1 --pretty=%s 2>/dev/null || echo "unknown")
FILES=$(git -C "${THEGENT_ROOT}" diff-tree --no-commit-id -r --name-only HEAD 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

uv run --project "${THEGENT_ROOT}" python -c "
from docs_engine.capture.commit_hook import write_worklog_entry
from pathlib import Path
files = [f for f in '${FILES}'.split(',') if f]
p = write_worklog_entry(
    docs_root=Path('${DOCS_ROOT}'),
    db_path=Path('${DB_PATH}'),
    commit_sha='${SHA}',
    commit_msg='${MSG}',
    files_changed=files,
)
print(f'docs-engine: worklog written → {p}')
"
