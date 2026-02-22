#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MAX_LINES=${MAX_LINES:-2500}
WARN_LINES=${WARN_LINES:-2000}
SCOPE=${MAX_LINES_SCOPE:-changed}
IMPL=${THEGENT_MAX_LINES_IMPL:-rust}
EXCLUDE_PREFIXES=${MAX_LINES_EXCLUDE_PREFIXES:-}

run_rust() {
  set -- --max-lines "$MAX_LINES" --warn-lines "$WARN_LINES" --scope "$SCOPE"
  if [ -n "$EXCLUDE_PREFIXES" ]; then
    set -- "$@" --exclude-prefixes "$EXCLUDE_PREFIXES"
  fi

  if command -v max_lines >/dev/null 2>&1; then
    exec max_lines "$@"
  fi
  if command -v cargo >/dev/null 2>&1; then
    exec cargo run --quiet --manifest-path "$ROOT_DIR/crates/thegent-utils/Cargo.toml" --bin max_lines -- \
      "$@"
  fi
  echo "MAX_LINES_GATE FAIL: Rust implementation unavailable (need max_lines or cargo)" >&2
  exit 2
}

run_zig() {
  if command -v zig >/dev/null 2>&1; then
    exec env MAX_LINES_SCOPE="$SCOPE" zig run "$ROOT_DIR/scripts/max_lines_gate.zig"
  fi
  echo "MAX_LINES_GATE FAIL: Zig implementation unavailable (need zig)" >&2
  exit 2
}

case "$IMPL" in
  rust) run_rust ;;
  zig) run_zig ;;
  *)
    echo "MAX_LINES_GATE FAIL: invalid THEGENT_MAX_LINES_IMPL='$IMPL' (use rust|zig)" >&2
    exit 2
    ;;
esac
