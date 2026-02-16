#!/bin/bash
# Hook: PreToolUse (Write)
# Purpose: Enforce CLAUDE.md doc organization rules.
# Block creation of .md files in project root (except allowed files).
# Block creation of .md files outside docs/ subdirectories.

# Pre-init fast-path for dispatcher mode (non-.md files exit immediately)
[[ -n "${_HOOK_DISPATCHED:-}" && "${FILE_PATH:-}" != *.md ]] && exit 0

# Dispatched mode: skip common.sh entirely — env vars already set by dispatcher
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  set -euo pipefail
  HOOK_NAME="DOC-LOCATION-GUARD"
  # FILE_PATH and PROJECT_DIR already exported by dispatcher
else
  set -euo pipefail
  HOOK_NAME="DOC-LOCATION-GUARD"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

# Only check .md files
[[ "$FILE_PATH" != *.md ]] && exit 0

# Resolve to relative path from project root
REL_PATH="${FILE_PATH#"$PROJECT_DIR"/}"

# If path didn't change, it's outside project — allow
[[ "$REL_PATH" == "$FILE_PATH" ]] && exit 0

# Allowed root-level .md files
ALLOWED_ROOT=(
  "README.md"
  "CHANGELOG.md"
  "AGENTS.md"
  "CLAUDE.md"
  "claude.md"
  "00_START_HERE.md"
  "PRD.md"
  "ADR.md"
  "FUNCTIONAL_REQUIREMENTS.md"
  "PLAN.md"
  "USER_JOURNEYS.md"
)

# Check if file is in root (no / in relative path)
if [[ "$REL_PATH" != */* ]]; then
  for allowed in "${ALLOWED_ROOT[@]}"; do
    [[ "$REL_PATH" == "$allowed" ]] && exit 0
  done
  # Not in allowed list — block
  cat >&2 <<EOF
BLOCKED: Cannot create .md file in project root.
File: $REL_PATH
Move to appropriate docs/ subdirectory:
  - Guides: docs/guides/
  - Reports: docs/reports/
  - Research: docs/research/
  - Reference: docs/reference/
  - Checklists: docs/checklists/
EOF
  exit 2
fi

# Check that docs go into proper subdirectories
if [[ "$REL_PATH" == docs/*.md ]] && [[ "$REL_PATH" != docs/*/*.md ]]; then
  cat >&2 <<EOF
BLOCKED: .md files must be in docs/ subdirectories, not docs/ root.
File: $REL_PATH
Move to: docs/guides/, docs/reports/, docs/research/, docs/reference/, or docs/checklists/
EOF
  exit 2
fi

exit 0
