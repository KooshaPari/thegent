#!/bin/bash
# Build script for thegent-runtime that bypasses shims
set -e

# Use absolute path to cargo to avoid shim interception
CARGO_BIN="/usr/local/bin/cargo"
if [ ! -f "$CARGO_BIN" ]; then
    CARGO_BIN=$(command -v cargo 2>/dev/null || echo "cargo")
fi

cd "$(dirname "$0")"
echo "Building runtime-dispatch..."
export BYPASS_ULTRA_SHIM=1
"$CARGO_BIN" build --release

echo "Build complete: target/release/runtime-dispatch"
