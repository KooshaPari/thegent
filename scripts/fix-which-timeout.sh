#!/usr/bin/env bash
# Fix which timeout by adding fast-path wrappers
# This prevents shell initialization cascades during PATH resolution
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEGENT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Fixing which timeout issue...${NC}"
echo ""

# Create fast-path wrapper for which
WRAPPER_FILE="$THEGENT_ROOT/hooks/lib/which-wrapper.sh"
mkdir -p "$(dirname "$WRAPPER_FILE")"

cat > "$WRAPPER_FILE" << 'WRAPPER_EOF'
#!/usr/bin/env bash
# Fast-path wrapper for which command
# Prevents shell initialization cascades during PATH resolution

which() {
    # Set flag to skip wrapper functions during PATH resolution
    export _RESOLVING_PATH=1
    
    # Use system which directly
    command which "$@"
    local exit_code=$?
    
    # Unset flag
    unset _RESOLVING_PATH
    
    return $exit_code
}

# Export for subprocesses
export -f which
WRAPPER_EOF

chmod +x "$WRAPPER_FILE"
echo -e "${GREEN}✅ Created which-wrapper.sh${NC}"

# Update common.sh to respect _RESOLVING_PATH flag
COMMON_SH="$THEGENT_ROOT/hooks/lib/common.sh"
if grep -q "_RESOLVING_PATH" "$COMMON_SH" 2>/dev/null; then
    echo -e "${GREEN}✅ common.sh already has fast-path support${NC}"
else
    echo -e "${YELLOW}⚠️  Note: hooks/lib/common.sh may need fast-path support${NC}"
fi

# Add to shell config
SHELL_CONFIG=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [[ -n "$SHELL_CONFIG" ]]; then
    if ! grep -q "which-wrapper.sh" "$SHELL_CONFIG" 2>/dev/null; then
        echo ""
        echo -e "${BLUE}📝 Adding fast-path to $SHELL_CONFIG${NC}"
        {
            echo ""
            echo "# thegent: Fast-path for which command (prevents timeout)"
            echo "if [[ -f \"\$HOME/.local/share/thegent/hooks/lib/which-wrapper.sh\" ]]; then"
            echo "    source \"\$HOME/.local/share/thegent/hooks/lib/which-wrapper.sh\""
            echo "elif [[ -f \"./thegent/hooks/lib/which-wrapper.sh\" ]]; then"
            echo "    source \"./thegent/hooks/lib/which-wrapper.sh\""
            echo "fi"
        } >> "$SHELL_CONFIG"
        echo -e "${GREEN}✅ Added to $SHELL_CONFIG${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Run: source $SHELL_CONFIG${NC}"
    else
        echo -e "${GREEN}✅ Already configured in $SHELL_CONFIG${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not find .zshrc or .bashrc${NC}"
fi

echo ""
echo -e "${GREEN}✅ which timeout fix applied!${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart your shell or run: source $SHELL_CONFIG"
echo "  2. Test: time which codex  (should be <10ms)"
echo ""
