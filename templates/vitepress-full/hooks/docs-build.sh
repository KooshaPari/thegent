#!/bin/bash
#
# Pre-commit hook for auto-building VitePress documentation
# Installs as .git/hooks/pre-commit
#

set -e

# Configuration
DOCS_DIR="${DOCS_DIR:-docs}"
OUTPUT_DIR="${OUTPUT_DIR:-docs-dist}"
AUTO_BUILD="${AUTO_BUILD:-true}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[DOCS]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[DOCS]${NC} $1"
}

log_error() {
  echo -e "${RED}[DOCS ERROR]${NC} $1"
}

# Check if docs directory exists
check_docs() {
  if [ ! -d "${DOCS_DIR}" ]; then
    log_warn "No docs directory found at ${DOCS_DIR}, skipping docs build"
    exit 0
  fi
}

# Check for docs changes
check_changes() {
  # Get list of changed files in docs directory
  if git rev-parse --verify HEAD > /dev/null 2>&1; then
    against=HEAD
  else
    # Initial commit
    against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
  fi

  # Check for any docs changes
  if git diff --name-only --cached -- "${DOCS_DIR}" | grep -q .; then
    log_info "Docs files staged, building..."
    return 0
  elif git diff --name-only "${against}" -- "${DOCS_DIR}" | grep -q .; then
    log_info "Docs files modified, building..."
    return 0
  else
    log_info "No docs changes detected, skipping build"
    exit 0
  fi
}

# Install the hook
install_hook() {
  local hook_path=".git/hooks/pre-commit"
  local script_path="$(dirname "$0")/docs-build.sh"

  if [ -f "${hook_path}" ]; then
    if grep -q "docs-build.sh" "${hook_path}"; then
      log_info "Hook already installed"
      return 0
    fi
    log_warn "Pre-commit hook exists but doesn't include docs-build.sh"
    log_info "Appending to existing hook..."
    echo "" >> "${hook_path}"
    echo "# Docs build hook" >> "${hook_path}"
    echo "bash ${script_path}" >> "${hook_path}"
  else
    log_info "Installing pre-commit hook..."
    cat > "${hook_path}" << EOF
#!/bin/bash
# Docs auto-build pre-commit hook
bash "\$(dirname "\$0")/../../templates/vitepress-full/hooks/docs-build.sh"
EOF
    chmod +x "${hook_path}"
  fi

  log_info "Pre-commit hook installed successfully"
}

# Build docs
build_docs() {
  log_info "Building documentation..."

  # Check for package.json
  if [ ! -f "package.json" ]; then
    log_error "No package.json found"
    exit 1
  fi

  # Install dependencies if needed
  if [ ! -d "node_modules" ]; then
    log_info "Installing dependencies..."
    npm install
  fi

  # Build
  if command -v bun >/dev/null 2>&1; then
    bun x vitepress build "${DOCS_DIR}" --out-dir "${OUTPUT_DIR}"
  else
    npx vitepress build "${DOCS_DIR}" --out-dir "${OUTPUT_DIR}"
  fi

  if [ -f "${OUTPUT_DIR}/index.html" ]; then
    log_info "Documentation built successfully to ${OUTPUT_DIR}"
  else
    log_error "Build failed"
    exit 1
  fi
}

# Main
main() {
  # Skip if auto-build is disabled
  if [ "${AUTO_BUILD}" != "true" ]; then
    log_info "Auto-build disabled, skipping"
    exit 0
  fi

  # Skip if not in git repo
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_warn "Not a git repository, skipping"
    exit 0
  fi

  check_docs
  check_changes
  build_docs
}

# Handle arguments
case "${1:-}" in
  --install)
    install_hook
    ;;
  --check)
    check_docs
    check_changes
    log_info "Would build docs"
    ;;
  *)
    main
    ;;
esac
