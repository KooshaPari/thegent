#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Local pre-push defaults to skipping docs build unless explicitly enabled.
export THGENT_SKIP_DOCS_BUILD="${THGENT_SKIP_DOCS_BUILD:-1}"

# Always run the configured pre-push stage checks first.
./scripts/run_pre_commit_stage.sh pre-push

# Enforce strict governance policy checks as part of pre-push gate.
task quality:pre-push:strict-governance

# Local GH Actions parity lane for pre-push.
if [[ "${THGENT_HOOK_RUN_GHA_PRE_PUSH:-1}" == "1" ]]; then
  THGENT_ACT_DOCKERLESS=1 task ci:local-gha:pre-push
fi
