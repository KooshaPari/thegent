#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGES_DIR="$ROOT_DIR/packages"
FORGE_DIR="$PACKAGES_DIR/phenotype-forge"
DEP_GUARD_DIR="$PACKAGES_DIR/phenotype-dep-guard"

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

build_tools() {
  echo "Building tool projects"

  run_step "Rust: phenotype-forge" run_in_dir "$FORGE_DIR" cargo build
  run_step "Python: phenotype-dep-guard" run_in_dir "$DEP_GUARD_DIR" bash -lc 'python -m pip install --disable-pip-version-check build >/dev/null && python -m build'
}

main() {
  build_tools
}

main "$@"
