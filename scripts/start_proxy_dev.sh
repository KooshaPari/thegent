#!/usr/bin/env bash
# Start CLIProxyAPIPlus for local dev. Uses fork binary when built, else PATH.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FORK_BIN="$ROOT/../CLIProxyAPIPlus-fork/cli-proxy-api-plus"
if [ -x "$FORK_BIN" ]; then
  export THGENT_CLIPROXY_BINARY="$FORK_BIN"
  # Ensure fork has config.yaml if it exists
  FORK_CONFIG="$ROOT/../CLIProxyAPIPlus-fork/config.yaml"
  THEGENT_CONFIG="$ROOT/.config/thegent/cliproxy-config.yaml"
  if [ ! -f "$FORK_CONFIG" ] && [ -f "$THEGENT_CONFIG" ]; then
    mkdir -p "$(dirname "$FORK_CONFIG")"
    cp "$THEGENT_CONFIG" "$FORK_CONFIG"
  fi
fi
exec python "$ROOT/scripts/start_proxy.py" "$@"
