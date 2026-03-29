#!/usr/bin/env bash
# Rust-backed complexity ratchet wrapper.
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

if command -v thegent-hooks >/dev/null 2>&1; then
    BIN_PATH="$(command -v thegent-hooks)"
elif [[ -x "${PROJECT_ROOT}/hooks/bin/thegent-hooks" ]]; then
    BIN_PATH="${PROJECT_ROOT}/hooks/bin/thegent-hooks"
else
    echo "complexity-ratchet: thegent-hooks runtime not found; install/compile the Rust runtime first" >&2
    exit 1
fi

export PROJECT_DIR="$PROJECT_ROOT"
exec "$BIN_PATH" complexity-ratchet
