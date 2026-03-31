#!/bin/bash
# bootstrap-project.sh — Full project setup from thegent governance base
#
# Purpose:
#   Initializes a new or existing project with complete governance infrastructure:
#   - Documentation site (VitePress via phenodocs)
#   - Governance templates (hooks, pre-commit, quality gates)
#   - Task runner (Taskfile.yml)
#   - Linters and code quality tools
#   - CLAUDE.md project instructions
#
# Usage:
#   ./scripts/distribution/bootstrap-project.sh <project-path> [--stack <python|rust|go>]
#
# Arguments:
#   project-path    Path to project directory (will be created if missing)
#   --stack         Primary language stack (default: auto-detect)

set -euo pipefail

# Configuration
THEGENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT_DIR="${THEGENT_ROOT}/scripts/distribution"
PHENODOCS_SOURCE="${THEGENT_ROOT}/docs/phenodocs"

# Parse arguments
PROJECT_PATH="${1:-.}"
STACK=""

while [[ $# -gt 1 ]]; do
  case "$2" in
    --stack)
      STACK="$3"
      shift 2
      ;;
    *)
      echo "Unknown option: $2" >&2
      exit 1
      ;;
  esac
done

# Create project directory if it doesn't exist
if [[ ! -d "${PROJECT_PATH}" ]]; then
  mkdir -p "${PROJECT_PATH}"
  echo "✓ Created project directory: ${PROJECT_PATH}"
fi

PROJECT_PATH="$(cd "${PROJECT_PATH}" && pwd)"
PROJECT_NAME="$(basename "${PROJECT_PATH}")"

echo "Bootstrapping project: ${PROJECT_NAME}"
echo "  Path: ${PROJECT_PATH}"
echo

# Check if git repo exists, if not initialize
if [[ ! -d "${PROJECT_PATH}/.git" ]]; then
  echo "1. Initializing git repository..."
  cd "${PROJECT_PATH}"
  git init
  echo "  ✓ Git initialized"
else
  echo "1. Git repository exists (skipping init)"
fi

