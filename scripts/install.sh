#!/usr/bin/env zsh
# thegent install — full system installer (Unix)
# Same as bootstrap.sh. Use either URL:
#   curl -fsSL .../scripts/install.sh | sh -s -- install
#   curl -fsSL .../scripts/bootstrap.sh | sh -s -- install
#
# Phases: install thegent → setup → doctor

set -e

GITHUB_RAW="https://raw.githubusercontent.com/kooshapari/thegent/main"
SCRIPT_URL="${GITHUB_RAW}/scripts/install.sh"

warn() { [ -z "$THGENT_BOOTSTRAP_QUIET" ] && echo "Warning: $*" >&2; }
die() { echo "Error: $*" >&2; exit 1; }
step() { echo ""; echo "==> $*"; }

usage() {
  cat <<EOF
thegent install — full system installer

Phases: install thegent → setup → doctor

Usage:
  curl -fsSL ${SCRIPT_URL} | sh -s -- [options]

Options:
  install       Full bootstrap (default)
  --no-setup    Install CLI only
  --full        Use thegent setup --full
  --no-deps     Skip optional system deps
  --rust-shims  Build and install Rust accelerators (requires Cargo)
  --help        Show this help

Environment:
  THGENT_BOOTSTRAP_SYSTEM_SHIMS=1  Install git wrapper to system path
  THGENT_BOOTSTRAP_DEPS=1          Install ripgrep, fd, jq (brew/apt)
  THGENT_BOOTSTRAP_QUIET=1         Suppress non-critical warnings
EOF
}

run_setup=1
use_full_setup=0
install_deps=0
install_rust_shims=0
[ -n "$THGENT_BOOTSTRAP_DEPS" ] && install_deps=1
[ -n "$THGENT_BOOTSTRAP_RUST_SHIMS" ] && install_rust_shims=1

for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    --no-setup) run_setup=0 ;;
    --full) use_full_setup=1 ;;
    --no-deps) install_deps=0 ;;
    --rust-shims) install_rust_shims=1 ;;
    install) ;;
    *) warn "Unknown option: $arg" ;;
  esac
done

export PATH="${HOME}/.local/bin:${PATH}"
[ -d "/opt/homebrew/bin" ] && export PATH="/opt/homebrew/bin:${PATH}"
[ -d "/usr/local/bin" ] && export PATH="/usr/local/bin:${PATH}"

echo "thegent install"
echo "==============="

if [ "$install_deps" = 1 ]; then
  step "Installing optional tools (Modern Unix)..."
  if command -v brew >/dev/null 2>&1; then
    brew install ripgrep fd jq eza bat zoxide delta duf dust procs bottom yazi xh sd \
                 zellij starship hyperfine tokei onefetch lazygit lazydocker grex \
                 mise proto pixi pkgx wasmtime wasmer zig bpftrace 2>/dev/null || warn "brew install failed"
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq && sudo apt-get install -y ripgrep fd-find jq eza bat zoxide 2>/dev/null || warn "apt install failed"
  fi
fi

if [ "$install_rust_shims" = 1 ]; then
  step "Building and installing Rust accelerators..."
  if [ -f "./scripts/install-thegent-shims.sh" ]; then
    ./scripts/install-thegent-shims.sh || warn "Rust shim installation failed. Falling back to default."
  elif command -v curl >/dev/null 2>&1; then
    # In case we're running via curl | sh and script is not local
    curl -fsSL "${GITHUB_RAW}/scripts/install-thegent-shims.sh" | bash || warn "Rust shim download/install failed."
  fi
fi

if command -v thegent >/dev/null 2>&1; then
  echo "==> thegent already installed: $(thegent --version 2>/dev/null || echo 'in PATH')"
else
  step "Installing thegent..."
  if command -v uv >/dev/null 2>&1; then
    uv tool install thegent
  elif command -v bun >/dev/null 2>&1; then
    bun install -g thegent
  elif command -v pipx >/dev/null 2>&1; then
    pipx install thegent
  elif command -v pip3 >/dev/null 2>&1; then
    pip3 install --user thegent
  elif command -v pip >/dev/null 2>&1; then
    pip install --user thegent
  else
    die "No installer (uv, bun, pipx, pip). Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi
fi

export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v thegent >/dev/null 2>&1; then
  die "thegent not in PATH. Add: export PATH=\"\${HOME}/.local/bin:\${PATH}\""
fi

if [ "$run_setup" != 1 ]; then
  echo ""
  echo "==> Install complete (--no-setup). Run: thegent setup"
  exit 0
fi

if [ "$use_full_setup" = 1 ]; then
  step "Running thegent setup --full..."
  thegent setup --full || warn "setup --full had issues. Run 'thegent doctor'."
else
  step "Running thegent setup..."
  thegent setup || warn "setup had issues. Run 'thegent setup' manually."
fi

step "Running thegent doctor..."
if thegent doctor; then
  echo ""
  echo "Bootstrap complete. Try: thegent run \"Hello\" free"
else
  echo ""
  echo "Some checks failed. Run 'thegent doctor --fix' or see docs/guides/TROUBLESHOOTING.md"
  exit 1
fi
