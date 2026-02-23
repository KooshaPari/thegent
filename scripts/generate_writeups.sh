#!/bin/bash
# Generate research writeups using thegent free (works without proxy)

set -e

BASE_DIR="/Users/kooshapari/temp-PRODVERCEL/485/kush"
cd "$BASE_DIR"

echo "=== Generating Research Writeups ==="
echo ""

declare -a TASKS=(
    "research-tui-compositor:TUI Compositor Implementation:docs/research/TUI_COMPOSITOR_IMPLEMENTATION_PLAN.md"
    "research-cross-platform-isolation:User isolation implementation (Hybrid model):docs/research/CROSS_PLATFORM_ISOLATION_PLAN.md"
    "research-cross-platform-shell:POSIX + PowerShell dual-shell strategy:docs/research/CROSS_PLATFORM_SHELL_PLAN.md"
    "research-hook-rust-phase1:Build thegent-hooks binary with core subcommands:docs/research/HOOK_RUST_PHASE1_PLAN.md"
    "research-library-http:Replace urllib with httpx (7 files):docs/research/HTTP_LIBRARY_MIGRATION_PLAN.md"
)

for TASK in "${TASKS[@]}"; do
    IFS=':' read -r TASK_ID TITLE OUTPUT_FILE <<< "$TASK"
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo "✓ $TASK_ID already exists: $OUTPUT_FILE"
        continue
    fi
    
    echo "Generating: $TASK_ID"
    PROMPT="Generate comprehensive research writeup for: $TASK_ID - $TITLE. Include: 1) Current state audit, 2) Architecture design, 3) Implementation plan with phases, 4) Integration points, 5) Testing strategy. Save to $OUTPUT_FILE"
    
    thegent free "$PROMPT" --bg > /dev/null 2>&1 || {
        echo "  ⚠ Failed, retrying..."
        sleep 2
        thegent free "$PROMPT" --bg > /dev/null 2>&1 || echo "  ✗ Failed after retry"
    }
    
    sleep 3  # Small delay between launches
done

echo ""
echo "=== Writeups Launched ==="
echo "Monitor progress: ls -lh docs/research/*_PLAN.md"
echo "Check sessions: thegent mcp list"
