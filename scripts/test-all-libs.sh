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

has_ts_tests() {
  local path="$1"
  find "$path" -type f ! -path '*/node_modules/*' ! -path '*/dist/*' | grep -Eq '\.(test|spec)\.(ts|tsx|js|jsx)$'
}

has_python_tests() {
  local path="$1"
  find "$path" -type f ! -path '*/.venv/*' ! -path '*/build/*' ! -path '*/dist/*' ! -path '*/.pytest_cache/*' | grep -Eq '(^|/)test_.*\.py$|(^|/).*_test\.py$|/tests/.*\.py$'
}

test_rust_libs() {
  local run_all_targets="${CI_SKIP_DOCTESTS:-0}"

  for name in "${RUST_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"
    local manifest="$path/Cargo.toml"

    if [[ ! -f "$manifest" ]]; then
      echo "Skipping ${name}: missing $manifest"
      continue
    fi

    if [[ "$run_all_targets" == "1" ]]; then
      run_step "Test Rust lib ${name} (all targets)" run_in_dir "$path" cargo test --all-targets
    else
      run_step "Test Rust lib ${name}" run_in_dir "$path" cargo test --lib
    fi
  done
}

test_go_libs() {
  for name in "${GO_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/go.mod" ]]; then
      echo "Skipping ${name}: missing go.mod"
      continue
    fi

    run_step "Test Go lib ${name}" run_in_dir "$path" go test ./...
  done
}

test_ts_libs() {
  for name in "${TS_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/package.json" ]]; then
      echo "Skipping ${name}: missing package.json"
      continue
    fi

    run_step "Install TS lib ${name}" run_in_dir "$path" npm_install
    if has_ts_tests "$path"; then
      run_step "Test TS lib ${name}" run_in_dir "$path" npm run test --if-present
    else
      echo "Skipping TS tests for ${name}: no test files found"
    fi
  done
}

test_python_libs() {
  for name in "${PY_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ ! -f "$path/pyproject.toml" ]]; then
      echo "Skipping ${name}: missing pyproject.toml"
      continue
    fi

    run_step "Install Python lib ${name}" run_in_dir "$path" python -m pip install --disable-pip-version-check -e .
    if has_python_tests "$path"; then
      run_step "Test Python lib ${name}" run_in_dir "$path" pytest -q
    else
      echo "Skipping Python tests for ${name}: no test files found"
    fi
  done
}

test_zig_libs() {
  for name in "${ZIG_LIBS[@]}"; do
    local path="$LIBS_DIR/$name"

    if [[ -f "$path/build.zig" ]]; then
      run_step "Test Zig lib ${name}" run_in_dir "$path" zig build test
    elif [[ -f "$path/src/lib.zig" ]]; then
      run_step "Test Zig lib ${name}" run_in_dir "$path" zig test src/lib.zig
    else
      echo "Skipping ${name}: missing build.zig and src/lib.zig"
    fi
  done
}

main() {
  echo "Testing all production libraries under $LIBS_DIR"
  test_rust_libs
  test_go_libs
  test_ts_libs
  test_python_libs
  test_zig_libs
}

main "$@"
