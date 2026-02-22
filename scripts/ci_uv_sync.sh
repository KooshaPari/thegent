#!/usr/bin/env bash

set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "ci_uv_sync.sh FAIL: uv not found in PATH"
  exit 1
fi

SYNC_ARGS=("sync" "--all-extras" "--dev")

os="$(uname -s)"
arch="$(uname -m)"

if [ "$os" != "Darwin" ] || [ "$arch" != "arm64" ]; then
  SYNC_ARGS+=("--no-install-package" "extism")
  SYNC_ARGS+=("--no-install-package" "extism-sys")
fi

uv "${SYNC_ARGS[@]}"
