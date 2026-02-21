#!/usr/bin/env zsh
# EMERGENCY FIX: Run this from a CLEAN terminal to fix shell corruption
# This script fixes CLIProxyAPI config issues that cause shell corruption
#
# Usage: bash scripts/emergency_fix_shell.sh
# Or: chmod +x scripts/emergency_fix_shell.sh && ./scripts/emergency_fix_shell.sh

set -euo pipefail

echo "=== EMERGENCY SHELL CORRUPTION FIX ==="
echo ""
echo "This script will:"
echo "1. Fix CLIProxyAPI config issues"
echo "2. Stop corrupted processes"
echo "3. Reset shell environment"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 1. Ensure CLIProxyAPI config exists
echo "Step 1: Ensuring CLIProxyAPI config..."
python3 "$ROOT/scripts/fix_shell_corruption.py" || {
    echo "Failed to run Python fix script, trying manual fix..."
    
    # Manual config creation
    CONFIG_DIR="$HOME/.config/thegent"
    CONFIG_FILE="$CONFIG_DIR/cliproxy-config.yaml"
    AUTH_DIR="$CONFIG_DIR/cliproxy-auth"
    
    mkdir -p "$CONFIG_DIR" "$AUTH_DIR"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" <<EOF
port: 8317
auth-dir: $AUTH_DIR
EOF
        echo "Created config at $CONFIG_FILE"
    fi
    
    # Fix plusplus config if needed
    PLUSPLUS_BIN="$ROOT/../cliproxyapi-plusplus/cli-proxy-api-plus"
    PLUSPLUS_CONFIG="$ROOT/../cliproxyapi-plusplus/config.yaml"
    if [ -f "$PLUSPLUS_BIN" ] && [ ! -f "$PLUSPLUS_CONFIG" ]; then
        mkdir -p "$(dirname "$PLUSPLUS_CONFIG")"
        cp "$CONFIG_FILE" "$PLUSPLUS_CONFIG"
        echo "Created plusplus config at $PLUSPLUS_CONFIG"
    fi
}

echo ""

# 2. Stop all CLIProxyAPI/thegent processes
echo "Step 2: Stopping corrupted processes..."
pkill -f "cli-proxy-api-plus" 2>/dev/null || echo "  (No cli-proxy-api-plus processes)"
pkill -f "thegent.*mcp" 2>/dev/null || echo "  (No thegent mcp processes)"
pkill -f "process-compose" 2>/dev/null || echo "  (No process-compose processes)"
sleep 2
echo "  ✓ Processes stopped"

echo ""

# 3. Check for problematic shell configs
echo "Step 3: Checking shell configuration..."
PROBLEMS=0

for config in ~/.zshrc ~/.zshenv ~/.zprofile; do
    if [ -f "$config" ]; then
        if grep -q "eval.*ls\|eval.*\$(ls)\|eval.*\`ls\`" "$config" 2>/dev/null; then
            echo "  ⚠️  WARNING: Found problematic eval in $config"
            PROBLEMS=$((PROBLEMS + 1))
        fi
    fi
done

if [ $PROBLEMS -eq 0 ]; then
    echo "  ✓ No problematic patterns found"
fi

echo ""

# 4. Provide reset instructions
echo "=== FIX COMPLETE ==="
echo ""
echo "Next steps:"
echo ""
echo "1. In your CURRENT terminal (this one), test commands:"
echo "   echo 'test' > /tmp/test_clean.txt"
echo "   cat /tmp/test_clean.txt"
echo ""
echo "2. If commands work here, the corrupted terminal can be closed."
echo ""
echo "3. To restart services cleanly:"
echo "   cd $ROOT"
echo "   python3 -m thegent.main mcp up"
echo ""
echo "4. If shell corruption persists in Codex:"
echo "   python3 -m thegent.main mcp fix codex"
echo "   python3 -m thegent.main mcp migrate-unimount codex"
echo ""
echo "Done!"
