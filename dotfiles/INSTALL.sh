#!/usr/bin/env bash
# thegent dotfiles installer
# Installs shell, git, and Claude development environment configs on a new system
# Usage: ./dotfiles/INSTALL.sh

set -e

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"

echo "Installing thegent dotfiles from: $DOTFILES"
echo "Target home: $HOME_DIR"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Shell configs
echo "Installing shell configs..."
ln -sf "$DOTFILES/shell/zshrc" "$HOME_DIR/.zshrc" && echo -e "${GREEN}✓${NC} .zshrc linked"
ln -sf "$DOTFILES/shell/bashrc" "$HOME_DIR/.bashrc" && echo -e "${GREEN}✓${NC} .bashrc linked"

# Git config
echo ""
echo "Installing git config..."
ln -sf "$DOTFILES/git/gitconfig" "$HOME_DIR/.gitconfig" && echo -e "${GREEN}✓${NC} .gitconfig linked"

# Editor configs
echo ""
echo "Installing editor configs..."
ln -sf "$DOTFILES/editors/editorconfig" "$HOME_DIR/.editorconfig" 2>/dev/null && echo -e "${GREEN}✓${NC} .editorconfig linked" || echo -e "${YELLOW}⚠${NC} .editorconfig not found (optional)"

# Tool configs (linters, quality gates)
echo ""
echo "Installing tool configs..."
ln -sf "$DOTFILES/tools/shellcheckrc" "$HOME_DIR/.shellcheckrc" && echo -e "${GREEN}✓${NC} .shellcheckrc linked"
ln -sf "$DOTFILES/tools/vale.ini" "$HOME_DIR/.vale.ini" && echo -e "${GREEN}✓${NC} .vale.ini linked"
ln -sf "$DOTFILES/tools/pre-commit-config.yaml" "$HOME_DIR/.pre-commit-config.yaml" && echo -e "${GREEN}✓${NC} .pre-commit-config.yaml linked"
ln -sf "$DOTFILES/tools/jscpd.json" "$HOME_DIR/.jscpd.json" && echo -e "${GREEN}✓${NC} .jscpd.json linked"
ln -sf "$DOTFILES/tools/importlinter" "$HOME_DIR/.importlinter" && echo -e "${GREEN}✓${NC} .importlinter linked"

# Claude development environment
echo ""
echo "Installing Claude development configs..."
mkdir -p "$HOME_DIR/.claude"
cp "$DOTFILES/claude/AGENTS.md" "$HOME_DIR/.claude/AGENTS.md" && echo -e "${GREEN}✓${NC} AGENTS.md copied"
cp "$DOTFILES/claude/settings.json" "$HOME_DIR/.claude/settings.json" && echo -e "${GREEN}✓${NC} settings.json copied"
chmod 600 "$HOME_DIR/.claude/settings.json"

echo ""
echo -e "${GREEN}✓ All dotfiles installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Reload your shell: exec \$SHELL"
echo "  2. Run pre-commit install in any project: pre-commit install"
echo "  3. Verify git config: git config --list | grep user"
echo ""
