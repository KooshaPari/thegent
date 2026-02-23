#!/usr/bin/env bash
set -euo pipefail

TOOL="${1:?Usage: $0 <ty|basedpyright> <files...>}"
shift || true

py_files=()
for f in "$@"; do
  [[ -f "$f" ]] || continue
  [[ "$f" == *.py ]] || continue
  py_files+=("$f")
done

if [[ "${#py_files[@]}" -eq 0 ]]; then
  echo "No Python files selected for ${TOOL}; skipping."
  exit 0
fi

case "$TOOL" in
  ty)
    exec uv run ty check "${py_files[@]}"
    ;;
  basedpyright)
    exec uv run basedpyright "${py_files[@]}"
    ;;
  *)
    echo "Unknown typecheck tool: $TOOL" >&2
    exit 1
    ;;
esac
