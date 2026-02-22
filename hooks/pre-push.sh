#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v git >/dev/null 2>&1; then
  echo "pre-push.sh: git is required to locate repository root" >&2
  exit 1
fi
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

export THEGENT_HOOK_PROFILE="pre-push"
export THEGENT_CI_EVENT="${THEGENT_CI_EVENT:-push}"
export THEGENT_CI_EMULATION_MODE="${THEGENT_CI_EMULATION_MODE:-hook}"
export SKIP="${SKIP:-no-commit-to-branch}"

THEGENT_CI_EVENT="$THEGENT_CI_EVENT" \
THEGENT_CI_EMULATION_MODE="$THEGENT_CI_EMULATION_MODE" \
bash scripts/ci-local-emulator.sh
