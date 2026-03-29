#!/usr/bin/env zsh

# thegent - Unified CLI Wrapper
# This script handles the uv/virtualenv environment and hardware-specific optimizations.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Detect Hardware Context
PLATFORM="$(uname -s)"
ARCH="$(uname -m)"

# Performance Tuning for M1/M2/M3
if [[ "$PLATFORM" == "Darwin" && "$ARCH" == "arm64" ]]; then
  export THEGENT_PLATFORM="mac-silicon"
  export THEGENT_PERF_MODE="maximal"
fi

# Performance Tuning for WSL2 / Ryzen
if [[ -n "$WSL_DISTRO_NAME" ]]; then
  export THEGENT_PLATFORM="wsl2"
  export THEGENT_PERF_MODE="maximal"
fi

# Entry point using uv run (fast-path)
if command -v uv &> /dev/null; then
  # Use the project environment where this script resides
  exec uv run --project "$PROJECT_ROOT" python -m thegent.cli.apps.main "$@"
else
  # Fallback to system python if uv is missing (not recommended)
  echo "[Warning] 'uv' not found. Falling back to system python. Performance may be degraded."
  exec python3 -m thegent.cli.apps.main "$@"
fi
