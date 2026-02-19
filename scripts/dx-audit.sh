#!/usr/bin/env bash
# dx-audit.sh — Programmatic enforcement of thegent DX standards
# WP-DX1: Extended with complexity (radon) and import-boundary (tach) checks.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/src/thegent"
TESTS_DIR="$ROOT_DIR/tests"
MAX_CYCLOMATIC="${DX_AUDIT_MAX_CC:-15}"
COMPLEXITY_STRICT="${DX_AUDIT_COMPLEXITY_STRICT:-0}"
VIOLATIONS=0

# --- 1. Module Size Check ---
echo "=== Module Size Audit ==="
MAX_LINES=500
TARGET_LINES=350
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

# --- 2.1 AI Slop Audit ---
echo ""
echo "=== AI Slop Audit (TODO placeholders) ==="
while IFS= read -r f; do
    if grep -Ei "TODO: implement|TODO: add|TODO: fix the bug|as an AI" "$f" >/dev/null; then
        echo "[WARN] $f: Potential AI-generated placeholder or slop detected."
    fi
done < <(find "$SRC_DIR" -name "*.py")

# --- 3. Cyclomatic Complexity (optional: requires radon) ---
# Advisory by default (COMPLEXITY_STRICT=0). Set DX_AUDIT_COMPLEXITY_STRICT=1 to fail.
echo ""
echo "=== Cyclomatic Complexity (max $MAX_CYCLOMATIC) ==="
if command -v radon >/dev/null 2>&1; then
    _cc_out=$(radon cc "$SRC_DIR" -n "$MAX_CYCLOMATIC" -a 2>/dev/null || true)
    if [[ -n "$_cc_out" ]]; then
        _cc_count=$(echo "$_cc_out" | grep -cE "^\s+[FMC] [0-9]+:" 2>/dev/null || echo 0)
        if [[ "${_cc_count:-0}" -gt 0 ]]; then
            if [[ "${COMPLEXITY_STRICT}" == "1" ]]; then
                echo "[FAIL] $_cc_count functions/methods/classes exceed cyclomatic complexity $MAX_CYCLOMATIC:"
                echo "$_cc_out"
                VIOLATIONS=$((VIOLATIONS + _cc_count))
            else
                echo "[WARN] $_cc_count functions/methods/classes exceed cyclomatic complexity $MAX_CYCLOMATIC (advisory; set DX_AUDIT_COMPLEXITY_STRICT=1 to fail)"
                echo "$_cc_out" | head -50
                [[ "$_cc_count" -gt 50 ]] && echo "... and $((_cc_count - 50)) more"
            fi
        else
            echo "PASS: No functions exceed cyclomatic complexity $MAX_CYCLOMATIC"
        fi
    else
        echo "PASS: No functions exceed cyclomatic complexity $MAX_CYCLOMATIC"
    fi
else
    echo "SKIP: radon not installed (pip install radon). Complexity check disabled."
fi

# --- 4. Import Boundary / Architecture (optional: requires tach) ---
echo ""
echo "=== Import Boundary (tach) ==="
if command -v tach >/dev/null 2>&1; then
    cd "$ROOT_DIR" || exit 1
    if tach check 2>&1; then
        echo "PASS: Architecture boundaries enforced"
    else
        echo "[FAIL] tach check reported boundary violations"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
else
    echo "SKIP: tach not installed (pip install tach). Import-boundary check disabled."
fi

# --- 5. Summary ---
echo ""
if [[ "$VIOLATIONS" -gt 0 ]]; then
    echo "DX AUDIT FAIL: Found $VIOLATIONS violation(s)."
    exit 1
else
    echo "DX AUDIT PASS: Standards maintained."
    exit 0
fi
