#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Always run the configured pre-commit stage checks first.
./scripts/run_pre_commit_stage.sh pre-commit

# Optional local GH Actions parity lane (dockerless) for pre-commit.
if [[ "${THGENT_HOOK_RUN_GHA_PRE_COMMIT:-1}" == "1" ]]; then
  THGENT_ACT_DOCKERLESS=1 task ci:local-gha:pre-commit
fi
