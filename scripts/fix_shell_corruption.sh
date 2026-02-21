#!/usr/bin/env zsh
# Emergency fix for shell corruption where commands are being evaluated incorrectly.
# This script helps diagnose and fix shell hook issues.

set -euo pipefail

echo "=== Shell Corruption Diagnostic & Fix ==="
echo ""

# 1. Check for problematic hooks
echo "1. Checking for problematic shell hooks..."
if [ -f ~/.zshrc ]; then
    echo "   Found ~/.zshrc"
    if grep -q "eval.*ls\|eval.*\$(ls)\|eval.*\`ls\`" ~/.zshrc 2>/dev/null; then
        echo "   ⚠️  WARNING: Found problematic eval in ~/.zshrc"
    fi
fi

if [ -f ~/.zshenv ]; then
    echo "   Found ~/.zshenv"
    if grep -q "eval.*ls\|eval.*\$(ls)\|eval.*\`ls\`" ~/.zshenv 2>/dev/null; then
        echo "   ⚠️  WARNING: Found problematic eval in ~/.zshenv"
    fi
fi

# 2. Check for CLIProxyAPI wrapper issues
echo ""
echo "2. Checking CLIProxyAPI configuration..."
CLIPROXY_CONFIG="${HOME}/.config/thegent/cliproxy-config.yaml"
if [ ! -f "$CLIPROXY_CONFIG" ]; then
    echo "   ⚠️  Missing CLIProxyAPI config, creating..."
    mkdir -p "$(dirname "$CLIPROXY_CONFIG")"
    cat > "$CLIPROXY_CONFIG" <<EOF
port: 8317
auth-dir: ${HOME}/.config/thegent/cliproxy-auth
EOF
    echo "   ✓ Created config at $CLIPROXY_CONFIG"
fi

# 3. Check for cliproxy plusplus config issue
echo ""
echo "3. Checking cliproxyapi-plusplus config..."
PLUSPLUS_CONFIG="../cliproxyapi-plusplus/config.yaml"
if [ -f "../cliproxyapi-plusplus/cli-proxy-api-plus" ] && [ ! -f "$PLUSPLUS_CONFIG" ]; then
    echo "   ⚠️  plusplus binary exists but config missing, creating..."
    mkdir -p "$(dirname "$PLUSPLUS_CONFIG")"
    cp "$CLIPROXY_CONFIG" "$PLUSPLUS_CONFIG" 2>/dev/null || true
    echo "   ✓ Created plusplus config"
fi

# 4. Provide reset instructions
echo ""
echo "=== Fix Instructions ==="
echo ""
echo "If shell is corrupted, try these steps:"
echo ""
echo "1. Open a NEW terminal (don't use the corrupted one)"
echo ""
echo "2. Reset shell hooks:"
echo "   unset precmd_functions chpwd_functions PROMPT_COMMAND"
echo "   unset -f precmd chpwd"
echo ""
echo "3. Check for problematic aliases/functions:"
echo "   type ls"
echo "   type eval"
echo ""
echo "4. If using Codex/CLIProxyAPI, restart it:"
echo "   thegent mcp down"
echo "   thegent mcp up"
echo ""
echo "5. If issue persists, check for wrapper scripts:"
echo "   which cli-proxy-api-plus"
echo "   env | grep -i proxy"
echo ""
echo "=== Quick Fix ==="
echo ""
echo "To immediately fix CLIProxyAPI config issue:"
echo "  mkdir -p ~/.config/thegent"
echo "  python -m thegent.main mcp cliproxy ensure-config"
echo ""
echo "Done!"
