#!/usr/bin/env bash
# lint-fast.sh -- Run oxlint then ESLint on the given paths.
#
# Usage:
#   scripts/lint-fast.sh [paths...]
#   scripts/lint-fast.sh src/ web/
#
# Behaviour:
#   1. Run oxlint (50-100x faster than ESLint) on all paths.
#      If oxlint exits non-zero, print diagnostics and continue.
#   2. Run eslint on all paths.
#      Exit with the combined error status.
#
# Environment:
#   OXLINT_CONFIG  -- path to oxlintrc.json (default: auto-detect)
#   ESLINT_CONFIG  -- path to ESLint config  (default: auto-detect)
#
# Exit codes:
#   0  -- both linters passed
#   1  -- one or both linters reported errors

set -euo pipefail

OXLINT_ARGS=()
ESLINT_ARGS=()

if [[ -n "${OXLINT_CONFIG:-}" ]]; then
    OXLINT_ARGS+=("--config" "${OXLINT_CONFIG}")
fi

if [[ -n "${ESLINT_CONFIG:-}" ]]; then
    ESLINT_ARGS+=("--config" "${ESLINT_CONFIG}")
fi

OXLINT_EXIT=0
ESLINT_EXIT=0

# ---- oxlint ----------------------------------------------------------------
if command -v oxlint &>/dev/null; then
    echo "[lint-fast] Running oxlint..."
    oxlint "${OXLINT_ARGS[@]}" "$@" || OXLINT_EXIT=$?
    if [[ "${OXLINT_EXIT}" -ne 0 ]]; then
        echo "[lint-fast] oxlint reported issues (exit ${OXLINT_EXIT})"
    else
        echo "[lint-fast] oxlint: clean"
    fi
else
    echo "[lint-fast] WARNING: oxlint not found; skipping fast pre-filter." >&2
fi

# ---- eslint ----------------------------------------------------------------
if command -v eslint &>/dev/null; then
    echo "[lint-fast] Running eslint..."
    eslint "${ESLINT_ARGS[@]}" "$@" || ESLINT_EXIT=$?
    if [[ "${ESLINT_EXIT}" -ne 0 ]]; then
        echo "[lint-fast] eslint reported issues (exit ${ESLINT_EXIT})"
    else
        echo "[lint-fast] eslint: clean"
    fi
else
    echo "[lint-fast] WARNING: eslint not found; skipping." >&2
fi

# Combined exit: non-zero if either linter failed
if [[ "${OXLINT_EXIT}" -ne 0 || "${ESLINT_EXIT}" -ne 0 ]]; then
    exit 1
fi

exit 0
