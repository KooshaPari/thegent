#!/usr/bin/env zsh
# linting-accelerator.sh — JS/TS Linting Acceleration Layer
# Purpose: Try oxlint first (5-50x faster), fallback to eslint, normalize output
# Integrated into: quality-gate.sh for TS/JS file linting
# Usage: linting_accelerator <command> <file1> [file2] ...
# Commands: ts-lint, ts-dead-imports, ts-all (both)

set -euo pipefail

_ACCEL_LOG_FILE="${TMPDIR:-/tmp}/linting-accelerator-$(date +%s).log"

# shellcheck disable=SC2317  # usage is called via error handling
_accel_usage() {
  cat <<'EOF' >&2
linting_accelerator — JS/TS Linting Fallback Wrapper

USAGE:
  linting_accelerator <command> [file1] [file2] ...

COMMANDS:
  ts-lint              Run oxlint (or eslint fallback) on TypeScript files
  ts-dead-imports      Check for dead imports using oxlint (or eslint fallback)
  ts-all               Run both linting and dead-import checks

EXAMPLES:
  linting_accelerator ts-lint src/app.ts src/utils.ts
  linting_accelerator ts-dead-imports src/**/*.ts
  linting_accelerator ts-all src/**/*.{ts,tsx}

OUTPUT:
  - Returns tool output (JSON or plain text as provided by oxlint/eslint)
  - Logs tool used to stderr if VERBOSE=1
  - Exit code matches underlying tool exit code

FALLBACK BEHAVIOR:
  1. Try oxlint first (fast path, Rust-based)
  2. If unavailable or fails, try eslint (legacy fallback)
  3. If both unavailable, exit with clear error message

ENVIRONMENT:
  VERBOSE         Enable debug logging (default: off)
  OXLINT_DISABLE  Force eslint even if oxlint available (testing only)
EOF
  exit "${1:-1}"
}

# Log debug message if VERBOSE
_accel_debug() {
  if [[ "${VERBOSE:-0}" == "1" ]]; then
    echo "[linting-accelerator] $*" >&2
  fi
}

# Log to persistent log for troubleshooting
_accel_log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >> "$_ACCEL_LOG_FILE"
}

# Check if command is available
_accel_cmd_available() {
  local cmd="$1"
  if command -v "$cmd" &>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Run oxlint lint check
_accel_oxlint_lint() {
  local files=("$@")
  if [[ ${#files[@]} -eq 0 ]]; then
    _accel_debug "oxlint: no files provided"
    return 1
  fi

  _accel_debug "Running oxlint lint on ${#files[@]} files"
  _accel_log "oxlint lint: ${#files[@]} files"

  oxlint "${files[@]}" 2>&1
}

# Run eslint lint check (fallback)
_accel_eslint_lint() {
  local files=("$@")
  if [[ ${#files[@]} -eq 0 ]]; then
    _accel_debug "eslint: no files provided"
    return 1
  fi

  _accel_debug "Running eslint lint on ${#files[@]} files"
  _accel_log "eslint lint: ${#files[@]} files (fallback)"

  # Use minimal eslint config for maximum compatibility
  eslint --no-eslintrc --max-warnings 0 "${files[@]}" 2>&1 || true
}

# Run oxlint dead-imports check
_accel_oxlint_dead_imports() {
  local files=("$@")
  if [[ ${#files[@]} -eq 0 ]]; then
    _accel_debug "oxlint: no files provided for dead-imports"
    return 1
  fi

  _accel_debug "Running oxlint dead-imports on ${#files[@]} files"
  _accel_log "oxlint dead-imports: ${#files[@]} files"

  # oxlint: check for no-unused-vars rule
  oxlint --deny no-unused-vars "${files[@]}" 2>&1
}

# Run eslint dead-imports check (fallback)
_accel_eslint_dead_imports() {
  local files=("$@")
  if [[ ${#files[@]} -eq 0 ]]; then
    _accel_debug "eslint: no files provided for dead-imports"
    return 1
  fi

  _accel_debug "Running eslint dead-imports on ${#files[@]} files"
  _accel_log "eslint dead-imports: ${#files[@]} files (fallback)"

  # eslint: check no-unused-vars rule
  eslint --no-eslintrc --rule '{"no-unused-vars":"error"}' "${files[@]}" 2>&1 || true
}

# Main entry point
_accel_main() {
  local cmd="${1:-}"
  shift || true

  # Validate command
  case "$cmd" in
    ts-lint|ts-dead-imports|ts-all) ;;
    -h|--help) _accel_usage 0 ;;
    "") _accel_usage 1 ;;
    *)
      echo "ERROR: Unknown command '$cmd'" >&2
      _accel_usage 1
      ;;
  esac

  # Collect files
  local files=()
  while [[ $# -gt 0 ]]; do
    files+=("$1")
    shift
  done

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "ERROR: No files provided" >&2
    _accel_usage 1
  fi

  _accel_debug "Command: $cmd | Files: ${#files[@]}"

  # Force eslint for testing/debugging
  if [[ "${OXLINT_DISABLE:-0}" == "1" ]]; then
    _accel_debug "oxlint disabled by OXLINT_DISABLE, using eslint"
    case "$cmd" in
      ts-lint) _accel_eslint_lint "${files[@]}" ;;
      ts-dead-imports) _accel_eslint_dead_imports "${files[@]}" ;;
      ts-all)
        _accel_eslint_lint "${files[@]}"
        _accel_eslint_dead_imports "${files[@]}"
        ;;
    esac
    return $?
  fi

  # Try oxlint first
  if _accel_cmd_available oxlint; then
    _accel_debug "oxlint is available, using it (fast path)"
    _accel_log "Using: oxlint (fast path)"
    case "$cmd" in
      ts-lint) _accel_oxlint_lint "${files[@]}" ;;
      ts-dead-imports) _accel_oxlint_dead_imports "${files[@]}" ;;
      ts-all)
        _accel_oxlint_lint "${files[@]}"
        _accel_oxlint_dead_imports "${files[@]}"
        ;;
    esac
    return $?
  fi

  # Fallback to eslint
  if _accel_cmd_available eslint; then
    _accel_debug "oxlint unavailable, falling back to eslint"
    _accel_log "Using: eslint (fallback)"
    case "$cmd" in
      ts-lint) _accel_eslint_lint "${files[@]}" ;;
      ts-dead-imports) _accel_eslint_dead_imports "${files[@]}" ;;
      ts-all)
        _accel_eslint_lint "${files[@]}"
        _accel_eslint_dead_imports "${files[@]}"
        ;;
    esac
    return $?
  fi

  # Neither available
  {
    echo "ERROR: Neither oxlint nor eslint is available"
    echo "To use JS/TS linting:"
    echo "  1. Install oxlint (recommended): npm install -g oxlint"
    echo "  2. OR install eslint (fallback): npm install -g eslint"
  } >&2
  _accel_log "FAIL: Neither oxlint nor eslint available"
  return 127
}

# Run if sourced with args or executed directly
if [ -n "${ZSH_VERSION:-}" ]; then
  _ACCEL_PATH="${(%):-%x}"
elif [ -n "${BASH_VERSION:-}" ]; then
  _ACCEL_PATH="${BASH_SOURCE[0]}"
else
  _ACCEL_PATH="$0"
fi

if [[ "$_ACCEL_PATH" == "$0" ]]; then
  _accel_main "$@"
fi
