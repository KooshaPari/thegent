#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIBS_DIR="$ROOT_DIR/libs"

RUST_LIBS=(
  "cipher"
  "tracing"
  "logger"
  "metrics"
  "nexus"
  "gauge"
  "hexagonal-rs"
  "xdd-lib-rs"
)
GO_LIBS=(
  "clikit"
  "hexagonal-go"
)
TS_LIBS=(
  "auth-ts"
  "config-ts"
  "hexagonal-ts"
)
PY_LIBS=(
  "evaluation"
  "hexagonal-py"
)
ZIG_LIBS=(
  "logging-zig"
)

run_step() {
  local label="$1"
  shift

  echo ""
  echo "▶ ${label}"
  "$@"
}

run_in_dir() {
  local path="$1"
  shift
  (
    cd "$path"
    "$@"
  )
}

npm_install() {
  if [[ -f package-lock.json ]]; then
    npm ci --no-audit --no-fund
  else
    npm install --no-audit --no-fund
  fi
}

build_rust_libs() {
  for name in "${RUST_LIBS[@]}"; do
    local manifest="$LIBS_DIR/${name}/Cargo.toml"

    if [[ ! -f "$manifest" ]]; then
      echo "Skipping ${name}: missing $manifest"
      continue
    fi

    run_step "Build Rust lib ${name}" cargo build --manifest-path "$manifest" --lib
  done
}

build_go_libs() {
  for name in "${GO_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/go.mod" ]]; then
      echo "Skipping ${name}: missing go.mod"
      continue
    fi

    run_step "Build Go lib ${name}" run_in_dir "$path" go build ./...
  done
}

build_ts_libs() {
  for name in "${TS_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/package.json" ]]; then
      echo "Skipping ${name}: missing package.json"
      continue
    fi

    run_step "Install TS lib ${name}" run_in_dir "$path" npm_install
    run_step "Build TS lib ${name}" run_in_dir "$path" npm run build --if-present
  done
}

build_python_libs() {
  for name in "${PY_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/pyproject.toml" ]]; then
      echo "Skipping ${name}: missing pyproject.toml"
      continue
    fi

    run_step "Build Python lib ${name}" run_in_dir "$path" bash -lc 'python -m pip install --disable-pip-version-check build >/dev/null && python -m build'
  done
}

build_zig_libs() {
  for name in "${ZIG_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ -f "$path/build.zig" ]]; then
      run_step "Build Zig lib ${name}" run_in_dir "$path" zig build
    elif [[ -f "$path/src/lib.zig" ]]; then
      run_step "Validate Zig lib ${name}" run_in_dir "$path" zig test src/lib.zig
    else
      echo "Skipping ${name}: missing build.zig and src/lib.zig"
    fi
  done
}

main() {
  echo "Building all production libraries under $LIBS_DIR"
  build_rust_libs
  build_go_libs
  build_ts_libs
  build_python_libs
  build_zig_libs
}

main "$@"
