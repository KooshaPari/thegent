#!/usr/bin/env bash
# Expand fragmented research docs using thegent flash agents
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$THEGENT_ROOT/docs"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📚 Expanding fragmented research docs...${NC}"
echo ""

# Check for thegent flash agents
if command -v dex &>/dev/null; then
    FLASH_CMD="dex flash"
elif command -v thegent &>/dev/null && thegent clode --help &>/dev/null; then
    FLASH_CMD="thegent clode flash"
else
    echo -e "${YELLOW}⚠️  Flash agents not found. Install dex or thegent clode${NC}"
    echo "   Continuing with manual expansion..."
    FLASH_CMD=""
fi

# Fragment files to expand (P0 completed, P1 pending)
FRAGMENTS=(
    "research/scratchpad/session_review.md:P1"
    "research/GOVERNANCE_WP_GAPS.md:P1"
    "research/COST_ROUTING_DEFERRED.md:P1"
)

# Index files to update (P2)
INDEXES=(
    "research/SWARM_RESEARCH_INDEX.md"
    "research/CROSS_PLATFORM_RESEARCH_INDEX.md"
    "plans/00-MASTER-INDEX.md"
)

echo -e "${BLUE}📋 Fragment Expansion${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for fragment_info in "${FRAGMENTS[@]}"; do
    IFS=':' read -r fragment priority <<< "$fragment_info"
    fragment_path="$DOCS_DIR/$fragment"
    
    if [[ ! -f "$fragment_path" ]]; then
        echo -e "${YELLOW}⚠️  Skipping $fragment (not found)${NC}"
        continue
    fi
    
    echo -e "${BLUE}📄 Expanding: $fragment${NC}"
    
    if [[ -n "$FLASH_CMD" ]]; then
        echo "   Using flash agent: $FLASH_CMD"
        # Use flash agent to expand
        # Note: Actual implementation depends on flash agent API
        echo -e "${YELLOW}   ⚠️  Flash agent expansion pending (manual expansion recommended)${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Manual expansion required${NC}"
    fi
    
    echo ""
done

echo -e "${BLUE}📋 Index Updates${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for index in "${INDEXES[@]}"; do
    index_path="$DOCS_DIR/$index"
    
    if [[ ! -f "$index_path" ]]; then
        echo -e "${YELLOW}⚠️  Skipping $index (not found)${NC}"
        continue
    fi
    
    echo -e "${BLUE}📑 Updating: $index${NC}"
    echo "   Add sprawl-status column and links"
    echo ""
done

echo -e "${GREEN}✅ Fragment expansion script ready${NC}"
echo ""
echo "Next steps:"
echo "  1. Review expanded fragments"
echo "  2. Update indexes with sprawl status"
echo "  3. Run incorporator: thegent plan incorporate"
echo "  4. Add BACKLOG items to WORK_STREAM.md"
