#!/usr/bin/env bash
# Monitor process count and detect fork failures
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Monitoring process count and fork failures...${NC}"
echo ""

# Current process count
PROC_COUNT=$(ps aux | wc -l | tr -d ' ')
echo -e "${BLUE}Current process count:${NC} $PROC_COUNT"

# System limits
MAX_PROCS=$(ulimit -u 2>/dev/null || echo "unknown")
echo -e "${BLUE}Max user processes:${NC} $MAX_PROCS"

# Check for fork failures
FORK_FAILURES=0
if command -v dmesg &>/dev/null; then
    FORK_FAILURES=$(dmesg 2>/dev/null | grep -c "fork: retry" || echo "0")
    if [[ $FORK_FAILURES -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Fork failures detected in system logs: $FORK_FAILURES${NC}"
    fi
fi

# Check thegent-related processes
THEGENT_PROCS=$(ps aux | grep -cE "[t]hegent|[c]ommon\.sh|[h]ook" || echo "0")
echo -e "${BLUE}thegent-related processes:${NC} $THEGENT_PROCS"

# Analysis and recommendations
echo ""
echo -e "${BLUE}📊 Analysis:${NC}"

if [[ $PROC_COUNT -gt 500 ]]; then
    echo -e "  ${RED}🔴 CRITICAL: Process count is very high ($PROC_COUNT)${NC}"
    echo "     Recommendation: Restart shell, apply fast-path fixes"
elif [[ $PROC_COUNT -gt 200 ]]; then
    echo -e "  ${YELLOW}🟡 WARNING: Process count is elevated ($PROC_COUNT)${NC}"
    echo "     Recommendation: Monitor and consider applying fixes"
else
    echo -e "  ${GREEN}✅ Process count is normal ($PROC_COUNT)${NC}"
fi

if [[ $THEGENT_PROCS -gt 50 ]]; then
    echo -e "  ${YELLOW}🟡 WARNING: Many thegent processes ($THEGENT_PROCS)${NC}"
    echo "     Recommendation: Check for process leaks"
fi

if [[ $FORK_FAILURES -gt 0 ]]; then
    echo -e "  ${RED}🔴 CRITICAL: Fork failures detected ($FORK_FAILURES)${NC}"
    echo "     Recommendation: Increase process limit, restart shell"
fi

echo ""
echo -e "${BLUE}💡 To fix:${NC}"
echo "   1. Run: bash thegent/scripts/fix-which-timeout.sh"
echo "   2. Restart your shell"
echo "   3. Monitor: watch -n 1 'ps aux | wc -l'"
echo ""