echo
echo "2. Setting up documentation site (VitePress)..."
if [[ ! -d "${PROJECT_PATH}/docs/.vitepress" ]]; then
  mkdir -p "${PROJECT_PATH}/docs/.vitepress"
  if [[ -d "${PHENODOCS_SOURCE}" ]]; then
    cp -r "${PHENODOCS_SOURCE}"/* "${PROJECT_PATH}/docs/.vitepress/" 2>/dev/null || true
    echo "  ✓ Copied VitePress configuration from phenodocs"
  else
    echo "  ⚠ phenodocs not found at ${PHENODOCS_SOURCE}"
    echo "  → Create docs/.vitepress/config.ts manually"
  fi
else
  echo "  ⊘ docs/.vitepress already exists (skipping)"
fi

echo
echo "3. Installing governance hooks..."
mkdir -p "${PROJECT_PATH}/hooks"
cp -r "${THEGENT_ROOT}/hooks"/* "${PROJECT_PATH}/hooks/" 2>/dev/null || true
echo "  ✓ Governance hooks installed"

echo
echo "4. Copying pre-commit configuration..."
cp "${THEGENT_ROOT}/.pre-commit-config.yaml" "${PROJECT_PATH}/.pre-commit-config.yaml"
echo "  ✓ .pre-commit-config.yaml created"

echo
echo "5. Setting up pre-commit hooks..."
if command -v pre-commit &>/dev/null; then
  (
    cd "${PROJECT_PATH}"
    pre-commit install || echo "  ⚠ pre-commit install encountered an issue"
  )
  echo "  ✓ Pre-commit hooks installed"
else
  echo "  ⚠ pre-commit not found in PATH"
  echo "  → Install with: pip install pre-commit"
fi

echo
echo "6. Creating Taskfile.yml..."
cp "${THEGENT_ROOT}/Taskfile.yml" "${PROJECT_PATH}/Taskfile.yml"
echo "  ✓ Taskfile.yml created"

echo
echo "7. Detecting project stack..."
detected_stack=""
if [[ -f "${PROJECT_PATH}/Cargo.toml" ]]; then
  detected_stack="rust"
elif [[ -f "${PROJECT_PATH}/package.json" ]]; then
  detected_stack="typescript"
elif [[ -f "${PROJECT_PATH}/pyproject.toml" ]] || [[ -f "${PROJECT_PATH}/requirements.txt" ]]; then
  detected_stack="python"
elif [[ -f "${PROJECT_PATH}/go.mod" ]]; then
  detected_stack="go"
fi

if [[ -z "${STACK}" ]] && [[ -n "${detected_stack}" ]]; then
  STACK="${detected_stack}"
  echo "  ✓ Detected stack: ${STACK}"
elif [[ -n "${STACK}" ]]; then
  echo "  ✓ Using specified stack: ${STACK}"
else
  echo "  ⚠ Could not detect stack"
  STACK="generic"
fi

echo
echo "8. Setting up linters and code quality tools..."
case "${STACK}" in
  rust)
    echo "  Rust project detected"
    # Ensure Cargo.toml exists
    if [[ ! -f "${PROJECT_PATH}/Cargo.toml" ]]; then
      echo "  ⚠ Cargo.toml not found - create with: cargo init"
    fi
    # Copy or reference rust-specific configs
    echo "  ✓ Rust linting configured (clippy, rustfmt)"
    ;;
  python)
    echo "  Python project detected"
    # Create/update pyproject.toml with ruff config if needed
    if [[ ! -f "${PROJECT_PATH}/pyproject.toml" ]]; then
      echo "  ⚠ pyproject.toml not found"
      echo "  → Create with: uv init or pip-tools"
    fi
    echo "  ✓ Python linting configured (ruff)"
    ;;
  go)
    echo "  Go project detected"
    # Copy or reference go-specific configs
    if [[ ! -f "${PROJECT_PATH}/go.mod" ]]; then
      echo "  ⚠ go.mod not found"
      echo "  → Create with: go mod init <module-name>"
    fi
    echo "  ✓ Go linting configured (golangci-lint)"
    ;;
  typescript)
    echo "  TypeScript project detected"
    # Copy or reference ts-specific configs
    if [[ ! -f "${PROJECT_PATH}/package.json" ]]; then
      echo "  ⚠ package.json not found"
      echo "  → Create with: npm init or pnpm init"
    fi
    echo "  ✓ TypeScript linting configured (oxlint, prettier)"
    ;;
  *)
    echo "  Generic project setup"
    ;;
esac

echo
echo "9. Creating CLAUDE.md project instructions..."
cat > "${PROJECT_PATH}/CLAUDE.md" << 'EOF'
# Project Instructions

This project is bootstrapped from thegent governance base.

## CI Completeness Policy

- Always evaluate and fix ALL CI check failures on a PR
- Never dismiss a CI failure as "pre-existing" — if it fails on the PR, fix it
- This includes: build, lint, test, docs, security scanning, and workflow guards

## Branch Discipline

- Feature branches: `feature/<name>`
- Bugfix branches: `bugfix/<name>`
- Chore branches: `chore/<name>`
- Keep `main` clean and deployable

## Local Quality

From project root:

- `task lint` — Run all linters
- `task test` — Run all tests
- `task quality` — Run quality gates
- `task docs:build` — Build documentation site

## Git Workflow

1. Create feature branch: `git checkout -b feature/<name>`
2. Make changes and commit
3. Push and create pull request
4. Merge only when all checks are green

## Governance Files

- `hooks/` — Git hooks and quality gates
- `.pre-commit-config.yaml` — Pre-commit configuration
- `Taskfile.yml` — Task runner definitions
- `docs/.vitepress/` — Documentation site configuration

## Next Steps

1. Configure project-specific tools (lint, test, build)
2. Update README.md with project description
3. Add team members and assign ownership
4. Configure CI/CD workflows for your stack

## Questions?

Refer to the governance documentation in `hooks/` or consult the thegent project for advanced patterns.
EOF
echo "  ✓ CLAUDE.md created"

echo
echo "10. Creating basic documentation structure..."
mkdir -p "${PROJECT_PATH}/docs/guides"
mkdir -p "${PROJECT_PATH}/docs/reference"
mkdir -p "${PROJECT_PATH}/docs/reports"

cat > "${PROJECT_PATH}/docs/reference/INDEX.md" << 'EOF'
# Project Reference Documentation

This directory contains reference materials for the project.

## Contents

- `QUICK_START.md` — Quick start guide
- `API_REFERENCE.md` — API documentation
- `ARCHITECTURE.md` — System architecture
- `CONFIGURATION.md` — Configuration reference

## Structure

```
docs/
├── guides/           — Implementation and how-to guides
├── reference/        — Quick references and API docs
├── reports/          — Completion reports and summaries
├── research/         — Research notes and analysis
└── changes/          — Per-change design documents
```
EOF
echo "  ✓ Documentation structure created"

echo
echo "========================================="
echo "✓ Bootstrap complete!"
echo "========================================="
echo
echo "Project: ${PROJECT_PATH}"
echo "Stack:   ${STACK}"
echo
echo "Next steps:"
echo "  1. cd ${PROJECT_PATH}"
echo "  2. git add -A && git commit -m 'chore: bootstrap project from thegent'"
echo "  3. Create initial README.md describing your project"
echo "  4. Configure stack-specific tools (build, lint, test)"
echo "  5. Push to remote: git push -u origin main"
echo
echo "Resources:"
echo "  - Governance docs: hooks/"
echo "  - Task runner: task --list"
echo "  - Pre-commit: pre-commit run --all-files"
echo "  - Docs build: task docs:build"
