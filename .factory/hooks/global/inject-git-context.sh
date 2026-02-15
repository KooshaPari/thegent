#!/usr/bin/env bash
# Global hook: Inject git context on every prompt

if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  status=$(git status --porcelain 2>/dev/null | wc -l | xargs)
  
  if [ "$status" -gt 0 ]; then
    echo "📍 Branch: $branch ($status uncommitted changes)"
  else
    echo "📍 Branch: $branch (clean)"
  fi
fi

exit 0
