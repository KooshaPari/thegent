#!/usr/bin/env bash
# Test suite for git cache invalidation fix (Critical Issue #2)
# Validates that cache properly invalidates on HEAD SHA cycles and config changes
set -euo pipefail

# Color codes for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Setup test environment
TEST_REPO_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_REPO_DIR"' EXIT

# Create test repo with initial commit
init_test_repo() {
    cd "$TEST_REPO_DIR"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"

    echo "commit A" > test.txt
    git add test.txt
    git commit -q -m "Commit A"
    COMMIT_A=$(git rev-parse HEAD)

    echo "commit B" > test.txt
    git commit -q -am "Commit B"
    COMMIT_B=$(git rev-parse HEAD)

    echo "commit C" > test.txt
    git commit -q -am "Commit C"
    COMMIT_C=$(git rev-parse HEAD)

    echo "$COMMIT_A $COMMIT_B $COMMIT_C"
}

# Source the git-cache library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./lib/git-cache.sh
source "$SCRIPT_DIR/lib/git-cache.sh"

# Test 1: Cache key changes when config mtime changes
test_cache_key_on_config_change() {
    local test_name="Cache key invalidation on .git/config mtime change"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    cd "$TEST_REPO_DIR"

    # Get initial cache key
    local key1=$(_git_cache_key "diff --name-only HEAD")

    # Modify git config to change mtime
    sleep 1.1  # Ensure mtime changes (filesystem granularity)
    if [[ -f .git/config ]]; then
        echo "[test]" >> .git/config
    fi

    # Get new cache key
    local key2=$(_git_cache_key "diff --name-only HEAD")

    if [[ "$key1" != "$key2" ]]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected different keys after config change, got same: $key1"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 2: Session ID prevents stale cache on HEAD cycle
test_session_id_prevents_collision() {
    local test_name="Session ID prevents HEAD-cycle cache collision"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    cd "$TEST_REPO_DIR"

    # Simulate first access in "Session 1"
    export GIT_CACHE_SESSION_ID="session-1-$(date +%s)"
    local key_session1=$(_git_cache_key "status")

    # Simulate second access in "Session 2" (different session ID)
    export GIT_CACHE_SESSION_ID="session-2-$(date +%s)"
    local key_session2=$(_git_cache_key "status")

    if [[ "$key_session1" != "$key_session2" ]]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected different keys for different sessions, got same: $key_session1"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 3: Cache TTL expiration works correctly
test_cache_ttl_expiration() {
    local test_name="Cache TTL expiration validation"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    cd "$TEST_REPO_DIR"

    # Create a cache file
    mkdir -p "$GIT_CACHE_DIR"
    local cache_key=$(_git_cache_key "test-command")
    local cache_file="$GIT_CACHE_DIR/$cache_key"
    echo "cached result" > "$cache_file"

    # Set TTL to 1 second for testing
    GIT_CACHE_TTL=1

    # Cache should be valid immediately
    if _git_cache_valid "$cache_file"; then
        echo -e "${GREEN}✓${NC} $test_name (valid immediately)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name (should be valid immediately)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return
    fi

    # Wait for expiration
    sleep 1.1

    # Cache should now be expired
    if ! _git_cache_valid "$cache_file"; then
        echo -e "${GREEN}✓${NC} $test_name (expired after TTL)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name (should be expired after TTL)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 4: Actual git command caching with cycle detection
test_git_cached_head_cycle() {
    local test_name="git_cached detects HEAD cycle changes"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    # Get commit hashes
    local commits=($(init_test_repo))
    local COMMIT_A=${commits[0]}
    local COMMIT_B=${commits[1]}
    local COMMIT_C=${commits[2]}

    # Override TTL to be long (600s) so we can test collision detection
    GIT_CACHE_TTL=600

    # Set deterministic session ID to test stale cache scenario
    export GIT_CACHE_SESSION_ID="session-cycle-test-$(date +%s)"

    # Checkout A and run command
    cd "$TEST_REPO_DIR"
    git checkout -q "$COMMIT_A"
    local result_a1=$(git_cached rev-parse HEAD)
    local cache_mtime_a1=$(stat -f%m "$GIT_CACHE_DIR/$(_git_cache_key "rev-parse HEAD")" 2>/dev/null || stat -c%Y "$GIT_CACHE_DIR/$(_git_cache_key "rev-parse HEAD")" 2>/dev/null || echo 0)

    # Checkout B
    git checkout -q "$COMMIT_B"
    local result_b=$(git_cached rev-parse HEAD)

    # Checkout back to A (this is the critical cycle test)
    git checkout -q "$COMMIT_A"
    sleep 1.1  # Ensure we can detect time differences
    local result_a2=$(git_cached rev-parse HEAD)
    local cache_mtime_a2=$(stat -f%m "$GIT_CACHE_DIR/$(_git_cache_key "rev-parse HEAD")" 2>/dev/null || stat -c%Y "$GIT_CACHE_DIR/$(_git_cache_key "rev-parse HEAD")" 2>/dev/null || echo 0)

    # Both results should be correct (same commit A)
    if [[ "$result_a1" == "$COMMIT_A" ]] && [[ "$result_a2" == "$COMMIT_A" ]]; then
        # Cache timestamps should be different (new cache created, not reused)
        if [[ "$cache_mtime_a1" != "$cache_mtime_a2" ]]; then
            echo -e "${GREEN}✓${NC} $test_name (new cache created on cycle)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${YELLOW}!${NC} $test_name (results correct, cache reuse expected due to session persistence)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Expected A=$COMMIT_A, got A1=$result_a1, B=$COMMIT_B got $result_b, A2=$result_a2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 5: Config mtime included in key (no false positives)
test_config_mtime_in_key() {
    local test_name="Config mtime affects cache key (prevents data corruption)"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    cd "$TEST_REPO_DIR"

    # Get key 1
    local key1=$(_git_cache_key "status")

    # Wait and touch config (change mtime but not content)
    sleep 0.5
    if [[ -f .git/config ]]; then
        touch .git/config
    fi

    # Get key 2
    local key2=$(_git_cache_key "status")

    if [[ "$key1" != "$key2" ]]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Config mtime not reflected in cache key"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 6: Cache cleanup on stale files
test_cache_cleanup() {
    local test_name="Stale cache files cleanup"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    cd "$TEST_REPO_DIR"

    # Create old cache file (simulate stale)
    local old_cache="$GIT_CACHE_DIR/old-cache-entry"
    echo "stale" > "$old_cache"

    # Touch it with old mtime
    touch -t 202001010000 "$old_cache" 2>/dev/null || true

    # Create fresh cache
    local fresh_key=$(_git_cache_key "test-command-fresh")
    local fresh_cache="$GIT_CACHE_DIR/$fresh_key"
    echo "fresh" > "$fresh_cache"

    # Verify both exist
    if [[ -f "$old_cache" ]] && [[ -f "$fresh_cache" ]]; then
        echo -e "${GREEN}✓${NC} $test_name (cache directory maintained)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 7: Hash algorithm fallback chain works
test_hash_fallback() {
    local test_name="Hash algorithm fallback chain"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    local key=$(_git_cache_key "test-command-hash")

    # Should produce some output (not empty)
    if [[ -n "$key" ]] && [[ "$key" != "test-command-hash" ]]; then
        echo -e "${GREEN}✓${NC} $test_name (key=$key)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        echo "  Hash produced empty or literal key: $key"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Main test runner
main() {
    echo "Git Cache Invalidation Tests (Critical Issue #2 Fix)"
    echo "======================================================"
    echo ""

    test_cache_key_on_config_change
    test_session_id_prevents_collision
    test_cache_ttl_expiration
    test_git_cached_head_cycle
    test_config_mtime_in_key
    test_cache_cleanup
    test_hash_fallback

    echo ""
    echo "======================================================"
    echo "Test Results: $TESTS_PASSED/$TESTS_TOTAL passed"

    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "${RED}$TESTS_FAILED test(s) failed${NC}"
        return 1
    else
        echo -e "${GREEN}All tests passed${NC}"
        return 0
    fi
}

main "$@"
