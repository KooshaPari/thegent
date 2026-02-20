#!/usr/bin/env zsh
# test-pyramid-validator.sh — Validates pytest distribution against pyramid targets
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_DIR="$ROOT_DIR/tests"

# Pyramid targets (from CLAUDE.md / qa-config.json)
TARGET_UNIT=70
TARGET_INT=20
TARGET_E2E=10
TOLERANCE=5

echo "=== Test Pyramid Audit ==="

# Count tests using markers
UNIT_COUNT=$(uv run pytest --collect-only -m unit "$TESTS_DIR" 2>/dev/null | grep -c "test_") || UNIT_COUNT=0
INT_COUNT=$(uv run pytest --collect-only -m integration "$TESTS_DIR" 2>/dev/null | grep -c "test_") || INT_COUNT=0
E2E_COUNT=$(uv run pytest --collect-only -m e2e "$TESTS_DIR" 2>/dev/null | grep -c "test_") || E2E_COUNT=0

TOTAL=$((UNIT_COUNT + INT_COUNT + E2E_COUNT))

if [[ "$TOTAL" -eq 0 ]]; then
    echo "[WARN] No tests found with unit/integration/e2e markers."
    exit 0
fi

PCT_UNIT=$((UNIT_COUNT * 100 / TOTAL))
PCT_INT=$((INT_COUNT * 100 / TOTAL))
PCT_E2E=$((E2E_COUNT * 100 / TOTAL))

PASS=true

check_band() {
    local name="$1" actual="$2" target="$3"
    local low=$((target - TOLERANCE))
    local high=$((target + TOLERANCE))
    if [[ "$actual" -lt "$low" ]] || [[ "$actual" -gt "$high" ]]; then
        echo "  [FAIL] $name: $actual% (target: $target% +/-$TOLERANCE%)"
        PASS=false
    else
        echo "  [PASS] $name: $actual% (target: $target% +/-$TOLERANCE%)"
    fi
}

echo "Total Marker-Counted Tests: $TOTAL"
check_band "Unit" "$PCT_UNIT" "$TARGET_UNIT"
check_band "Integration" "$PCT_INT" "$TARGET_INT"
check_band "E2E" "$PCT_E2E" "$TARGET_E2E"

if [[ "$PASS" == "true" ]]; then
    echo "RESULT: PASS"
    exit 0
else
    echo "RESULT: FAIL (Pyramid out of balance)"
    exit 1
fi
