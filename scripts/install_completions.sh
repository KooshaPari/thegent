#!/usr/bin/env bash
# install_completions.sh — Install thegent shell completions.
#
# Detects the current shell and runs the appropriate
# `thegent --install-completion` invocation provided by typer.
#
# @trace WL-040 WP-4003
#
# Usage:
#   bash scripts/install_completions.sh

set -euo pipefail

DETECTED_SHELL="${SHELL:-}"
SHELL_NAME="$(basename "${DETECTED_SHELL}")"

echo "Detected shell: ${SHELL_NAME}"

case "${SHELL_NAME}" in
    zsh)
        COMP_SHELL="zsh"
        ;;
    bash)
        COMP_SHELL="bash"
        ;;
    fish)
        COMP_SHELL="fish"
        ;;
    *)
        echo "Unsupported shell '${SHELL_NAME}'. Supported: bash, zsh, fish." >&2
        exit 1
        ;;
esac

echo "Installing thegent completions for ${COMP_SHELL}..."

# typer's --install-completion respects the _TYPER_COMPLETE_SHELL env var
# when passed as argument, or auto-detects from SHELL.
thegent --install-completion "${COMP_SHELL}"

echo "Done. Restart your shell (or source your rc file) for completions to take effect."
