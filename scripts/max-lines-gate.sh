#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MAX_LINES=${MAX_LINES:-500}
WARN_LINES=${WARN_LINES:-350}
IMPL=${THEGENT_MAX_LINES_IMPL:-auto}
SCOPE=${MAX_LINES_SCOPE:-changed}

run_rust_bin() {
  "$@" --max-lines "$MAX_LINES" --warn-lines "$WARN_LINES" --scope "$SCOPE"
}

run_auto() {
  if command -v cargo >/dev/null 2>&1; then
    cargo run --quiet --manifest-path "$ROOT_DIR/crates/thegent-utils/Cargo.toml" --bin thegent-max-lines -- \
      --max-lines "$MAX_LINES" --warn-lines "$WARN_LINES"
    return $?
  fi
  if command -v thegent-max-lines >/dev/null 2>&1; then
    run_rust_bin thegent-max-lines
    return $?
  fi
  if command -v zig >/dev/null 2>&1; then
    MAX_LINES_SCOPE="$SCOPE" zig run "$ROOT_DIR/scripts/max_lines_gate.zig"
    return $?
  fi
  return 127
}

case "$IMPL" in
  rust)
    if command -v thegent-max-lines >/dev/null 2>&1; then
      run_rust_bin thegent-max-lines
    elif command -v cargo >/dev/null 2>&1; then
      cargo run --quiet --manifest-path "$ROOT_DIR/crates/thegent-utils/Cargo.toml" --bin thegent-max-lines -- \
        --max-lines "$MAX_LINES" --warn-lines "$WARN_LINES"
    else
      echo "MAX_LINES_GATE FAIL: Rust implementation requested but unavailable" >&2
      exit 2
    fi
    ;;
  zig)
    if command -v zig >/dev/null 2>&1; then
      MAX_LINES_SCOPE="$SCOPE" zig run "$ROOT_DIR/scripts/max_lines_gate.zig"
    else
      echo "MAX_LINES_GATE FAIL: Zig implementation requested but unavailable" >&2
      exit 2
    fi
    ;;
  auto)
    if ! run_auto; then
      echo "MAX_LINES_GATE FAIL: no implementation available (rust binary, zig, or cargo)" >&2
      exit 2
    fi
    ;;
  *)
    echo "MAX_LINES_GATE FAIL: invalid THEGENT_MAX_LINES_IMPL='$IMPL' (use auto|rust|zig)" >&2
    exit 2
    ;;
esac

exit 0
