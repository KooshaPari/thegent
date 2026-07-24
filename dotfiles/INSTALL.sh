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

# Bundled zsh scripts (stow package under shell/stow/)
# Source-of-truth for: worktree-governance, fork-guardian, protected-processes,
# safeguards, org-secrets, refresh-zsh-cache. See shell/stow/README.md.
echo ""
echo "Installing bundled zsh scripts via stow..."
if [ -d "$DOTFILES/shell/stow" ]; then
  if command -v stow >/dev/null 2>&1; then
    ( cd "$DOTFILES/shell/stow" && stow --target="$HOME_DIR" --restow . ) \
      && echo -e "${GREEN}✓${NC} zsh bundle installed via stow" \
      || echo -e "${YELLOW}⚠${NC} stow returned non-zero; bundle may be partially linked. Inspect with 'stow --target=$HOME_DIR -n -v .' from shell/stow/"
  else
    echo -e "${YELLOW}⚠${NC} 'stow' not found on PATH — skipping shell/stow/ bundle install"
    echo -e "${YELLOW}  ${NC} Install GNU Stow (brew install stow) and re-run, or copy files from shell/stow/ manually"
  fi
else
  echo -e "${YELLOW}⚠${NC} shell/stow/ not present in this checkout — skipping bundle install"
fi

echo ""
echo -e "${GREEN}✓ All dotfiles installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Reload your shell: exec \$SHELL"
echo "  2. Run pre-commit install in any project: pre-commit install"
echo "  3. Verify git config: git config --list | grep user"
echo "  4. (Optional) Source the stow'd zsh scripts from ~/.zshrc:"
echo "       for f in ~/.zsh-worktree-governance.zsh \\"
echo "                ~/.zsh-fork-guardian.zsh \\"
echo "                ~/.zsh-protected-processes.zsh \\"
echo "                ~/.zsh-safeguards.zsh; do"
echo "         [[ -f \"\$f\" ]] && source \"\$f\""
echo "       done"
echo ""
