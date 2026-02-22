#!/bin/bash
# Installation script for runtime-dispatch
# Creates symlinks for all supported tools in ~/.local/bin/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BINARY="$SCRIPT_DIR/target/release/runtime-dispatch"
BIN_DIR="$HOME/.local/bin"

# Ensure binary exists
if [ ! -f "$BINARY" ]; then
    echo "Error: Binary not found at $BINARY"
    echo "Please run: cd $SCRIPT_DIR && ./build.sh"
    exit 1
fi

# Ensure bin directory exists
mkdir -p "$BIN_DIR"

# List of tools to create symlinks for
TOOLS=(
    "git"
    "grep"
    "find"
    "ls"
    "du"
    "cat"
    "node"
    "npm"
    "npx"
    "python"
    "pip"
)

echo "Installing runtime-dispatch symlinks to $BIN_DIR..."

for tool in "${TOOLS[@]}"; do
    link_path="$BIN_DIR/$tool"

    # Backup existing binary if it's not already our symlink
    if [ -L "$link_path" ]; then
        current_target=$(readlink "$link_path")
        if [ "$current_target" = "$BINARY" ]; then
            echo "  ✓ $tool already linked"
            continue
        fi
    fi

    if [ -f "$link_path" ] && [ ! -L "$link_path" ]; then
        echo "  ⚠ Backing up existing $tool to ${link_path}.backup"
        mv "$link_path" "${link_path}.backup"
    fi

    echo "  → Linking $tool -> runtime-dispatch"
    ln -sf "$BINARY" "$link_path"
done

echo ""
echo "Installation complete!"
echo ""
echo "To test:"
echo "  $BIN_DIR/git --version"
echo ""
echo "To bypass shim temporarily:"
echo "  export BYPASS_ULTRA_SHIM=1"
echo ""
echo "To uninstall:"
echo "  for tool in ${TOOLS[*]}; do rm -f $BIN_DIR/\$tool; done"
