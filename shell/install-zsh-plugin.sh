#!/usr/bin/env zsh
# install-zsh-plugin.sh - Install zsh-thegent-integration plugin

set -euo pipefail

SCRIPT_DIR="${${(%):-%x}:h}"
PLUGIN_NAME="zsh-thegent-integration"
TARGET_DIR="${HOME}/.zsh/${PLUGIN_NAME}"
STARSHIP_DIR="${HOME}/.config/starship"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Check prerequisites
check_prereqs() {
  log_info "Checking prerequisites..."
  
  # Check zsh
  if [[ -z "$(command -v zsh)" ]]; then
    log_error "zsh not found. Please install zsh first."
    exit 1
  fi
  log_info "  ✓ zsh: $(zsh --version)"
  
  # Check thegent
  if [[ -z "$(command -v thegent)" ]]; then
    log_warn "thegent not found in PATH. Some features may not work."
    log_warn "  Install: pip install thegent"
  else
    log_info "  ✓ thegent: $(thegent --version 2>/dev/null || echo 'found')"
  fi
  
  # Check starship
  if [[ -z "$(command -v starship)" ]]; then
    log_warn "starship not found. Starship module will not work."
    log_warn "  Install: brew install starship"
  else
    log_info "  ✓ starship: $(starship --version)"
  fi
}

# Create plugin directory
setup_plugin() {
  log_info "Setting up zsh plugin..."
  
  # Create plugin directory
  mkdir -p "${HOME}/.zsh"
  
  # Symlink or copy plugin
  if [[ -L "${TARGET_DIR}" ]]; then
    log_info "  Removing existing symlink..."
    rm "${TARGET_DIR}"
  elif [[ -d "${TARGET_DIR}" ]]; then
    log_info "  Removing existing directory..."
    rm -rf "${TARGET_DIR}"
  fi
  
  # Create symlink
  ln -s "${SCRIPT_DIR}/zsh-thegent-integration" "${TARGET_DIR}"
  log_info "  ✓ Plugin installed to: ${TARGET_DIR}"
  
  # Add to .zshrc if not present
  add_to_zshrc
}

add_to_zshrc() {
  local zshrc="${HOME}/.zshrc"
  local plugin_line="# thegent plugin
source \"\${HOME}/.zsh/${PLUGIN_NAME}/thegent.plugin.zsh\""
  
  if [[ -f "$zshrc" ]]; then
    if grep -q "thegent.plugin.zsh" "$zshrc"; then
      log_info "  ✓ Plugin already in .zshrc"
      return
    fi
  fi
  
  echo "" >> "$zshrc"
  echo "$plugin_line" >> "$zshrc"
  log_info "  ✓ Added plugin to .zshrc"
}

# Setup starship module
setup_starship() {
  log_info "Setting up Starship module..."
  
  # Create starship config directory
  mkdir -p "${STARSHIP_DIR}/modules"
  
  # Copy starship module
  local module_source="${SCRIPT_DIR}/starship/thegent.py"
  local module_target="${STARSHIP_DIR}/modules/thegent.py"
  
  if [[ -f "$module_source" ]]; then
    cp "$module_source" "$module_target"
    log_info "  ✓ Starship module installed to: ${module_target}"
    
    # Add to starship.toml if exists
    add_to_starship_config
  else
    log_warn "  Starship module not found: ${module_source}"
  fi
}

add_to_starship_config() {
  local starship_config="${STARSHIP_DIR}/config.toml"
  
  # Default config if file doesn't exist
  local thegent_config='
# thegent integration
[thegent]
symbol = "🤖"
format = "[$symbol($status )($work_stream )($lsp )]($style)"
style = "bold green"
disabled = false
show_work_stream = true
show_lsp = true
'
  
  if [[ -f "$starship_config" ]]; then
    if grep -q "^\[thegent\]" "$starship_config"; then
      log_info "  ✓ thegent config already in starship.toml"
      return
    fi
    
    echo "$thegent_config" >> "$starship_config"
    log_info "  ✓ Added thegent to starship.toml"
  else
    # Create new config
    cat > "$starship_config" << 'EOF'
# Starship configuration

format = """
$directory$git_branch$git_status
$thegent
$character"""

$thegent_config
EOF
    log_info "  ✓ Created starship.toml with thegent config"
  fi
}

# Print summary
print_summary() {
  echo ""
  echo "======================================"
  echo -e "${GREEN}Installation complete!${NC}"
  echo "======================================"
  echo ""
  echo "Next steps:"
  echo "  1. Restart your terminal or run: source ~/.zshrc"
  echo "  2. Test: tg status"
  echo "  3. Key bindings:"
  echo "       Alt+G - Quick thegent prompt"
  echo "       Alt+F - Quick file agent"
  echo "       Alt+S - Skills menu"
  echo ""
  echo "Available commands:"
  echo "  tg <cmd>       - Quick thegent alias"
  echo "  tgf <file>     - Run agent on file"
  echo "  tgs <skill>    - Run skill"
  echo "  tgp <prompt>   - Quick prompt"
  echo "  tgstatus       - Quick status check"
  echo "  tgwork         - Show work stream"
  echo ""
  echo "Async operations:"
  echo "  tgxa <cmd>     - Async execute"
  echo "  tgxj [job]     - Job status"
  echo "  tgxl <job>     - Job logs"
  echo ""
}

# Main
main() {
  log_info "Installing zsh-thegent-integration..."
  log_info "  Source: ${SCRIPT_DIR}"
  log_info "  Target: ${TARGET_DIR}"
  echo ""
  
  check_prereqs
  echo ""
  
  setup_plugin
  echo ""
  
  setup_starship
  echo ""
  
  print_summary
}

main "$@"
