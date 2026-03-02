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
GIT_BINARY_NAME="thegent-git"
CHECKOUT_BINARY_NAME="thegent-git-checkout"

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

# Resolve the requested binary path - look in various locations
resolve_binary_path() {
    local binary_name="$1"
    local binary_path=""
    local installed_candidate=""
    local installed_resolved=""
    local workspace_target="${SCRIPT_DIR}/../crates/target/release"
    local crate_target="${SCRIPT_DIR}/../crates/thegent-shims/target/release"
    local candidate_binary_names=("${binary_name}")
    local candidate=""

    # Prefer workspace release target layout, then crate-local target fallback.
    if [[ "$binary_name" == "thegent-shims" ]]; then
        candidate_binary_names=("${binary_name}" "thegent-git" "thegent-git-checkout")
    fi

    for candidate in "${candidate_binary_names[@]}"; do
        if [[ -f "${workspace_target}/${candidate}" ]]; then
            binary_path="${workspace_target}/${candidate}"
            break
        elif [[ -f "${crate_target}/${candidate}" ]]; then
            binary_path="${crate_target}/${candidate}"
            break
        fi
    done

    if [[ -n "$binary_path" ]]; then
        echo "$binary_path"
        return 0
    fi

    if [[ -f "${INSTALL_DIR}/${binary_name}" ]]; then
        installed_candidate="${INSTALL_DIR}/${binary_name}"
        installed_resolved="$(realpath "$installed_candidate" 2>/dev/null || true)"

        if [[ -L "${INSTALL_DIR}/${binary_name}" ]] && [[ "$(readlink "${INSTALL_DIR}/${binary_name}" 2>/dev/null || true)" == "${INSTALL_DIR}/${binary_name}" ]]; then
            installed_candidate=""
            installed_resolved=""
        fi

        # Require the resolved target to be a matching binary name, not an unrelated link.
        if [[ -n "$installed_resolved" && "$(basename "$installed_resolved")" == "$binary_name" ]]; then
            binary_path="$installed_candidate"
        fi
    fi

    if [[ -z "$binary_path" && -f "/usr/local/bin/${binary_name}" ]]; then
        binary_path="/usr/local/bin/${binary_name}"
    fi

    echo "$binary_path"
}

# Find or build the binary
find_or_build_binary() {
    local binary_path
    local binary_name="$1"
    local workspace_target="${SCRIPT_DIR}/../crates/target/release"
    binary_path=$(resolve_binary_path "$binary_name")

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
            if (cd "$build_dir" && cargo build --release); then
                local built_binary_path=""
                built_binary_path="$(resolve_binary_path "$binary_name")"
                if [[ -n "$built_binary_path" && -x "$built_binary_path" ]]; then
                    echo "$built_binary_path"
                    return 0
                fi

                if [[ -n "$build_dir" && -n "${workspace_target}" && -f "${workspace_target}/thegent-shims" ]]; then
                    built_binary_path="${workspace_target}/thegent-shims"
                elif [[ -n "$build_dir" && -f "${workspace_target}/thegent-git-checkout" ]]; then
                    built_binary_path="${workspace_target}/thegent-git-checkout"
                elif [[ -n "$build_dir" && -f "${workspace_target}/thegent-git" ]]; then
                    built_binary_path="${workspace_target}/thegent-git"
                fi

                if [[ -n "$built_binary_path" && -x "$built_binary_path" ]]; then
                    echo "$built_binary_path"
                    return 0
                fi

                echo -e "${RED}Build succeeded but binary missing for ${binary_name}${NC}" >&2
                return 1
            fi

            echo -e "${RED}Build failed for ${binary_name}.${NC}" >&2
            return 1
        else
            echo -e "${RED}cargo not found. Please install Rust first.${NC}"
            return 1
        fi
    fi

    echo -e "${RED}Could not find or build ${binary_name} binary.${NC}"
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

    local harnesses=(
        "dex"
        "clode"
        "roid"
        "fanta"
        "antigma"
        "cline"
        "roocode"
        "opencode"
    )
    for harness in "${harnesses[@]}"; do
        link="${INSTALL_DIR}/${harness}"
        echo -e "${GREEN}Creating harness shim: ${link}${NC}"
        ln -sf "${INSTALL_DIR}/${BINARY_NAME}" "$link"
    done

    # Dedicated bin wrappers for high-risk commands (no shell dispatch)
    echo -e "${GREEN}Creating dedicated binary shims for git family${NC}"
    local dedicated_git
    local dedicated_checkout
    dedicated_git="$(resolve_binary_path "${GIT_BINARY_NAME}")"
    if [[ -n "$dedicated_git" ]]; then
        ln -sf "$dedicated_git" "${INSTALL_DIR}/${GIT_BINARY_NAME}"
    else
        ln -sf "${INSTALL_DIR}/${BINARY_NAME}" "${INSTALL_DIR}/${GIT_BINARY_NAME}"
    fi

    dedicated_checkout="$(resolve_binary_path "${CHECKOUT_BINARY_NAME}")"
    if [[ -n "$dedicated_checkout" ]]; then
        ln -sf "$dedicated_checkout" "${INSTALL_DIR}/${CHECKOUT_BINARY_NAME}"
    else
        ln -sf "${INSTALL_DIR}/${BINARY_NAME}" "${INSTALL_DIR}/${CHECKOUT_BINARY_NAME}"
    fi
}

# Warn when a harness is shadowed by another binary earlier in PATH.
check_path_collisions() {
    local harness
    local resolved
    for harness in \
        dex clode roid fanta antigma cline roocode opencode \
        thegent-git thegent-git-checkout; do
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
    if ! binary_path=$(find_or_build_binary "$BINARY_NAME"); then
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
    echo "  - thegent-git -> thegent-git"
    echo "  - thegent-git-checkout -> thegent-git-checkout"
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
