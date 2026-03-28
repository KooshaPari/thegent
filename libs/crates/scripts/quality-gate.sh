#!/bin/bash
set -e

ACTION="${1:-verify}"

case "$ACTION" in
  verify)
    echo "Running quality checks..."
    cargo fmt -- --check
    cargo clippy --all-targets --all-features -- -D warnings
    cargo test --lib --bins
    ;;
  *)
    echo "Usage: $0 {verify}"
    exit 1
    ;;
esac
