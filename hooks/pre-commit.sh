#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v git >/dev/null 2>&1; then
  echo "pre-commit.sh: git is required to locate repository root" >&2
  exit 1
fi
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

export THEGENT_HOOK_PROFILE="pre-commit"

if command -v uv >/dev/null 2>&1; then
  uv run pre-commit run
  exit 0
fi

if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit not found; install uv or pre-commit to run local commit checks." >&2
  exit 1
fi

pre-commit run
