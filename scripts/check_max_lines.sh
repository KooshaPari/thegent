#!/usr/bin/env sh
# @trace WL-122
# Canonical max-lines gate: reads contracts/max_lines.json, scans source files with wc -l.
# Exits 1 if any file exceeds max_lines_per_file.
set -eu

{
  CDPATH=
  ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
}
CONTRACT="$ROOT_DIR/contracts/max_lines.json"

if [ ! -f "$CONTRACT" ]; then
  echo "MAX_LINES_GATE FAIL: missing contract $CONTRACT" >&2
  exit 1
fi

MAX=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['max_lines_per_file'])" "$CONTRACT")
EXCLUDES=$(python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
print('\n'.join(d.get('exclude', [])))
" "$CONTRACT")

violations=0

is_excluded() {
  _path="$1"
  echo "$EXCLUDES" | while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue
    # Strip leading path separator for relative matching
    rel="${_path#"$ROOT_DIR"/}"
    case "$rel" in
      "$pattern") echo "yes"; return 0 ;;
    esac
  done
}

while IFS= read -r file; do
  # Skip non-regular files
  [ -f "$file" ] || continue

  # Check exclusions
  excluded=$(is_excluded "$file")
  [ "$excluded" = "yes" ] && continue

  lines=$(wc -l < "$file" 2>/dev/null || echo 0)
  if [ "$lines" -gt "$MAX" ]; then
    echo "MAX_LINES_GATE FAIL: $file has $lines lines (limit $MAX)" >&2
    violations=$((violations + 1))
  fi
done << EOF
$(find "$ROOT_DIR" -type f \( \
  -name "*.py" -o \
  -name "*.sh" -o \
  -name "*.ts" -o \
  -name "*.js" -o \
  -name "*.go" -o \
  -name "*.rs" -o \
  -name "*.zig" \
\) 2>/dev/null)
EOF

if [ "$violations" -gt 0 ]; then
  echo "MAX_LINES_GATE FAIL: $violations file(s) exceed $MAX lines" >&2
  exit 1
fi

echo "MAX_LINES_GATE PASS: all files within $MAX lines"
