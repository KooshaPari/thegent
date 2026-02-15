#!/bin/bash
# Pre-commit hook to build VitePress docs when docs/ changes
# Exit on error
set -e

# Check if docs/ has changes
if ! git diff --cached --name-only | grep -q "^docs/"; then
  echo "No docs changes detected, skipping docsite build."
  exit 0
fi

echo "Docs changes detected, building docsite..."

# Check if pnpm is available
if ! command -v pnpm &> /dev/null; then
  echo "Error: pnpm not found. Please install pnpm first."
  exit 1
fi

# Build the docsite (run from root where package.json exists)
cd "$(git rev-parse --show-toplevel)"
pnpm run docs:build

echo "Docsite built successfully!"

# Stage the built files
git add docs-dist/
