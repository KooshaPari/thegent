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

verify_rust_libs() {
  local count=0
  for name in "${RUST_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"
    local manifest="$path/Cargo.toml"

    [[ -f "$manifest" ]] || {
      echo "Skipping ${name}: missing $manifest"
      continue
    }

    count=$((count + 1))
    run_step "Cargo check ${name}" run_in_dir "$path" cargo check --manifest-path Cargo.toml
  done
  echo "Verified $count Rust crates"
}

verify_go_libs() {
  local count=0
  for name in "${GO_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    [[ -f "$path/go.mod" ]] || {
      echo "Skipping ${name}: missing go.mod"
      continue
    }

    count=$((count + 1))
    run_step "Go module check ${name}" run_in_dir "$path" go test ./...
  done
  echo "Checked $count Go projects"
}

verify_ts_libs() {
  local count=0
  for name in "${TS_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    [[ -f "$path/package.json" ]] || {
      echo "Skipping ${name}: missing package.json"
      continue
    }

    count=$((count + 1))
    run_step "TypeScript install ${name}" run_in_dir "$path" npm_install
    run_step "TypeScript build check ${name}" run_in_dir "$path" npm run build --if-present
  done
  echo "Checked $count TypeScript projects"
}

verify_python_libs() {
  local count=0
  for name in "${PY_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    [[ -f "$path/pyproject.toml" ]] || {
      echo "Skipping ${name}: missing pyproject.toml"
      continue
    }

    count=$((count + 1))
    run_step "Python editable install check for ${name}" run_in_dir "$path" bash -lc 'python -m pip install --disable-pip-version-check -e . >/dev/null'
  done
  echo "Checked $count Python projects"
}

verify_zig_libs() {
  local count=0
  for name in "${ZIG_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ -f "$path/build.zig" ]]; then
      count=$((count + 1))
      run_step "Zig build check ${name}" run_in_dir "$path" zig build
    elif [[ -f "$path/src/lib.zig" ]]; then
      count=$((count + 1))
      run_step "Zig test check ${name}" run_in_dir "$path" zig test src/lib.zig
    else
      echo "Skipping ${name}: missing build.zig and src/lib.zig"
    fi
  done
  echo "Checked $count Zig projects"
}

main() {
  echo "Verifying library manifests and buildability for libs under $LIBS_DIR"
  verify_rust_libs
  verify_go_libs
  verify_ts_libs
  verify_python_libs
  verify_zig_libs
}

main "$@"
