#!/usr/bin/env zsh
# Install zsh plugins for ~/.zshrc.local (fnm, fzf-tab, autosuggestions, etc.)
# Run from thegent repo root or with THEGENT_ROOT set.
# Usage: ./scripts/install_zsh_plugins.sh [--template-only]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${THEGENT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ZSH_PLUGINS="${HOME}/.zsh/plugins"
ZSH_THEMES="${HOME}/.zsh/themes"

usage() {
  echo "Usage: $0 [--template-only]"
  echo "  --template-only  Only copy zshrc.local.template, don't install plugins"
  exit 0
}

[[ "${1:-}" == "--help" || "${1:-}" == "-h" ]] && usage

TEMPLATE_ONLY=false
[[ "${1:-}" == "--template-only" ]] && TEMPLATE_ONLY=true

echo "=== Zsh Plugin Installer ==="
echo ""

# 1. Ensure plugin dirs exist
mkdir -p "$ZSH_PLUGINS" "$ZSH_THEMES"

# 2. Install plugins (git clone if not present)
install_plugin() {
  local name="$1"
  local url="$2"
  local dest="$3"
  if [[ -d "$dest" ]]; then
    echo "  ✓ $name already installed at $dest"
  else
    echo "  Installing $name..."
    git clone --depth 1 "$url" "$dest"
    echo "  ✓ $name installed"
  fi
}

if [[ "$TEMPLATE_ONLY" != true ]]; then
  echo "1. Installing plugins..."
  install_plugin "fzf-tab" "https://github.com/Aloxaf/fzf-tab.git" "$ZSH_PLUGINS/fzf-tab"
  install_plugin "zsh-autosuggestions" "https://github.com/zsh-users/zsh-autosuggestions.git" "$ZSH_PLUGINS/zsh-autosuggestions"
  install_plugin "fast-syntax-highlighting" "https://github.com/zdharma-continuum/fast-syntax-highlighting.git" "$ZSH_PLUGINS/fast-syntax-highlighting"
  echo ""

  echo "2. Checking fzf..."
  if command -v fzf &>/dev/null; then
    echo "  ✓ fzf installed"
  else
    echo "  ⚠ fzf not found. Install with: brew install fzf"
  fi
  echo ""

  echo "3. Checking Node version manager (fnm/mise)..."
  if command -v fnm &>/dev/null; then
    echo "  ✓ fnm installed"
  elif command -v mise &>/dev/null; then
    echo "  ✓ mise installed"
  else
    echo "  ⚠ Neither fnm nor mise found. Install with:"
    echo "    brew install fnm   # Node only"
    echo "    brew install mise  # Node, Python, Go, etc."
  fi
  echo ""
fi

# 4. Copy template to ~/.zshrc.local if it doesn't exist
TEMPLATE="$REPO_ROOT/shell/zshrc.local.template"
if [[ -f "$TEMPLATE" ]]; then
  if [[ ! -f "${HOME}/.zshrc.local" ]]; then
    cp "$TEMPLATE" "${HOME}/.zshrc.local"
    echo "4. Created ~/.zshrc.local from template"
  else
    echo "4. ~/.zshrc.local exists; not overwriting. Compare with: $TEMPLATE"
  fi
else
  echo "4. Template not found at $TEMPLATE"
fi

echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Open a new terminal or run: exec zsh"
echo "  2. Edit ~/.zshrc.local to uncomment fnm/mise and prompt (starship/p10k)"
echo "  3. See docs/guides/SHELL_ZSH_PLUGIN_SETUP.md for full guide"
echo ""
