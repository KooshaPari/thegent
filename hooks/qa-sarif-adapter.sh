#!/usr/bin/env bash
# qa-sarif-adapter.sh
# Ingests SARIF files and produces a deterministic summary JSON.
set -euo pipefail
HOOK_NAME="QA-SARIF-ADAPTER"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"

# This hook takes PROJECT_DIR as $1, not from stdin
PROJECT_DIR="${1:-$(pwd)}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
OUT_DIR="$PROJECT_DIR/.claude/verification"
OUT_FILE="$OUT_DIR/sarif-summary.json"

mkdir -p "$OUT_DIR"

if ! command -v jq >/dev/null 2>&1; then
  echo "SARIF ADAPTER: jq not available; skipping"
  exit 0
fi

mapfile -t SARIF_FILES < <(
  find "$PROJECT_DIR" -maxdepth 8 \
    -type d \( -name .git -o -name node_modules -o -name .venv -o -name venv -o -name dist -o -name build \) -prune -o \
    -type f \( -name '*.sarif' -o -name '*.sarif.json' \) -print | head -50
)

if [[ ${#SARIF_FILES[@]} -eq 0 ]]; then
  jq -n '{files:0,total_results:0,levels:{error:0,warning:0,note:0,none:0}}' > "$OUT_FILE"
  echo "SARIF ADAPTER: files=0 total_results=0 output=$OUT_FILE"
  exit 0
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

for f in "${SARIF_FILES[@]}"; do
  jq -c --arg f "$f" '
    {
      file: $f,
      total: ([.runs[]?.results[]?] | length),
      error: ([.runs[]?.results[]? | select((.level // "warning") == "error")] | length),
      warning: ([.runs[]?.results[]? | select((.level // "warning") == "warning")] | length),
      note: ([.runs[]?.results[]? | select((.level // "warning") == "note")] | length),
      none: ([.runs[]?.results[]? | select((.level // "warning") == "none")] | length)
    }
  ' "$f" 2>/dev/null || true
 done > "$TMP"

jq -s '
  {
    files: length,
    total_results: (map(.total) | add // 0),
    levels: {
      error: (map(.error) | add // 0),
      warning: (map(.warning) | add // 0),
      note: (map(.note) | add // 0),
      none: (map(.none) | add // 0)
    },
    by_file: .
  }
' "$TMP" > "$OUT_FILE"

FILES="$(jq '.files' "$OUT_FILE")"
TOTAL="$(jq '.total_results' "$OUT_FILE")"
ERRS="$(jq '.levels.error' "$OUT_FILE")"
WARNS="$(jq '.levels.warning' "$OUT_FILE")"

echo "SARIF ADAPTER: files=$FILES total_results=$TOTAL errors=$ERRS warnings=$WARNS output=$OUT_FILE"
exit 0
