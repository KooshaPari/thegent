#!/usr/bin/env bash
# Rust-backed security pipeline wrapper.
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

if command -v thegent-hooks >/dev/null 2>&1; then
    BIN_PATH="$(command -v thegent-hooks)"
elif [[ -x "${PROJECT_ROOT}/hooks/bin/thegent-hooks" ]]; then
    BIN_PATH="${PROJECT_ROOT}/hooks/bin/thegent-hooks"
else
    echo "security-pipeline: thegent-hooks runtime not found; install/compile the Rust runtime first" >&2
    exit 1
fi

export PROJECT_DIR="$PROJECT_ROOT"
mkdir -p "$PROJECT_ROOT/artifacts/hooks"
export THEGENT_SECURITY_PIPELINE_RESULT_JSON="$PROJECT_ROOT/artifacts/hooks/security-pipeline-result.json"
exec "$BIN_PATH" security-pipeline
