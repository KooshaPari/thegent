#!/usr/bin/env zsh
# thegent bootstrap — full system installer (Unix)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- [install]
#
# Phases: install thegent → install -t all → install-shims → setup → doctor
#
# Options:
#   install       Full bootstrap (default)
#   --no-setup    Install CLI only, skip post-install setup
#   --full        Use thegent setup --full (install, shims, lock-cleanup, MCP)
#   --no-deps     Skip optional system deps (ripgrep, fd, jq)
#   --help        Show this help
#
# Environment:
#   THGENT_BOOTSTRAP_SYSTEM_SHIMS=1  Run install-shims --system (nix/direnv)
#   THGENT_BOOTSTRAP_DEPS=1          Install optional tools (rg, fd, jq) via brew/apt
#   THGENT_BOOTSTRAP_QUIET=1        Suppress non-critical warnings
#   THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE=1  Create .thegent-primary-main marker in current repo

set -e

GITHUB_RAW="https://raw.githubusercontent.com/kooshapari/thegent/main"
REPO_URL="https://github.com/kooshapari/thegent"

# --- Helpers ---
warn() {
  if [ -z "$THGENT_BOOTSTRAP_QUIET" ]; then
    echo "Warning: $*" >&2
  fi
}

die() {
  echo "Error: $*" >&2
  exit 1
}

step() {
  echo ""
  echo "==> $*"
}

# --- Usage ---
usage() {
  cat <<EOF
thegent bootstrap — full system installer

Installs thegent and configures your environment:
  1. Install thegent (uv → pipx → pip)
  2. thegent install -t all
  3. thegent install-shims
  4. thegent setup
  5. thegent doctor

Usage:
  curl -fsSL ${GITHUB_RAW}/scripts/bootstrap.sh | sh -s -- [options]

Options:
  install       Full bootstrap (default)
  --no-setup    Install CLI only
  --full        Use thegent setup --full (includes lock-cleanup, MCP service)
  --no-deps     Skip optional system deps
  --help        Show this help

Environment:
  THGENT_BOOTSTRAP_SYSTEM_SHIMS=1  Install git wrapper to system path
  THGENT_BOOTSTRAP_DEPS=1          Install ripgrep, fd, jq (brew/apt)
  THGENT_BOOTSTRAP_QUIET=1         Suppress non-critical warnings
  THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE=1  Write .thegent-primary-main in current git repo

Examples:
  curl -fsSL ${GITHUB_RAW}/scripts/bootstrap.sh | sh -s -- install
  curl -fsSL ${GITHUB_RAW}/scripts/bootstrap.sh | bash -s -- install --full
EOF
}

# --- Parse args ---
run_setup=1
use_full_setup=0
install_deps=0
install_worktree_governance="${THGENT_BOOTSTRAP_WORKTREE_GOVERNANCE:-1}"
[ -n "$THGENT_BOOTSTRAP_DEPS" ] && install_deps=1

for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    --no-setup) run_setup=0 ;;
    --full) use_full_setup=1 ;;
    --no-deps) install_deps=0 ;;
    install) ;;
    *) warn "Unknown option: $arg" ;;
  esac
done

# --- PATH ---
export PATH="${HOME}/.local/bin:${PATH}"
[ -d "/opt/homebrew/bin" ] && export PATH="/opt/homebrew/bin:${PATH}"
[ -d "/usr/local/bin" ] && export PATH="/usr/local/bin:${PATH}"

echo "thegent bootstrap"
echo "================="

# --- Phase 0: Optional system deps ---
if [ "$install_deps" = 1 ]; then
  step "Installing optional tools (ripgrep, fd, jq)..."
  if command -v brew >/dev/null 2>&1; then
    brew install ripgrep fd jq || warn "brew install ripgrep fd jq failed"
  elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq && sudo apt-get install -y ripgrep fd-find jq || warn "apt install failed"
  else
    warn "No brew or apt; skip optional deps or set THGENT_BOOTSTRAP_DEPS=0"
  fi
fi

# --- Phase 1: Install thegent ---
if command -v thegent >/dev/null 2>&1; then
  echo "==> thegent already installed: $(thegent --version 2>/dev/null || echo 'in PATH')"
else
  step "Installing thegent..."
  if command -v uv >/dev/null 2>&1; then
    uv tool install thegent
  elif command -v pipx >/dev/null 2>&1; then
    pipx install thegent
  elif command -v pip3 >/dev/null 2>&1; then
    pip3 install --user thegent
  elif command -v pip >/dev/null 2>&1; then
    pip install --user thegent
  else
    die "No installer (uv, pipx, pip). Install one:
  uv:   curl -LsSf https://astral.sh/uv/install.sh | sh
  pipx: pip install pipx && pipx ensurepath
  pip:  Install Python from python.org"
  fi
fi

export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v thegent >/dev/null 2>&1; then
  die "thegent not in PATH. Add to your shell profile:
  export PATH=\"\${HOME}/.local/bin:\${PATH}\""
fi

# --- Phase 2–5: Post-install (if not --no-setup) ---
if [ "$run_setup" != 1 ]; then
  echo ""
  echo "==> Install complete (--no-setup). Run when ready:"
  echo "    thegent install -t all && thegent setup && thegent doctor"
  exit 0
fi

if [ "$use_full_setup" = 1 ]; then
  step "Running thegent setup --full..."
  if thegent setup --full; then
    :
  else
    warn "setup --full had issues. Run 'thegent doctor' to diagnose."
  fi
else
  step "Running thegent install -t all..."
  thegent install -t all || warn "install -t all had issues. Run 'thegent doctor'."

  step "Running thegent install-shims..."
  thegent install-shims || warn "install-shims had issues. Run 'thegent doctor'."

  if [ -n "$THGENT_BOOTSTRAP_SYSTEM_SHIMS" ]; then
    step "Running thegent install-shims --system..."
    thegent install-shims --system 2>/dev/null || warn "install-shims --system skipped (requires sudo)."
  fi

  step "Running thegent setup..."
  thegent setup || warn "setup had issues. Run 'thegent setup' manually."
fi

# --- Phase 6: Verify ---
step "Running thegent doctor..."
if thegent doctor; then
  if [ "$install_worktree_governance" = 1 ]; then
    repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -n "$repo_root" ]; then
      marker="$repo_root/.thegent-primary-main"
      mkdir -p "${THGENT_WORKTREE_ROOT:-$repo_root/.worktrees}"
      if [ ! -f "$marker" ]; then
        cat > "$marker" <<'EOF'
# thegent primary checkout policy marker
# Keep this repository checkout on main.
# Use dedicated worktrees for branch development.
EOF
        echo "Created policy marker: $marker"
        echo "Governance docs: docs/governance/WORKTREE_AND_DELEGATION_INDEX.md"
      fi
    fi
  fi
  echo ""
  echo "Bootstrap complete. Try: thegent run \"Hello\" free"
else
  echo ""
  echo "Some checks failed. Run 'thegent doctor --fix' or see docs/guides/TROUBLESHOOTING.md"
  exit 1
fi
