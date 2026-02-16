#!/bin/bash
#
# Multi-version build script for VitePress documentation
# Builds multiple versions of documentation for different branches/releases
#

set -e

# Configuration
DOCS_DIR="${DOCS_DIR:-docs}"
OUTPUT_DIR="${OUTPUT_DIR:-docs-dist}"
VERSIONS_FILE="${VERSIONS_FILE:-.versions}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if vitepress is installed
check_dependencies() {
  if ! command -v npx &> /dev/null; then
    log_error "npx is required but not installed"
    exit 1
  fi

  if [ ! -d "node_modules" ]; then
    log_warn "node_modules not found, running npm install..."
    npm install
  fi
}

# Build single version
build_version() {
  local version=$1
  local version_dir="${OUTPUT_DIR}/${version}"

  log_info "Building version: ${version}"

  # Create version-specific config if needed
  if [ -f "docs/.vitepress/config.${version}.ts" ]; then
    log_info "Using version-specific config: config.${version}.ts"
    cp "docs/.vitepress/config.${version}.ts" "docs/.vitepress/config.ts"
  fi

  # Build
  npx vitepress build "${DOCS_DIR}" --out-dir "${version_dir}"

  # Create version indicator
  echo "${version}" > "${version_dir}/.version"

  log_info "Built version: ${version} -> ${version_dir}"
}

# Main build function
main() {
  log_info "Starting multi-version documentation build..."

  check_dependencies

  # Clean output directory
  if [ -d "${OUTPUT_DIR}" ]; then
    log_info "Cleaning output directory: ${OUTPUT_DIR}"
    rm -rf "${OUTPUT_DIR}"
  fi

  # Check for versions file
  if [ -f "${VERSIONS_FILE}" ]; then
    log_info "Reading versions from ${VERSIONS_FILE}"
    while IFS= read -r version; do
      # Skip comments and empty lines
      [[ "$version" =~ ^#.*$ ]] && continue
      [[ -z "$version" ]] && continue

      build_version "$version"
    done < "${VERSIONS_FILE}"
  else
    # Build default version
    log_info "No versions file found, building default version"
    build_version "latest"
  fi

  # Generate index
  if [ -f "${OUTPUT_DIR}/index.html" ]; then
    log_info "Documentation built successfully!"
    log_info "Output directory: ${OUTPUT_DIR}"
  else
    log_error "Build failed - no output found"
    exit 1
  fi

  # List built versions
  if [ -d "${OUTPUT_DIR}" ]; then
    log_info "Built versions:"
    for dir in "${OUTPUT_DIR}"/*/; do
      if [ -d "$dir" ]; then
        version=$(basename "$dir")
        echo "  - ${version}"
      fi
    done
  fi
}

# Handle command line arguments
case "${1:-}" in
  --help|-h)
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --clean        Clean output directory before building"
    echo ""
    echo "Environment Variables:"
    echo "  DOCS_DIR       Documentation source directory (default: docs)"
    echo "  OUTPUT_DIR     Output directory (default: docs-dist)"
    echo "  VERSIONS_FILE  Versions config file (default: .versions)"
    echo ""
    echo "Example .versions file:"
    echo "  # One version per line"
    echo "  v1.0.0"
    echo "  v2.0.0"
    echo "  latest"
    ;;
  --clean)
    log_info "Cleaning output directory..."
    rm -rf "${OUTPUT_DIR}"
    shift
    main "$@"
    ;;
  *)
    main "$@"
    ;;
esac
