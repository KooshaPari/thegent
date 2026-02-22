#!/bin/bash
# Cross-Platform System Setup Script for thegent
# Supports: macOS, Linux, Windows (WSL2), PowerShell
# After completion, thegent can be installed and run on any platform

set -euo pipefail

# Detect OS and shell
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            PLATFORM="macos"
            PACKAGE_MANAGER="homebrew"
            ;;
        Linux*)
            # Check if WSL2
            if grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
                PLATFORM="wsl2"
            else
                PLATFORM="linux"
            fi
            # Detect Linux package manager
            if command -v apt-get >/dev/null 2>&1; then
                PACKAGE_MANAGER="apt"
            elif command -v yum >/dev/null 2>&1; then
                PACKAGE_MANAGER="yum"
            elif command -v pacman >/dev/null 2>&1; then
                PACKAGE_MANAGER="pacman"
            elif command -v dnf >/dev/null 2>&1; then
                PACKAGE_MANAGER="dnf"
            else
                PACKAGE_MANAGER="unknown"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"
            PACKAGE_MANAGER="scoop"
            ;;
        *)
            PLATFORM="unknown"
            PACKAGE_MANAGER="unknown"
            ;;
    esac

    # Detect shell
    if [[ -n "${PSVersionTable:-}" ]] || command -v pwsh >/dev/null 2>&1; then
        SHELL_TYPE="powershell"
    else
        SHELL_TYPE="bash"
    fi
}

# Colors for output (works in bash/zsh)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Install package manager
install_package_manager() {
    case "$PACKAGE_MANAGER" in
        homebrew)
            if ! command -v brew >/dev/null 2>&1; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                if [[ -f /opt/homebrew/bin/brew ]]; then
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                fi
            fi
            ;;
        apt)
            log_info "Updating apt packages..."
            sudo apt-get update
            sudo apt-get install -y curl wget git build-essential
            ;;
        yum|dnf)
            log_info "Installing base packages..."
            sudo $PACKAGE_MANAGER install -y curl wget git gcc make
            ;;
        pacman)
            log_info "Installing base packages..."
            sudo pacman -Syu --noconfirm curl wget git base-devel
            ;;
        scoop)
            if ! command -v scoop >/dev/null 2>&1; then
                log_info "Installing Scoop..."
                if command -v pwsh >/dev/null 2>&1; then
                    pwsh -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force; iwr -useb get.scoop.sh | iex"
                else
                    log_warn "PowerShell not found, install Scoop manually"
                fi
            fi
            ;;
    esac
}

# Install mise (cross-platform)
install_mise() {
    log_info "Installing mise..."

    if command -v mise >/dev/null 2>&1; then
        log_success "mise already installed"
        return
    fi

    case "$PLATFORM" in
        macos)
            brew install mise
            ;;
        linux|wsl2)
            curl https://mise.run | sh
            ;;
        windows)
            if command -v scoop >/dev/null 2>&1; then
                scoop install mise
            else
                curl https://mise.run | sh
            fi
            ;;
    esac

    # Add to PATH
    export PATH="$HOME/.local/bin:$PATH"

    log_success "mise installed"
}

# Install tea (cross-platform)
install_tea() {
    log_info "Installing tea..."

    if command -v tea >/dev/null 2>&1; then
        log_success "tea already installed"
        return
    fi

    case "$PLATFORM" in
        macos)
            brew install teaxyz/pkgs/tea-cli
            ;;
        linux|wsl2|windows)
            sh <(curl https://tea.xyz)
            ;;
    esac

    log_success "tea installed"
}

# Install chezmoi (cross-platform)
install_chezmoi() {
    log_info "Installing chezmoi..."

    if command -v chezmoi >/dev/null 2>&1; then
        log_success "chezmoi already installed"
        return
    fi

    case "$PLATFORM" in
        macos)
            brew install chezmoi
            ;;
        linux|wsl2|windows)
            sh -c "$(curl -fsLS get.chezmoi.io)"
            ;;
    esac

    log_success "chezmoi installed"
}

