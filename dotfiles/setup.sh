#!/usr/bin/env bash
# thegent dotfiles setup
# Idempotent bootstrap: detect OS, install deps, symlink configs
# Usage: ./dotfiles/setup.sh [--dry-run] [--no-tools] [--profile <name>]
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME}"
DRY_RUN=0
INSTALL_TOOLS=1
PROFILE=""

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}  ✓${RESET} $*"; }
info() { echo -e "${CYAN}  →${RESET} $*"; }
warn() { echo -e "${YELLOW}  ⚠${RESET} $*"; }
err()  { echo -e "${RED}  ✗${RESET} $*" >&2; }
step() { echo -e "\n${BOLD}${BLUE}━━ $* ━━${RESET}"; }

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=1; shift ;;
    --no-tools)   INSTALL_TOOLS=0; shift ;;
    --profile)    PROFILE="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--no-tools] [--profile <name>]"
      echo ""
      echo "Profiles: minimal, work-macos, home-linux, wsl, rust-dev, cloud-ops"
      exit 0
      ;;
    *) err "Unknown argument: $1"; exit 1 ;;
  esac
done

[[ $DRY_RUN -eq 1 ]] && warn "DRY-RUN mode — no changes will be made"

# ── OS detection ──────────────────────────────────────────────────────────────
detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  elif grep -qi microsoft /proc/version 2>/dev/null; then
    echo "wsl"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "linux"
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "windows"
  else
    echo "unknown"
  fi
}

OS=$(detect_os)
info "Detected OS: ${BOLD}${OS}${RESET}"

# ── Symlink helper ────────────────────────────────────────────────────────────
symlink() {
  local src="$1"
  local dst="$2"
  local dst_dir
  dst_dir="$(dirname "$dst")"

  if [[ ! -e "$src" ]]; then
    warn "Source does not exist, skipping: $src"
    return 0
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    info "Would link: $src → $dst"
    return 0
  fi

  [[ ! -d "$dst_dir" ]] && mkdir -p "$dst_dir"

  if [[ -L "$dst" ]]; then
    local current_target
    current_target="$(readlink "$dst")"
    if [[ "$current_target" == "$src" ]]; then
      ok "Already linked: $dst"
      return 0
    else
      warn "Relinking $dst (was → $current_target)"
      rm "$dst"
    fi
  elif [[ -e "$dst" ]]; then
    local backup="${dst}.bak.$(date +%Y%m%d_%H%M%S)"
    warn "Backing up existing $dst → $backup"
    mv "$dst" "$backup"
  fi

  ln -s "$src" "$dst"
  ok "Linked: $dst → $src"
}

# ── Install Homebrew (macOS) ──────────────────────────────────────────────────
install_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    ok "Homebrew already installed ($(brew --version | head -1))"
    return 0
  fi

  info "Installing Homebrew..."
  if [[ $DRY_RUN -eq 0 ]]; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add brew to PATH for Apple Silicon
    if [[ -f /opt/homebrew/bin/brew ]]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    ok "Homebrew installed"
  else
    info "Would install Homebrew"
  fi
}

# ── Install apt packages (Linux/WSL) ─────────────────────────────────────────
install_apt_packages() {
  info "Updating apt and installing base packages..."
  if [[ $DRY_RUN -eq 0 ]]; then
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends \
      curl wget git zsh build-essential pkg-config \
      ca-certificates gnupg lsb-release unzip \
      ripgrep fd-find bat fzf jq
    ok "apt packages installed"
  else
    info "Would run: apt-get install curl wget git zsh ..."
  fi
}

# ── Install mise (tool version manager) ──────────────────────────────────────
install_mise() {
  if command -v mise >/dev/null 2>&1; then
    ok "mise already installed ($(mise --version))"
    return 0
  fi

  info "Installing mise (tool version manager)..."
  if [[ $DRY_RUN -eq 0 ]]; then
    curl -sSf https://mise.run | sh
    # Add to PATH for this session
    export PATH="${HOME}/.local/bin:${PATH}"
    ok "mise installed"
  else
    info "Would install mise via: curl -sSf https://mise.run | sh"
  fi
}

# ── Install tools via mise ────────────────────────────────────────────────────
install_mise_tools() {
  local mise_config="${DOTFILES_DIR}/dev/.mise.toml"
  if [[ ! -f "$mise_config" ]]; then
    warn "No mise config found at $mise_config, skipping tool install"
    return 0
  fi

  if ! command -v mise >/dev/null 2>&1; then
    err "mise not found — run install_mise first"
    return 1
  fi

  info "Installing tools via mise (node, go, rust, bun, python)..."
  if [[ $DRY_RUN -eq 0 ]]; then
    mise install --config "$mise_config" 2>&1 | while read -r line; do
      info "  mise: $line"
    done
    ok "mise tools installed"
  else
    info "Would run: mise install --config $mise_config"
  fi
}

# ── Homebrew bundle ───────────────────────────────────────────────────────────
install_brew_bundle() {
  local brewfile="${DOTFILES_DIR}/macos/Brewfile"
  if [[ ! -f "$brewfile" ]]; then
    warn "No Brewfile found at $brewfile"
    return 0
  fi

  info "Installing Homebrew bundle from $brewfile..."
  if [[ $DRY_RUN -eq 0 ]]; then
    brew bundle --file="$brewfile" 2>&1 | grep -E "^(Installing|Tapping|Cask)" | while read -r line; do
      info "  brew: $line"
    done
    ok "Homebrew bundle installed"
  else
    info "Would run: brew bundle --file=$brewfile"
  fi
}

