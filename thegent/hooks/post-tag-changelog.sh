#!/usr/bin/env bash
# Post-tag hook: regenerate CHANGELOG.md via git-cliff and index it.
# @trace FR-DOCS-010
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DB_PATH="${DOCS_ENGINE_DB:-${REPO_ROOT}/docs/.docs-engine.db}"

uv run python -c "
from pathlib import Path
from docs_engine.git.cliff import CliffRunner
CliffRunner(repo_root=Path('${REPO_ROOT}'), db_path=Path('${DB_PATH}')).run()
"

echo "CHANGELOG.md regenerated and indexed."
