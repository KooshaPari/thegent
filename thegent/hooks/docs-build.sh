#!/bin/zsh
# Pre-commit hook: build docs if docs changed

set -e

CHANGED_FILES=$(git diff --name-only --cached)
DOCS_CHANGED=$(echo "$CHANGED_FILES" | rg '\.md$' | rg '^docs/' || true)

if [ -n "$DOCS_CHANGED" ]; then
  echo "Markdown docs changed, building..."
  required_pm="$(node -p \"require('./package.json').packageManager?.split('@')[0] || 'bun'\" 2>/dev/null || echo bun)"
  case "$required_pm" in
    bun)
      bun run docs:build
      ;;
    pnpm)
      pnpm run docs:build
      ;;
    *)
      echo "Unsupported packageManager: ${required_pm}. Expected bun or pnpm."
      exit 1
      ;;
  esac
  if [ $? -ne 0 ]; then
    echo "ERROR: Doc build failed"
    exit 1
  fi
  echo "Doc build successful"
fi

exit 0
