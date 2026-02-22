#!/usr/bin/env zsh
# thegent-shims installation script
# Installs thegent-shims binary and creates harness symlinks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default installation directory
INSTALL_DIR="${HOME}/.local/bin"
BINARY_NAME="thegent-shims"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--install-dir <dir>]"
            echo ""
            echo "Options:"
            echo "  --install-dir <dir>  Installation directory (default: ~/.local/bin)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory (zsh-safe; avoids BASH_SOURCE dependency)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve binary path - look in various locations
resolve_binary_path() {
    local binary_path=""

    # Check if running from workspace (development)
    if [[ -f "${SCRIPT_DIR}/../crates/target/release/${BINARY_NAME}" ]]; then
        binary_path="${SCRIPT_DIR}/../crates/target/release/${BINARY_NAME}"
    # Check if running from crate-local target (development)
    elif [[ -f "${SCRIPT_DIR}/../crates/thegent-shims/target/release/${BINARY_NAME}" ]]; then
        binary_path="${SCRIPT_DIR}/../crates/thegent-shims/target/release/${BINARY_NAME}"
    # Check if already installed
    elif [[ -f "${INSTALL_DIR}/${BINARY_NAME}" ]]; then
        # Guard against self-referential symlink loops.
        if [[ -L "${INSTALL_DIR}/${BINARY_NAME}" ]] && [[ "$(readlink "${INSTALL_DIR}/${BINARY_NAME}" 2>/dev/null || true)" == "${INSTALL_DIR}/${BINARY_NAME}" ]]; then
            binary_path=""
        else
            binary_path="${INSTALL_DIR}/${BINARY_NAME}"
        fi
    # Try to find in common locations
    elif [[ -f "/usr/local/bin/${BINARY_NAME}" ]]; then
        binary_path="/usr/local/bin/${BINARY_NAME}"
    fi

    echo "$binary_path"
}

# Find or build the binary
find_or_build_binary() {
    local binary_path
    binary_path=$(resolve_binary_path)

    if [[ -n "$binary_path" ]]; then
        # Use stderr for info messages to avoid capturing in variable
        echo -e "${GREEN}Found existing binary: ${binary_path}${NC}" >&2
        echo "$binary_path"
        return 0
    fi

    # Try to build if not found
    echo -e "${YELLOW}Binary not found. Attempting to build...${NC}" >&2

    # Check if we're in a git repository with thegent-shims
    if [[ -f "${SCRIPT_DIR}/../crates/thegent-shims/Cargo.toml" ]]; then
        local build_dir="${SCRIPT_DIR}/../crates/thegent-shims"
        echo "Building thegent-shims..." >&2
        if command -v cargo &> /dev/null; then
            (cd "$build_dir" && cargo build --release)
            echo "${build_dir}/target/release/${BINARY_NAME}"
            return 0
        else
            echo -e "${RED}cargo not found. Please install Rust first.${NC}"
            return 1
        fi
    fi

    echo -e "${RED}Could not find or build thegent-shims binary.${NC}"
    return 1
}

# Create symlinks
create_symlinks() {
    local binary_path="$1"
    local link

    # Ensure install directory exists
    mkdir -p "$INSTALL_DIR"

    # Create the main binary symlink first
    echo -e "${GREEN}Installing ${BINARY_NAME} to ${INSTALL_DIR}/${BINARY_NAME}${NC}"
    ln -sf "$binary_path" "${INSTALL_DIR}/${BINARY_NAME}"

    local harnesses=("dex" "clode" "roid" "fanta" "antigma" "cline" "roocode" "opencode")
    for harness in "${harnesses[@]}"; do
        link="${INSTALL_DIR}/${harness}"
        echo -e "${GREEN}Creating harness shim: ${link}${NC}"
        ln -sf "${INSTALL_DIR}/${BINARY_NAME}" "$link"
    done
}

# Warn when a harness is shadowed by another binary earlier in PATH.
check_path_collisions() {
    local harness
    local resolved
    for harness in dex clode roid fanta antigma cline roocode opencode; do
        resolved="$(command -v "$harness" 2>/dev/null || true)"
        if [[ -n "$resolved" && "$resolved" != "${INSTALL_DIR}/${harness}" ]]; then
            echo -e "${YELLOW}Warning: '${harness}' resolves to ${resolved} (not ${INSTALL_DIR}/${harness}).${NC}"
            echo -e "${YELLOW}Add '${INSTALL_DIR}' earlier in PATH to use thegent-shims for '${harness}'.${NC}"
        fi
    done
}

# Main installation
main() {
    echo -e "${GREEN}=== thegent-shims Installation ===${NC}"
    echo ""

    # Check if INSTALL_DIR is in PATH
    if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
        echo -e "${YELLOW}Warning: ${INSTALL_DIR} is not in your PATH.${NC}"
        echo -e "${YELLOW}Add the following to your shell config (.bashrc, .zshrc, etc.):${NC}"
        echo ""
        echo "    export PATH=\"\${HOME}/.local/bin:\${PATH}\""
        echo ""
    fi

    # Find or build binary
    local binary_path
    if ! binary_path=$(find_or_build_binary); then
        echo -e "${RED}Failed to find or build thegent-shims${NC}"
        exit 1
    fi

    # Create symlinks
    create_symlinks "$binary_path"
    check_path_collisions

    echo ""
    echo -e "${GREEN}=== Installation Complete ===${NC}"
    echo ""
    echo "Installed shims:"
    echo "  - thegent-shims (main binary)"
    echo "  - dex -> thegent-shims"
    echo "  - clode -> thegent-shims"
    echo "  - roid -> thegent-shims"
    echo "  - fanta -> thegent-shims"
    echo "  - antigma -> thegent-shims"
    echo "  - cline -> thegent-shims"
    echo "  - roocode -> thegent-shims"
    echo "  - opencode -> thegent-shims"
    echo ""
    echo "Usage:"
    echo "  dex --help"
    echo "  clode --help"
    echo "  roid --help"
    echo "  fanta --help"
    echo "  antigma --help"
    echo "  cline --help"
    echo "  roocode --help"
    echo "  opencode --help"
}

main "$@"
