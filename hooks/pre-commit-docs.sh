#!/usr/bin/env bash
# Pre-commit hook to build VitePress docs when docs/ changes
# Exit on error
set -euo pipefail

# Determine project root and whether docs files are present in either
# staged or working-tree changes.
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! {
  git diff --cached --name-only;
  git diff --name-only;
} | rg '^docs/' >/dev/null 2>&1; then
  echo "No docs changes detected, skipping docsite build."
  exit 0
fi

required_pm="$(node -p "require('./package.json').packageManager?.split('@')[0] || 'bun'" 2>/dev/null || echo bun)"

case "$required_pm" in
  bun)
    if ! command -v bun >/dev/null 2>&1; then
      echo "Error: packageManager is bun but bun was not found in PATH."
      echo "Install Bun and ensure it is available before continuing."
      exit 1
    fi
    ;;
  pnpm)
    if ! command -v pnpm >/dev/null 2>&1; then
      echo "Error: packageManager is pnpm but pnpm was not found in PATH."
      echo "Install pnpm and ensure it is available before continuing."
      exit 1
    fi
    ;;
  *)
    echo "Error: unsupported packageManager '${required_pm}' in package.json."
    echo "Supported values: bun, pnpm."
    exit 1
    ;;
esac

echo "Docs changes detected, building docsite..."
if [[ "$required_pm" == "bun" ]]; then
  bun run docs:build
else
  pnpm run docs:build
fi

echo "Docsite built successfully!"

# Stage generated artifacts so downstream hooks and checks see updated files.
git add docs-dist/