# Install system packages (platform-specific)
install_system_packages() {
    log_info "Installing system packages for $PLATFORM..."

    case "$PACKAGE_MANAGER" in
        homebrew)
            brew install git curl wget zsh bash coreutils fzf ripgrep fd bat exa zoxide starship jq yq gh git-delta rust cargo
            brew install oven-sh/bun/bun
            ;;
        apt)
            sudo apt-get install -y git curl wget zsh bash build-essential fzf ripgrep fd bat exa jq yq gh rustc cargo
            # Install bun
            curl -fsSL https://bun.sh/install | bash
            ;;
        yum|dnf)
            sudo $PACKAGE_MANAGER install -y git curl wget zsh bash gcc make fzf ripgrep fd bat exa jq yq gh rust cargo
            curl -fsSL https://bun.sh/install | bash
            ;;
        pacman)
            sudo pacman -S --noconfirm git curl wget zsh bash base-devel fzf ripgrep fd bat exa jq yq github-cli rust cargo
            curl -fsSL https://bun.sh/install | bash
            ;;
        scoop)
            scoop install git curl wget zsh fzf ripgrep fd bat exa jq yq gh rust cargo bun
            ;;
    esac

    log_success "System packages installed"
}

# Setup mise configuration
setup_mise() {
    log_info "Setting up mise..."

    # Trust mise config
    mise trust ~/.mise.toml 2>/dev/null || true

    # Install global tool versions
    mise install python@3.12.9 node@24.13.1 ruby@3.3.7 || true

    # Set global versions
    mise use -g python@3.12.9 || true
    mise use -g node@24.13.1 || true
    mise use -g ruby@3.3.7 || true

    # Create .tool-versions
    cat > ~/.tool-versions << 'EOF'
python 3.12.9
node 24.13.1
ruby 3.3.7
EOF

    log_success "mise configured"
}

# Setup shell configuration (cross-platform)
setup_shell_config() {
    log_info "Setting up shell configuration..."

    case "$SHELL_TYPE" in
        powershell)
            # PowerShell profile
            if [[ "$PLATFORM" == "windows" ]]; then
                PROFILE_PATH="$PROFILE"
            else
                PROFILE_PATH="$HOME/.config/powershell/Microsoft.PowerShell_profile.ps1"
            fi

            mkdir -p "$(dirname "$PROFILE_PATH")"

            cat >> "$PROFILE_PATH" << 'POWERSHELL_EOF'
# mise hook for PowerShell
if (Get-Command mise -ErrorAction SilentlyContinue) {
    mise activate pwsh | Out-String | Invoke-Expression
}

# Add local bin to PATH
$env:PATH = "$HOME\.local\bin;$env:PATH"
POWERSHELL_EOF
            ;;
        bash)
            # Bash/zsh configuration
            if [[ ! -f ~/.zshenv ]]; then
                cat > ~/.zshenv << 'EOF'
# System shell environment
typeset -gU path

# PATH setup
path=(
  "$HOME/.local/bin"
  "$HOME/bin"
  $path
)
export PATH

# mise hook
if command -v mise >/dev/null 2>&1 && [[ -n "${PS1:-}" || -t 0 ]]; then
  eval "$(mise activate zsh)" 2>/dev/null || true
fi
EOF
            fi

            # Set zsh as default if available
            if command -v zsh >/dev/null 2>&1 && [[ "$SHELL" != "$(which zsh)" ]]; then
                chsh -s "$(which zsh)" || log_warn "Could not change shell"
            fi
            ;;
    esac

    log_success "Shell configuration set up"
}

# Create templates (cross-platform)
create_templates() {
    log_info "Creating templates..."

    mkdir -p ~/.templates

    # .tool-versions template
    cat > ~/.templates/.tool-versions << 'EOF'
python 3.12.9
node 24.13.1
ruby 3.3.7
EOF

    # .mise.toml template
    cat > ~/.templates/.mise.toml << 'EOF'
# mise configuration
[tools]
EOF

    # tea.yml template
    cat > ~/.templates/tea.yml << 'EOF'
dependencies:
  python.org: 3.12
  nodejs.org: 20
EOF

    # Shell script template
    if [[ "$PLATFORM" != "windows" ]]; then
        cat > ~/.templates/script.sh << 'EOF'
#!/bin/bash
set -euo pipefail
EOF
        chmod +x ~/.templates/script.sh
    else
        cat > ~/.templates/script.ps1 << 'EOF'
# PowerShell script template
param()
EOF
    fi

    # README template
    cat > ~/.templates/README.md << 'EOF'
# Project Name

## Setup

```bash
mise install
```

## Usage
EOF

    log_success "Templates created"
}

