#!/usr/bin/env bash
# dx-audit.sh — Programmatic enforcement of thegent DX standards
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/src/thegent"
TESTS_DIR="$ROOT_DIR/tests"

# --- 1. Module Size Check ---
MAX_LINES=500
TARGET_LINES=350
VIOLATIONS=0

echo "=== Module Size Audit ==="
while IFS= read -r f; do
    LINES=$(wc -l < "$f" | tr -d ' ')
    if [[ "$LINES" -gt "$MAX_LINES" ]]; then
        echo "[FAIL] $f: $LINES lines (exceeds hard limit of $MAX_LINES)"
        VIOLATIONS=$((VIOLATIONS + 1))
    elif [[ "$LINES" -gt "$TARGET_LINES" ]]; then
        echo "[WARN] $f: $LINES lines (approaching target of $TARGET_LINES)"
    fi
done < <(find "$SRC_DIR" -name "*.py")

# --- 2. Test Naming Audit ---
echo ""
echo "=== Test Naming Audit ==="
while IFS= read -r f; do
    BASE=$(basename "$f")
    if [[ "$BASE" =~ (fast|unit|integration|e2e|v[0-9]|old|new)\.py$ ]]; then
        echo "[FAIL] $f: non-canonical name. Use concern-based naming instead."
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done < <(find "$TESTS_DIR" -name "test_*.py")

# --- 3. Summary ---
echo ""
if [[ "$VIOLATIONS" -gt 0 ]]; then
    echo "DX AUDIT FAIL: Found $VIOLATIONS violation(s)."
    exit 1
else
    echo "DX AUDIT PASS: Standards maintained."
    exit 0
fi
