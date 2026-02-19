#!/bin/bash
# Test script for mise installation integration

set -e

echo "=========================================="
echo "Testing mise Installation Integration"
echo "=========================================="
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_check() {
    local name="$1"
    local command="$2"
    echo -n "Testing $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test 1: Check if thegent commands have system-deps flag
echo "1. Testing command flags..."
test_check "thegent install --help contains --system-deps" \
    "thegent install --help | grep -q 'system-deps'"
test_check "thegent setup --help contains --system-deps" \
    "thegent setup --help | grep -q 'system-deps'"
test_check "thegent install --help contains --nix" \
    "thegent install --help | grep -q '--nix'"

# Test 2: Dry run test
echo
echo "2. Testing dry-run mode..."
test_check "Dry run doesn't fail" \
    "thegent install --system-deps --dry-run > /dev/null 2>&1"

# Test 3: Check if mise functions exist in install.py
echo
echo "3. Testing code implementation..."
test_check "install_mise function exists" \
    "grep -q 'def install_mise' src/thegent/install.py"
test_check "verify_mise_installation function exists" \
    "grep -q 'def verify_mise_installation' src/thegent/install.py"
test_check "install_system_dependencies function exists" \
    "grep -q 'def install_system_dependencies' src/thegent/install.py"

# Test 4: Check if .mise.toml exists
echo
echo "4. Testing configuration files..."
test_check ".mise.toml exists" \
    "test -f .mise.toml"
test_check ".envrc exists and optimized" \
    "test -f .envrc && grep -q 'MISE_ENV' .envrc"

# Test 5: Check shell templates
echo
echo "5. Testing shell templates..."
test_check "shell/.zshenv exists" \
    "test -f shell/.zshenv"
test_check "shell/.zshenv contains mise hook" \
    "grep -q 'mise activate' shell/.zshenv"

# Summary
echo
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
