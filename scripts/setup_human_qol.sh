#!/bin/bash
# setup_human_qol.sh - Configure human-centric shell enhancements

set -e

PROJECT_ROOT="/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent"
HOOKS_BIN="$PROJECT_ROOT/crates/target/release/thegent-hooks"

if [ ! -f "$HOOKS_BIN" ]; then
    echo "Error: thegent-hooks binary not found. Please build it first."
    exit 1
fi

# Generate mise config and aliases
eval "$($HOOKS_BIN mise-setup)"

echo "Human QOL enhancements configured."
echo "Aliases added: g, gs, gd, gl, tf, tr"
echo "Smart tool defaults (rg, fd, uv, cargo) enabled for humans."
