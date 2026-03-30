#!/bin/bash
# validate-sync.sh — Check for governance drift between thegent and consumer repos
#
# Purpose:
#   Compares governance files in consumer repositories against thegent (source of truth).
#   Reports which repos are out of date and suggests update commands.
#
# Usage:
#   ./scripts/distribution/validate-sync.sh [consumer-repo-path] [--all] [--verbose]
#
# Arguments:
#   consumer-repo-path  Path to consumer repo (optional; defaults to current directory)
#   --all              Check against all known consumer repos (from config)
#   --verbose          Show detailed diff output

set -euo pipefail

# Configuration
THEGENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="${THEGENT_ROOT}/scripts/distribution"
CONFIG_FILE="${SCRIPT_DIR}/consumer-repos.txt"

# Known consumer repos (if config file doesn't exist, define defaults)
CONSUMER_REPOS=(
  "${THEGENT_ROOT}/../../AgilePlus"
  "${THEGENT_ROOT}/../../phenotype-infrakit"
  "${THEGENT_ROOT}/../../heliosCLI"
)

# Parse arguments
CONSUMER_REPO="${1:-.}"
CHECK_ALL=false
VERBOSE=false

while [[ $# -gt 1 ]]; do
  case "$2" in
    --all)
      CHECK_ALL=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown option: $2" >&2
      exit 1
      ;;
  esac
done

# Load consumer repos from config if it exists
if [[ -f "${CONFIG_FILE}" ]]; then
  mapfile -t CONSUMER_REPOS < "${CONFIG_FILE}"
fi

# Function to validate a single repo
validate_repo() {
  local repo_path="$1"
  local repo_name="$(basename "${repo_path}")"

  if [[ ! -d "${repo_path}/.git" ]]; then
    echo "✗ ${repo_name}: Not a git repository"
    return 1
  fi

  local out_of_sync=false
  local drift_files=()

  # Check hooks directory
  local target_hooks="${repo_path}/hooks"
  if [[ ! -d "${target_hooks}" ]]; then
    echo "⚠ ${repo_name}: hooks/ directory missing"
    out_of_sync=true
  else
    while IFS= read -r -d '' sourcefile; do
      local relpath="${sourcefile#${THEGENT_ROOT}/hooks/}"
      local targetfile="${target_hooks}/${relpath}"

      if [[ ! -f "${targetfile}" ]]; then
        drift_files+=("hooks/${relpath} (missing)")
        out_of_sync=true
      elif ! diff -q "${sourcefile}" "${targetfile}" >/dev/null 2>&1; then
        drift_files+=("hooks/${relpath} (outdated)")
        out_of_sync=true
      fi
    done < <(find "${THEGENT_ROOT}/hooks" -type f -print0)
  fi

  # Check .pre-commit-config.yaml
  local target_pre_commit="${repo_path}/.pre-commit-config.yaml"
  if [[ ! -f "${target_pre_commit}" ]]; then
    drift_files+=(".pre-commit-config.yaml (missing)")
    out_of_sync=true
  elif ! diff -q "${THEGENT_ROOT}/.pre-commit-config.yaml" "${target_pre_commit}" >/dev/null 2>&1; then
    drift_files+=(".pre-commit-config.yaml (outdated)")
    out_of_sync=true
  fi

  # Report findings
  if [[ "${out_of_sync}" == true ]]; then
    echo "✗ ${repo_name}: OUT OF SYNC"
    if [[ "${VERBOSE}" == true ]]; then
      for drift_file in "${drift_files[@]}"; do
        echo "    - ${drift_file}"
      done
    fi
    echo "    Update: ${SCRIPT_DIR}/distribute.sh ${repo_path} --force"
    return 1
  else
    echo "✓ ${repo_name}: In sync"
    return 0
  fi
}

# Main execution
echo "Validating governance sync..."
echo

if [[ "${CHECK_ALL}" == true ]]; then
  # Validate all known consumer repos
  total=0
  in_sync=0
  out_of_sync=0

  for repo in "${CONSUMER_REPOS[@]}"; do
    if [[ -d "${repo}" ]]; then
      total=$((total + 1))
      if validate_repo "${repo}"; then
        in_sync=$((in_sync + 1))
      else
        out_of_sync=$((out_of_sync + 1))
      fi
    else
      echo "⚠ Skipping (path not found): ${repo}"
    fi
  done

  echo
  echo "Summary:"
  echo "  Total:      ${total}"
  echo "  In sync:    ${in_sync}"
  echo "  Out of sync: ${out_of_sync}"

  if [[ ${out_of_sync} -gt 0 ]]; then
    exit 1
  fi
else
  # Validate single repo
  if validate_repo "${CONSUMER_REPO}"; then
    exit 0
  else
    exit 1
  fi
fi
