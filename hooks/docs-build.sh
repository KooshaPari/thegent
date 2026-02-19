#!/bin/zsh
# Pre-commit hook: build docs if docs changed

CHANGED_FILES=$(git diff --name-only --cached)
DOCS_CHANGED=$(echo "$CHANGED_FILES" | grep -E '\.md$' | grep -E '^docs/' || true)

if [ -n "$DOCS_CHANGED" ]; then
  echo "Markdown docs changed, building..."
  pnpm docs:build
  if [ $? -ne 0 ]; then
    echo "ERROR: Doc build failed"
    exit 1
  fi
  echo "Doc build successful"
fi

exit 0
