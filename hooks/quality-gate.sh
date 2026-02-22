#!/usr/bin/env bash
# Rust-backed quality gate wrapper.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if command -v thegent-hooks >/dev/null 2>&1; then
    BIN_PATH="$(command -v thegent-hooks)"
elif [[ -x "${REPO_ROOT}/hooks/bin/thegent-hooks" ]]; then
    BIN_PATH="${REPO_ROOT}/hooks/bin/thegent-hooks"
else
    echo "quality-gate: thegent-hooks runtime not found; install/compile the Rust runtime first" >&2
    exit 1
fi

changed_files=()
for arg in "$@"; do
    [[ -f "$arg" ]] || continue
    if [[ "$arg" == "$REPO_ROOT/"* ]]; then
        changed_files+=("${arg#"$REPO_ROOT/"}")
    else
        changed_files+=("$arg")
    fi
done
if ((${#changed_files[@]} > 0)); then
    CHANGED_FILES="$(printf '%s\n' "${changed_files[@]}")"
    export CHANGED_FILES
fi
export PROJECT_DIR="$REPO_ROOT"

exec "$BIN_PATH" quality-gate
