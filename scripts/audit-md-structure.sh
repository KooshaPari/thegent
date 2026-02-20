#!/usr/bin/env zsh
# Audit all MD docs for proper structure (frontmatter, H1, See also)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCS_DIR="$THEGENT_ROOT/docs"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📚 Auditing MD documentation structure...${NC}"
echo ""

MISSING_FRONTMATTER=()
MISSING_H1=()
MISSING_SEE_ALSO=()
TOTAL=0

while IFS= read -r -d '' file; do
    TOTAL=$((TOTAL + 1))
    filename=$(basename "$file")
    
    # Check for frontmatter or H1
    has_frontmatter=false
    has_h1=false
    has_see_also=false
    
    if head -5 "$file" | grep -qE "^---"; then
        has_frontmatter=true
    fi
    
    if head -10 "$file" | grep -qE "^# "; then
        has_h1=true
    fi
    
    if grep -qiE "^## .*See also|^## .*References|^## .*Related" "$file" 2>/dev/null; then
        has_see_also=true
    fi
    
    if [[ "$has_frontmatter" == "false" && "$has_h1" == "false" ]]; then
        MISSING_H1+=("$file")
    fi
    
    if [[ "$has_see_also" == "false" ]]; then
        MISSING_SEE_ALSO+=("$file")
    fi
    
done < <(find "$DOCS_DIR/research" -name "*.md" -type f -print0)

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Total MD files audited: $TOTAL${NC}"
echo ""

if [[ ${#MISSING_H1[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Missing frontmatter/H1 (${#MISSING_H1[@]} files):${NC}"
    for file in "${MISSING_H1[@]}"; do
        echo "   - ${file#$DOCS_DIR/}"
    done
    echo ""
else
    echo -e "${GREEN}✅ All files have frontmatter or H1${NC}"
    echo ""
fi

if [[ ${#MISSING_SEE_ALSO[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Missing 'See also' section (${#MISSING_SEE_ALSO[@]} files):${NC}"
    for file in "${MISSING_SEE_ALSO[@]}"; do
        echo "   - ${file#$DOCS_DIR/}"
    done
    echo ""
else
    echo -e "${GREEN}✅ All files have 'See also' section${NC}"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. Add frontmatter/H1 to files missing it"
echo "  2. Add 'See also' sections to files missing them"
echo "  3. Standardize heading levels"
