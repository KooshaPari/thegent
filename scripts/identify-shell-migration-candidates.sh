#!/usr/bin/env zsh
# Identify shell scripts that should be migrated to Rust/Go for performance
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔍 Identifying shell scripts for Rust/Go migration..."
echo ""

# Criteria for migration:
# 1. Frequently called (hooks, dispatchers)
# 2. Performance-critical (PATH resolution, process scanning)
# 3. Complex logic that would benefit from compiled performance
# 4. Cross-platform compatibility needs

echo "📊 High-priority candidates (frequently called, performance-critical):"
echo ""

# Find frequently called scripts
find "$THEGENT_ROOT/hooks" -name "*.sh" -type f | while read -r script; do
    # Count how many times it's sourced/called
    refs=$(grep -r "$(basename "$script")" "$THEGENT_ROOT" --include="*.sh" --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
    
    # Check if it's a dispatcher or common library
    if [[ "$script" == *"dispatcher"* ]] || [[ "$script" == *"common.sh"* ]] || [[ "$script" == *"lib/"* ]]; then
        echo "  🔴 CRITICAL: $script (referenced $refs times)"
    elif [[ $refs -gt 5 ]]; then
        echo "  🟡 HIGH: $script (referenced $refs times)"
    fi
done

echo ""
echo "📋 Scripts with expensive operations (should be Rust/Go):"
echo ""

# Find scripts with expensive operations
grep -r "find\|ps\|grep.*-r\|while.*read\|for.*in.*\$(find" "$THEGENT_ROOT/hooks" --include="*.sh" 2>/dev/null | \
    grep -v "^Binary" | \
    cut -d: -f1 | \
    sort -u | \
    while read -r script; do
        echo "  ⚡ $script (contains expensive operations)"
    done

echo ""
echo "🎯 Recommended migration priority:"
echo ""
echo "1. hooks/lib/common.sh - PATH resolution, tool detection (called by ALL hooks)"
echo "2. hooks/lib/fd-wrapper.sh - File discovery wrapper (frequently called)"
echo "3. hooks/lib/git-cache.sh - Git caching (performance-critical)"
echo "4. hooks/*-dispatcher.sh - Hook dispatchers (called on every tool use)"
echo "5. hooks/lib/git-wrapper.sh - Git mutex/lock handling (critical path)"
echo ""
echo "💡 Migration benefits:"
echo "  - Rust: 10-100x faster for process/file operations"
echo "  - Go: Good balance of performance and simplicity"
echo "  - Both: Better cross-platform support than bash"