# ── Shell config symlinks ─────────────────────────────────────────────────────
link_shell_configs() {
  step "Linking shell configs"
  symlink "${DOTFILES_DIR}/shell/.zshrc"     "${HOME_DIR}/.zshrc"
  symlink "${DOTFILES_DIR}/shell/.bashrc"    "${HOME_DIR}/.bashrc"
  symlink "${DOTFILES_DIR}/shell/aliases.sh" "${HOME_DIR}/.aliases.sh"
}

# ── Git configs ───────────────────────────────────────────────────────────────
link_git_configs() {
  step "Linking git configs"
  symlink "${DOTFILES_DIR}/git/.gitconfig"       "${HOME_DIR}/.gitconfig"
  symlink "${DOTFILES_DIR}/git/.gitignore_global" "${HOME_DIR}/.gitignore_global"
}

# ── Claude configs ────────────────────────────────────────────────────────────
link_claude_configs() {
  step "Linking Claude configs"
  mkdir -p "${HOME_DIR}/.claude"
  symlink "${DOTFILES_DIR}/claude/CLAUDE.md" "${HOME_DIR}/.claude/CLAUDE.md"
  symlink "${DOTFILES_DIR}/claude/AGENTS.md" "${HOME_DIR}/.claude/AGENTS.md"
}

# ── Dev configs ───────────────────────────────────────────────────────────────
link_dev_configs() {
  step "Linking dev tool configs"
  symlink "${DOTFILES_DIR}/dev/.mise.toml"          "${HOME_DIR}/.config/mise/config.toml"
  symlink "${DOTFILES_DIR}/dev/Taskfile.global.yml" "${HOME_DIR}/Taskfile.yml"
}

# ── Editor configs ────────────────────────────────────────────────────────────
link_editor_configs() {
  step "Linking editor configs"

  # VS Code
  local vscode_dst
  case "$OS" in
    macos)   vscode_dst="${HOME_DIR}/Library/Application Support/Code/User" ;;
    linux|wsl) vscode_dst="${HOME_DIR}/.config/Code/User" ;;
    *)       vscode_dst="${HOME_DIR}/.vscode-settings" ;;
  esac
  symlink "${DOTFILES_DIR}/editors/vscode/settings.json" "${vscode_dst}/settings.json"
  symlink "${DOTFILES_DIR}/editors/vscode/keybindings.json" "${vscode_dst}/keybindings.json"

  # Cursor
  local cursor_dst
  case "$OS" in
    macos)   cursor_dst="${HOME_DIR}/Library/Application Support/Cursor/User" ;;
    linux|wsl) cursor_dst="${HOME_DIR}/.config/Cursor/User" ;;
    *)       cursor_dst="${HOME_DIR}/.cursor-settings" ;;
  esac
  symlink "${DOTFILES_DIR}/editors/cursor/settings.json" "${cursor_dst}/settings.json"
}

# ── macOS system defaults ─────────────────────────────────────────────────────
apply_macos_defaults() {
  if [[ "$OS" != "macos" ]]; then
    return 0
  fi
  step "Applying macOS system defaults"
  if [[ $DRY_RUN -eq 0 ]]; then
    # shellcheck source=dotfiles/macos/defaults.sh
    bash "${DOTFILES_DIR}/macos/defaults.sh"
    ok "macOS defaults applied"
  else
    info "Would run: ${DOTFILES_DIR}/macos/defaults.sh"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────────
echo -e "${BOLD}${CYAN}"
echo "  ┌─────────────────────────────────┐"
echo "  │   thegent dotfiles setup v1.0   │"
echo "  └─────────────────────────────────┘"
echo -e "${RESET}"
info "Dotfiles source: ${DOTFILES_DIR}"
info "Home directory:  ${HOME_DIR}"
[[ -n "$PROFILE" ]] && info "Profile: ${PROFILE}"

# 1. Package manager / system deps
step "Installing system dependencies"
case "$OS" in
  macos)
    install_homebrew
    if [[ $INSTALL_TOOLS -eq 1 ]]; then
      install_brew_bundle
    fi
    ;;
  linux|wsl)
    install_apt_packages
    ;;
  *)
    warn "Unsupported OS '${OS}' — skipping system package install"
    ;;
esac

# 2. Tool version manager
if [[ $INSTALL_TOOLS -eq 1 ]]; then
  step "Installing tool version manager"
  install_mise
  install_mise_tools
fi

# 3. Symlink configs
link_shell_configs
link_git_configs
link_claude_configs
link_dev_configs
link_editor_configs

# 4. macOS defaults
apply_macos_defaults

echo ""
echo -e "${BOLD}${GREEN}━━ Setup complete! ━━${RESET}"
echo ""
echo "  Next steps:"
echo "  1. Restart your shell:   exec \$SHELL"
echo "  2. Set git user info:    git config --global user.name 'Your Name'"
echo "                           git config --global user.email 'you@example.com'"
echo "  3. Authenticate gh CLI:  gh auth login"
echo ""
