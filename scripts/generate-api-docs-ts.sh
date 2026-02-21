#!/usr/bin/env bash
# Generate TypeScript API documentation using TypeDoc, output to docs/site/api.
# Scans the project for .ts files (excluding node_modules, .shadow-DEL-* directories,
# and test/spec files) and fails loudly if none are found or if typedoc is missing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/docs/site/api"

echo "Scanning for TypeScript source files in ${PROJECT_ROOT}..."

# Collect .ts files, excluding node_modules, shadow dirs, test files, and config files.
mapfile -t TS_FILES < <(find "${PROJECT_ROOT}" \
  -name "*.ts" \
  -not -path "*/node_modules/*" \
  -not -path "*/.shadow-DEL-*/*" \
  -not -name "*.spec.ts" \
  -not -name "*.test.ts" \
  -not -name "playwright.config.ts" \
  -not -name "vitest.config.ts" \
  2>/dev/null || true)

if [[ ${#TS_FILES[@]} -eq 0 ]]; then
  echo "No TypeScript source files found — skipping TypeDoc generation."
  exit 0
fi

echo "Found ${#TS_FILES[@]} TypeScript file(s)."

if ! command -v typedoc &>/dev/null; then
  echo "ERROR: typedoc is not installed or not in PATH." >&2
  echo "Install it with: npm install -g typedoc  or add it to docs/site/package.json devDependencies" >&2
  exit 1
fi

echo "Generating TypeDoc output to ${OUTPUT_DIR}..."

typedoc \
  --out "${OUTPUT_DIR}" \
  --name "thegent API Reference" \
  --includeVersion \
  --readme none \
  "${TS_FILES[@]}"

echo "TypeDoc generation complete: ${OUTPUT_DIR}"