# Setup thegent (cross-platform)
setup_thegent() {
    log_info "Setting up thegent..."

    # Detect thegent directory (try common locations)
    THEGENT_DIRS=(
        "$HOME/temp-PRODVERCEL/485/kush/thegent"
        "$HOME/thegent"
        "$HOME/projects/thegent"
        "./thegent"
    )

    THEGENT_DIR=""
    for dir in "${THEGENT_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            THEGENT_DIR="$dir"
            break
        fi
    done

    if [[ -z "$THEGENT_DIR" ]]; then
        log_warn "thegent directory not found"
        return
    fi

    log_info "Found thegent at $THEGENT_DIR"
    cd "$THEGENT_DIR"

    # Install dependencies
    if [[ -f "package.json" ]]; then
        if command -v bun >/dev/null 2>&1; then
            bun install || log_warn "bun install failed"
        elif command -v npm >/dev/null 2>&1; then
            npm install || log_warn "npm install failed"
        fi
    fi

    # Build Rust extensions (if Makefile exists)
    if [[ -f "Makefile" ]] && command -v make >/dev/null 2>&1 && command -v cargo >/dev/null 2>&1; then
        make install || log_warn "make install failed"
    fi

    # Setup shell symlinks (Unix-like only)
    if [[ "$PLATFORM" != "windows" ]] && [[ -d "$THEGENT_DIR/shell" ]]; then
        [[ ! -f ~/.zsh_bundle.zsh ]] && ln -sf "$THEGENT_DIR/shell/.zsh_bundle.zsh" ~/.zsh_bundle.zsh || true
        [[ ! -f ~/.zsh_safeguards.zsh ]] && ln -sf "$THEGENT_DIR/shell/.zsh_safeguards.zsh" ~/.zsh_safeguards.zsh || true
        [[ ! -f ~/.zsh_optimization.zsh ]] && ln -sf "$THEGENT_DIR/shell/.zsh_optimization.zsh" ~/.zsh_optimization.zsh || true
        [[ ! -f ~/.zsh_advanced.zsh ]] && ln -sf "$THEGENT_DIR/shell/.zsh_advanced.zsh" ~/.zsh_advanced.zsh || true
    fi

    log_success "thegent setup completed"
}

# WSL2 specific setup
setup_wsl2() {
    if [[ "$PLATFORM" != "wsl2" ]]; then
        return
    fi

    log_info "Configuring WSL2-specific settings..."

    # Install Windows interop tools
    sudo apt-get install -y wslu || true

    # Setup Windows PATH integration
    if [[ ! -f ~/.wslconfig ]]; then
        cat > ~/.wslconfig << 'EOF'
[wsl2]
interop.appendWindowsPath=true
EOF
    fi

    log_success "WSL2 configured"
}

# Main installation
main() {
    log_info "Starting cross-platform installation..."
    echo ""

    detect_platform
    log_info "Detected: $PLATFORM ($PACKAGE_MANAGER, $SHELL_TYPE)"
    echo ""

    install_package_manager
    install_mise
    install_tea
    install_chezmoi
    install_system_packages
    setup_mise
    setup_shell_config
    create_templates
    setup_thegent

    if [[ "$PLATFORM" == "wsl2" ]]; then
        setup_wsl2
    fi

    echo ""
    log_success "═══════════════════════════════════════════════════════"
    log_success "Installation Complete!"
    log_success "═══════════════════════════════════════════════════════"
    echo ""
    log_info "Platform: $PLATFORM"
    log_info "Shell: $SHELL_TYPE"
    echo ""
    log_info "Next steps:"
    echo "  1. Restart your terminal"
    echo "  2. Run: mise list (to verify tools)"
    echo "  3. Use thegent!"
    echo ""
}

main "$@"
