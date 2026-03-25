#!/usr/bin/env bash
#===============================================================================
# Install Git Hooks for Codebase Atlas
#===============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="${SCRIPT_DIR}/../hooks"
GIT_HOOKS_DIR="${1:-.git/hooks}"

usage() {
    cat <<EOF
Usage: $(basename "$0") [GIT_HOOKS_DIR]

Installs codebase atlas git hooks.

Options:
  GIT_HOOKS_DIR  Path to .git/hooks directory (default: .git/hooks)

Hooks Installed:
  post-commit: Generates atlas after every commit (async)
  pre-push: Updates atlas before push (amends commit)

Examples:
  $(basename "$0")                  # Install in current repo
  $(basename "$0") /path/to/.git/hooks  # Install in specific repo
EOF
}

install_hook() {
    local hook_name="$1"
    local source="${HOOKS_DIR}/${hook_name}"
    local target="${GIT_HOOKS_DIR}/${hook_name}"

    if [[ ! -f "$source" ]]; then
        echo "[WARN] Hook source not found: $source"
        return 1
    fi

    if [[ ! -d "$GIT_HOOKS_DIR" ]]; then
        mkdir -p "$GIT_HOOKS_DIR"
    fi

    # Backup existing hook if present
    if [[ -f "$target" ]]; then
        local backup="${target}.backup.$(date +%s)"
        cp "$target" "$backup"
        echo "[INFO] Backed up existing hook to: $backup"

        # Append to existing hook if it has content
        if [[ -s "$target" ]]; then
            echo "" >> "$target"
            echo "# === Atlas Hook ===" >> "$target"
            cat "$source" >> "$target"
            chmod +x "$target"
            echo "[INFO] Appended to existing hook: $hook_name"
            return 0
        fi
    fi

    # Install hook
    cp "$source" "$target"
    chmod +x "$target"

    echo "[INFO] Installed: $hook_name -> $target"
}

main() {
    if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
        usage
        exit 0
    fi

    echo "Installing codebase atlas hooks..."
    echo "Target: $GIT_HOOKS_DIR"
    echo ""

    # Check if in git repo
    if [[ ! -d ".git" ]]; then
        echo "[WARN] Not in a git repository. Hooks will be installed but may not function."
    fi

    # Check if hooks directory exists
    if [[ ! -d "$HOOKS_DIR" ]]; then
        echo "[ERROR] Hooks directory not found: $HOOKS_DIR"
        echo "Please ensure you ran this script from within the repository."
        exit 1
    fi

    install_hook "atlas-post-commit"
    install_hook "atlas-pre-push"

    echo ""
    echo "Done! Atlas hooks are now active."
    echo ""
    echo "To generate atlas manually:"
    echo "  ./scripts/generate_codebase_atlas.sh"
    echo ""
    echo "To uninstall hooks:"
    echo "  rm ${GIT_HOOKS_DIR}/atlas-post-commit"
    echo "  rm ${GIT_HOOKS_DIR}/atlas-pre-push"
}

main "$@"
