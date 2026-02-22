#!/usr/bin/env zsh
# Normalize all MD docs - add frontmatter, cross-links, See also sections
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$THEGENT_ROOT/docs"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📚 Normalizing MD documentation...${NC}"
echo ""

# Check for expanded/consolidated docs that need "See also" sections
EXPANDED_DOCS=(
    "research/SESSION_RESEARCH_FRAGMENTS_EXPANDED.md"
    "research/CONVERSATION_DUMP_2026-02-16_EXPANDED.md"
    "research/CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md"
    "research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md"
    "research/LIBRARY_REPLACEMENT_CONSOLIDATED.md"
    "research/PHASE_DOCUMENTS_EXPANDED.md"
    "research/GOVERNANCE_WP_GAPS_EXPANDED.md"
    "research/COST_ROUTING_DEFERRED_EXPANDED.md"
)

echo -e "${BLUE}📋 Checking expanded/consolidated docs for 'See also' sections${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for doc in "${EXPANDED_DOCS[@]}"; do
    doc_path="$DOCS_DIR/$doc"

    if [[ ! -f "$doc_path" ]]; then
        echo -e "${YELLOW}⚠️  Skipping $doc (not found)${NC}"
        continue
    fi

    # Check if "See also" or "References" section exists
    if grep -qE "^## .*See also|^## .*References|^## .*Related" "$doc_path" 2>/dev/null; then
        echo -e "${GREEN}✅ $doc has See also/References section${NC}"
    else
        echo -e "${YELLOW}⚠️  $doc missing See also section${NC}"
        echo "   Add: ## See Also section with cross-links"
    fi
done

echo ""
echo -e "${BLUE}📋 Checking for frontmatter${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Sample check for frontmatter
SAMPLE_DOCS=(
    "research/SESSION_RESEARCH_FRAGMENTS.md"
    "research/CONVERSATION_DUMP_2026-02-16.md"
    "research/CROSS_PLATFORM_GAPS_AND_EXTENSIONS_RESEARCH.md"
)

for doc in "${SAMPLE_DOCS[@]}"; do
    doc_path="$DOCS_DIR/$doc"

    if [[ ! -f "$doc_path" ]]; then
        continue
    fi

    if head -5 "$doc_path" | grep -qE "^---|^# "; then
        echo -e "${GREEN}✅ $doc has proper structure${NC}"
    else
        echo -e "${YELLOW}⚠️  $doc may need frontmatter${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ MD normalization check complete${NC}"
echo ""
echo "Next steps:"
echo "  1. Review expanded docs for 'See also' sections"
echo "  2. Add frontmatter to docs missing it"
echo "  3. Ensure all docs cross-link to WORK_STREAM.md"
echo "  4. Standardize heading levels"
