#!/usr/bin/env bash
# Optimize runtime: Install Bun, optimize zsh, replace slow tools
set -euo pipefail

echo "=== Runtime Optimization ==="
echo ""

# 1. Install Bun (fastest JS runtime)
echo "1. Installing Bun..."
if ! command -v bun >/dev/null 2>&1; then
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
    echo "   ✓ Bun installed"
else
    echo "   ✓ Bun already installed: $(bun --version)"
fi

# 2. Check for problematic eval in shell configs
echo ""
echo "2. Checking shell configs for problematic eval..."
PROBLEMATIC_PATTERNS=(
    "eval.*ls"
    "eval.*find"
    "eval.*\$(ls)"
    "eval.*\`ls\`"
    "eval.*\$(find"
)

for config in ~/.zshrc ~/.zshenv ~/.zshrc.local; do
    if [[ -f "$config" ]]; then
        for pattern in "${PROBLEMATIC_PATTERNS[@]}"; do
            if grep -q "$pattern" "$config" 2>/dev/null; then
                echo "   ⚠️  WARNING: Found '$pattern' in $config"
            fi
        done
    fi
done

# 3. Update package.json to use Bun
echo ""
echo "3. Updating package.json to prefer Bun..."
if [[ -f package.json ]]; then
    # Add packageManager field if missing
    if ! grep -q '"packageManager"' package.json 2>/dev/null; then
        # Use jq if available, else sed
        if command -v jq >/dev/null 2>&1; then
            jq '. + {packageManager: "bun@latest"}' package.json > package.json.tmp && mv package.json.tmp package.json
        else
            echo "   Note: Install jq to auto-update package.json"
        fi
    fi
    echo "   ✓ package.json checked"
fi

# 4. Verify canonical zsh config
echo ""
echo "4. Verifying canonical zsh config..."
if [[ -f shell/.zshrc ]]; then
    echo "   ✓ Canonical .zshrc exists (comprehensive and optimal)"
    echo "   Note: Install with 'thegent install --target user'"
else
    echo "   ⚠️  Canonical .zshrc not found"
fi

# 5. Create Bun wrapper script
echo ""
echo "5. Creating Bun wrapper for faster JS execution..."
mkdir -p ~/.local/bin
cat > ~/.local/bin/bun-wrapper <<'EOF'
#!/usr/bin/env bash
# Fast Bun wrapper - use Bun for all JS/TS execution
exec bun "$@"
EOF
chmod +x ~/.local/bin/bun-wrapper
echo "   ✓ Created ~/.local/bin/bun-wrapper"

# 6. Summary
echo ""
echo "=== Optimization Complete ==="
echo ""
echo "Next steps:"
echo "1. Install canonical shell config (comprehensive and optimal):"
echo "   thegent install --target user"
echo ""
echo "2. Ensure Bun is in PATH:"
echo "   export PATH=\"\$HOME/.bun/bin:\$PATH\""
echo "   # Add to ~/.zshenv for persistence"
echo ""
echo "3. For JS/TS projects, use Bun:"
echo "   bun install    # instead of npm/pnpm install"
echo "   bun run dev    # instead of npm/pnpm run dev"
echo ""
echo "4. Test zsh startup speed:"
echo "   time zsh -c 'exit'"
echo "   # Should be <100ms with canonical config"
echo ""
