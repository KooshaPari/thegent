#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Always run the configured pre-push stage checks first.
./scripts/run_pre_commit_stage.sh pre-push

# Local GH Actions parity lane for pre-push.
if [[ "${THGENT_HOOK_RUN_GHA_PRE_PUSH:-1}" == "1" ]]; then
  THGENT_ACT_DOCKERLESS=1 task ci:local-gha:pre-push
fi
