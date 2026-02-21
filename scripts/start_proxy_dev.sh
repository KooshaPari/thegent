#!/usr/bin/env zsh
# Start CLIProxyAPIPlus for local dev. Uses plusplus binary when built, else PATH.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUSPLUS_BIN="$ROOT/../cliproxyapi-plusplus/cli-proxy-api-plus"
if [ -x "$PLUSPLUS_BIN" ]; then
  export THGENT_CLIPROXY_BINARY="$PLUSPLUS_BIN"
  # Ensure plusplus has config.yaml if missing
  PLUSPLUS_CONFIG="$ROOT/../cliproxyapi-plusplus/config.yaml"
  THEGENT_CONFIG="$ROOT/.config/thegent/cliproxy-config.yaml"
  if [ ! -f "$PLUSPLUS_CONFIG" ] && [ -f "$THEGENT_CONFIG" ]; then
    mkdir -p "$(dirname "$PLUSPLUS_CONFIG")"
    cp "$THEGENT_CONFIG" "$PLUSPLUS_CONFIG"
  fi
fi
exec python "$ROOT/scripts/start_proxy.py" "$@"
