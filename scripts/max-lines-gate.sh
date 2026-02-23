#!/usr/bin/env sh
set -eu

{
  CDPATH=
  ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
}
MAX_LINES=${MAX_LINES:-2500}
WARN_LINES=${WARN_LINES:-2000}
SCOPE=${MAX_LINES_SCOPE:-changed}
IMPL=${THEGENT_MAX_LINES_IMPL:-rust}
EXCLUDE_PREFIXES=${MAX_LINES_EXCLUDE_PREFIXES:-}

run_scoped_files() {
  checked=0
  warned=0
  failed=0
  for f in "$@"; do
    [ -f "$f" ] || continue
    lines=$(wc -l <"$f" | tr -d '[:space:]')
    checked=$((checked + 1))
    if [ "$lines" -gt "$MAX_LINES" ]; then
      echo "[FAIL] $f: $lines lines (max $MAX_LINES)" >&2
      failed=$((failed + 1))
    elif [ "$lines" -gt "$WARN_LINES" ]; then
      echo "[WARN] $f: $lines lines (>$WARN_LINES)" >&2
      warned=$((warned + 1))
    fi
  done
  echo "MAX_LINES_GATE summary: checked=$checked warn=$warned fail=$failed max=$MAX_LINES warn_at=$WARN_LINES"
  if [ "$failed" -gt 0 ]; then
    exit 1
  fi
  exit 0
}

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

if [ "$#" -gt 0 ]; then
  run_scoped_files "$@"
fi

case "$IMPL" in
  rust) run_rust ;;
  zig) run_zig ;;
  *)
    echo "MAX_LINES_GATE FAIL: invalid THEGENT_MAX_LINES_IMPL='$IMPL' (use rust|zig)" >&2
    exit 2
    ;;
esac
