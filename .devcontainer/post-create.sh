#!/usr/bin/env bash
# .devcontainer/post-create.sh — bootstrap a thegent devcontainer.
#
# Runs once after the container image is built and the workspace is mounted.
# Idempotent: re-running is safe; thegent stays at the pinned lockfile.
#
# @trace ONBOARD-L30: devcontainer bootstrap

set -euo pipefail

cd "$(dirname "$0")/.."

echo "[post-create] installing uv if missing"
if ! command -v uv >/dev/null 2>&1; then
    pip install --quiet uv
fi

echo "[post-create] syncing dependencies"
uv sync --all-extras

echo "[post-create] installing thegent in editable mode"
uv run pip install --quiet -e .

echo "[post-create] warming the CLI cache"
uv run python -m thegent --help >/dev/null || true

echo "[post-create] setup OK"
