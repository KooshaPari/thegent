#!/usr/bin/env bash
# traceability-validator.sh — Validates FR traceability tags in code and tests
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FR_FILE="$ROOT_DIR/FUNCTIONAL_REQUIREMENTS.md"
SRC_DIR="$ROOT_DIR/src/thegent"
TESTS_DIR="$ROOT_DIR/tests"

echo "=== FR Traceability Audit ==="

if [ ! -f "$FR_FILE" ]; then
    echo "[ERROR] $FR_FILE not found."
    exit 1
fi

# Extract all FR IDs from the manifest
ALL_FRS=$(grep -oE "FR-[A-Z]+-[0-9]+" "$FR_FILE" | sort -u)
FR_COUNT=$(echo "$ALL_FRS" | wc -l | tr -d ' ')

# Track coverage
COVERED_FRS=""
ORPHAN_TESTS=0

echo "Scanning tests for FR tags..."
while IFS= read -r fr; do
    if grep -rq "$fr" "$TESTS_DIR"; then
        COVERED_FRS+="$fr "
    fi
done <<< "$ALL_FRS"

COVERED_COUNT=$(echo "$COVERED_FRS" | wc -w | tr -d ' ')
PCT=$((COVERED_COUNT * 100 / FR_COUNT))

echo "FR Coverage: $COVERED_COUNT/$FR_COUNT ($PCT%)"

# Check for orphan test files (no FR tag)
while IFS= read -r f; do
    if ! grep -qE "FR-[A-Z]+-[0-9]+" "$f"; then
        echo "  [WARN] Orphan test file: $f"
        ORPHAN_TESTS=$((ORPHAN_TESTS + 1))
    fi
done < <(find "$TESTS_DIR" -name "test_*.py")

if [ "$PCT" -lt 80 ]; then
    echo "RESULT: FAIL (Coverage below 80%)"
    exit 1
elif [ "$ORPHAN_TESTS" -gt 5 ]; then
    echo "RESULT: WARN (Too many orphan tests)"
    exit 0
else
    echo "RESULT: PASS"
    exit 0
fi
