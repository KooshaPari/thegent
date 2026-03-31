#!/bin/bash
# distribute.sh — Distribute governance files to consumer repositories
#
# Purpose:
#   Pushes governance templates, hooks, and configuration from thegent (source of truth)
#   to consumer repositories (thegent-dependent projects).
#
# Usage:
#   ./scripts/distribution/distribute.sh <target-repo-path> [--force] [--no-backup]
#
# Arguments:
#   target-repo-path   Path to the target repository
#   --force            Overwrite existing files without prompting
#   --no-backup        Do not create backups of existing files
#
# Respects:
#   - Existing customizations (skips if .local-override marker exists)
#   - Backup originals before overwriting
#   - Pre-commit hook configuration

set -euo pipefail

# Configuration
THEGENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="${THEGENT_ROOT}/scripts/distribution"
GOVERNANCE_SOURCE="${THEGENT_ROOT}/hooks"
PRE_COMMIT_SOURCE="${THEGENT_ROOT}/.pre-commit-config.yaml"
TASKFILE_SOURCE="${THEGENT_ROOT}/Taskfile.yml"

# Parse arguments
TARGET_REPO="${1:-.}"
FORCE_OVERWRITE=false
CREATE_BACKUP=true

while [[ $# -gt 1 ]]; do
  case "$2" in
    --force)
      FORCE_OVERWRITE=true
      shift
      ;;
    --no-backup)
      CREATE_BACKUP=false
      shift
      ;;
    *)
      echo "Unknown option: $2" >&2
      exit 1
      ;;
  esac
done

# Validate target repo
if [[ ! -d "${TARGET_REPO}/.git" ]]; then
  echo "Error: ${TARGET_REPO} is not a git repository" >&2
  exit 1
fi

TARGET_REPO="$(cd "${TARGET_REPO}" && pwd)"
TARGET_HOOKS="${TARGET_REPO}/hooks"
TARGET_PRE_COMMIT="${TARGET_REPO}/.pre-commit-config.yaml"
TARGET_TASKFILE="${TARGET_REPO}/Taskfile.yml"

echo "Distributing governance from thegent..."
echo "  Source:  ${THEGENT_ROOT}"
echo "  Target:  ${TARGET_REPO}"
echo

# Function to check for local override marker
has_local_override() {
  local file="$1"
  [[ -f "${file}" ]] && grep -q "# .local-override" "${file}" && return 0 || return 1
}

# Function to backup file
backup_file() {
  local file="$1"
  if [[ -f "${file}" ]] && [[ "${CREATE_BACKUP}" == true ]]; then
    local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "${file}" "${backup}"
    echo "  ✓ Backed up: ${file} -> ${backup}"
  fi
}

# Function to sync file with confirmation
sync_file() {
  local source="$1"
  local target="$2"
  local description="$3"

  if [[ ! -f "${source}" ]]; then
    echo "  ⚠ Source not found: ${source}"
    return 1
  fi

  if [[ -f "${target}" ]]; then
    if has_local_override "${target}"; then
      echo "  ⊘ Skipping (local override): ${target}"
      return 0
    fi

    if [[ "${FORCE_OVERWRITE}" != true ]]; then
      echo "  ? File exists: ${target}"
      read -p "    Overwrite? (y/n) " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  ⊘ Skipped: ${target}"
        return 0
      fi
    fi

    backup_file "${target}"
  fi

  cp "${source}" "${target}"
  echo "  ✓ Synced: ${description}"
}

# Function to sync directory with confirmation
sync_directory() {
  local source="$1"
  local target="$2"
  local description="$3"

  if [[ ! -d "${source}" ]]; then
    echo "  ⚠ Source directory not found: ${source}"
    return 1
  fi

  mkdir -p "${target}"

  # Sync all files from source
  while IFS= read -r -d '' srcfile; do
    relpath="${srcfile#${source}/}"
    targetfile="${target}/${relpath}"

    if has_local_override "${targetfile}"; then
      echo "  ⊘ Skipping (local override): ${relpath}"
      continue
    fi

    mkdir -p "$(dirname "${targetfile}")"

    if [[ -f "${targetfile}" ]] && [[ "${FORCE_OVERWRITE}" != true ]]; then
      echo "  ? File exists: ${relpath}"
      read -p "    Overwrite? (y/n) " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  ⊘ Skipped: ${relpath}"
        continue
      fi
    fi

    backup_file "${targetfile}"
    cp "${srcfile}" "${targetfile}"
    echo "  ✓ Synced: ${relpath}"
  done < <(find "${source}" -type f -print0)

  echo "  ✓ Synced directory: ${description}"
}

# Perform sync operations
echo "1. Syncing governance hooks..."
sync_directory "${GOVERNANCE_SOURCE}" "${TARGET_HOOKS}" "governance hooks"

echo
echo "2. Syncing pre-commit configuration..."
sync_file "${PRE_COMMIT_SOURCE}" "${TARGET_PRE_COMMIT}" ".pre-commit-config.yaml"

echo
echo "3. Installing pre-commit hooks in target repo..."
(
  cd "${TARGET_REPO}"
  if command -v pre-commit &>/dev/null; then
    pre-commit install || echo "  ⚠ pre-commit install failed (pre-commit may not be installed)"
  else
    echo "  ⚠ pre-commit not found in PATH"
  fi
)

echo
echo "4. Syncing Taskfile (if not customized)..."
if [[ -f "${TARGET_TASKFILE}" ]]; then
  if ! has_local_override "${TARGET_TASKFILE}"; then
    backup_file "${TARGET_TASKFILE}"
    cp "${TASKFILE_SOURCE}" "${TARGET_TASKFILE}"
    echo "  ✓ Synced: Taskfile.yml"
  else
    echo "  ⊘ Skipping Taskfile (local override detected)"
  fi
else
  cp "${TASKFILE_SOURCE}" "${TARGET_TASKFILE}"
  echo "  ✓ Created: Taskfile.yml"
fi

echo
echo "5. Summary of distribution targets:"
echo "  - hooks/                          — Governance hooks (all scripts)"
echo "  - .pre-commit-config.yaml          — Pre-commit configuration"
echo "  - Taskfile.yml                     — Task runner (if not customized)"

echo
echo "✓ Distribution complete!"
echo
echo "Next steps:"
echo "  1. Review changes: cd ${TARGET_REPO} && git status"
echo "  2. Commit: git add -A && git commit -m 'chore: sync governance from thegent'"
echo "  3. Test hooks: pre-commit run --all-files (optional)"
