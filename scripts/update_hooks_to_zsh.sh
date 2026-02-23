#!/bin/zsh
# Update all hook scripts to use zsh instead of bash/sh

set -e

BASE_DIR="/Users/kooshapari/temp-PRODVERCEL/485/kush"
cd "$BASE_DIR"

echo "=== Updating Hook Scripts to zsh ==="
echo ""

# Find all shell scripts in hooks directory
HOOKS_DIR="thegent/hooks"
UPDATED=0
SKIPPED=0

find "$HOOKS_DIR" -name "*.sh" -type f | while read -r script; do
    # Check first line
    first_line=$(head -1 "$script")
    
    if [[ "$first_line" =~ ^#!/bin/(bash|sh)$ ]] || [[ "$first_line" =~ ^#!/usr/bin/(bash|sh)$ ]]; then
        echo "Updating: $script"
        # Replace shebang with zsh
        sed -i '' '1s|^#!/bin/bash$|#!/bin/zsh|' "$script"
        sed -i '' '1s|^#!/usr/bin/bash$|#!/bin/zsh|' "$script"
        sed -i '' '1s|^#!/bin/sh$|#!/bin/zsh|' "$script"
        sed -i '' '1s|^#!/usr/bin/sh$|#!/bin/zsh|' "$script"
        UPDATED=$((UPDATED + 1))
    elif [[ "$first_line" =~ ^#!/bin/zsh$ ]] || [[ "$first_line" =~ ^#!/usr/bin/zsh$ ]]; then
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "=== Update Complete ==="
echo "Updated: $UPDATED scripts"
echo "Already zsh: $SKIPPED scripts"
