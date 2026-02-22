#!/usr/bin/env bash
# Quality gate — runs on pre-commit.
# Fail fast: any non-zero exit blocks the commit.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Ruff lint + format check
if command -v uv &>/dev/null; then
    uv run ruff check src/docs_engine/ || exit 1
    uv run ruff format --check src/docs_engine/ || exit 1
    uv run pyright src/docs_engine/ || exit 1
fi

echo "quality-gate: passed"
