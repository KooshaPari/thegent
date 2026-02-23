#!/bin/bash
# Delegate 5 work items: Generate writeups with flash agents, implement with free agents

set -e

BASE_DIR="/Users/kooshapari/temp-PRODVERCEL/485/kush"
cd "$BASE_DIR"

echo "=== Agent Delegation: 5 Work Items ==="
echo ""

# Wait for writeups to be generated
echo "Phase 1: Waiting for research writeups..."
WAIT_COUNT=0
MAX_WAIT=60  # Wait up to 60 iterations (5 minutes if 5s intervals)

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    WRITEUP_COUNT=$(find docs/research -name "*_PLAN.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$WRITEUP_COUNT" -ge 5 ]; then
        echo "✓ All 5 writeups ready!"
        break
    fi
    echo "  Waiting... ($WRITEUP_COUNT/5 writeups found)"
    sleep 5
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ "$WRITEUP_COUNT" -lt 5 ]; then
    echo "⚠ Warning: Not all writeups ready. Proceeding with available ones..."
fi

echo ""
echo "Phase 2: Delegating implementations to free agents..."
echo ""

# Delegate implementations
declare -a TASKS=(
    "research-tui-compositor:TUI_COMPOSITOR_IMPLEMENTATION_PLAN.md"
    "research-cross-platform-isolation:CROSS_PLATFORM_ISOLATION_PLAN.md"
    "research-cross-platform-shell:CROSS_PLATFORM_SHELL_PLAN.md"
    "research-hook-rust-phase1:HOOK_RUST_PHASE1_PLAN.md"
    "research-library-http:HTTP_LIBRARY_MIGRATION_PLAN.md"
)

for TASK in "${TASKS[@]}"; do
    TASK_ID="${TASK%%:*}"
    PLAN_FILE="${TASK##*:}"
    PLAN_PATH="docs/research/$PLAN_FILE"
    
    if [ -f "$PLAN_PATH" ]; then
        echo "Delegating: $TASK_ID"
        thegent free "Implement $TASK_ID based on $PLAN_PATH. Follow the implementation plan step by step." --bg
        echo "  ✓ Launched in background"
    else
        echo "⚠ Skipping $TASK_ID: $PLAN_PATH not found"
    fi
    sleep 2  # Small delay between launches
done

echo ""
echo "=== Delegation Complete ==="
echo "All 5 implementations delegated to free agents"
echo "Monitor progress with: thegent mcp list"
echo "Check work stream: thegent plan progress"
