# =============================================================================
# install-git-hooks.sh — Set up all local Git hooks
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$(cd "$SCRIPT_DIR/hooks" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Detect if we're in a git repo
if [ ! -d ".git" ]; then
    error "Not in a Git repository. Run from project root."
    exit 1
fi

# Create hooks directory if it doesn't exist
HOOK_PATH="$(pwd)/.git/hooks"
mkdir -p "$HOOK_PATH"

# Link pre-push hook
if [ -f "$HOOKS_DIR/pre-push" ]; then
    ln -sf "$HOOKS_DIR/pre-push" "$HOOK_PATH/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    info "Installed pre-push hook → .git/hooks/pre-push"
else
    error "pre-push hook not found at $HOOKS_DIR/pre-push"
    exit 1
fi

# Link pre-commit hook if it exists
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    ln -sf "$HOOKS_DIR/pre-commit" "$HOOK_PATH/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    info "Installed pre-commit hook → .git/hooks/pre-commit"
fi

# Set core.hooksPath for the repo if not already set
if ! git config --get core.hooksPath > /dev/null 2>&1; then
    git config core.hooksPath "$HOOK_PATH"
    info "Set core.hooksPath to $HOOK_PATH"
else
    CURRENT_PATH="$(git config --get core.hooksPath)"
    if [ "$CURRENT_PATH" != "$HOOK_PATH" ]; then
        warn "core.hooksPath is already set to: $CURRENT_PATH"
        warn "To update: git config core.hooksPath '$HOOK_PATH'"
    else
        info "core.hooksPath already configured correctly"
    fi
fi

echo ""
info "Git hooks installed successfully!"
echo ""
echo "To skip hooks temporarily:"
echo "  SKIP_LOCAL_PREPUSH=1 git push"
echo ""
