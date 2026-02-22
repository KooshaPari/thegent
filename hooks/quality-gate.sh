#!/usr/bin/env bash
# Rust-backed quality gate wrapper.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

run_local_pre_commit() {
  if command -v uv >/dev/null 2>&1; then
    uv run pre-commit run
    return 0
  fi
  if ! command -v pre-commit >/dev/null 2>&1; then
    echo "quality-gate: pre-commit is required for local hook emulation but is not installed" >&2
    exit 1
  fi
  pre-commit run
}

run_local_pre_push() {
  if ! command -v bash >/dev/null 2>&1; then
    echo "quality-gate: bash is required for local pre-push emulation" >&2
    exit 1
  fi
  if ! command -v task >/dev/null 2>&1; then
    echo "quality-gate: task is required for local pre-push emulation but is not installed" >&2
    exit 1
  fi
  export THEGENT_HOOK_PROFILE="pre-push"
  THEGENT_HOOK_PROFILE=pre-push bash scripts/ci-local-emulator.sh
}

resolve_rust_gate() {
  if command -v thegent-hooks >/dev/null 2>&1; then
    BIN_PATH="$(command -v thegent-hooks)"
  elif [[ -x "${REPO_ROOT}/hooks/bin/thegent-hooks" ]]; then
    BIN_PATH="${REPO_ROOT}/hooks/bin/thegent-hooks"
  else
    echo "quality-gate: thegent-hooks runtime not found; install/compile the Rust runtime first" >&2
    exit 1
  fi
}

HOOK_PROFILE="${THEGENT_HOOK_PROFILE:-}"

if [[ "$HOOK_PROFILE" == "pre-commit" ]]; then
  run_local_pre_commit
  exit 0
fi

if [[ "$HOOK_PROFILE" == "pre-push" ]]; then
  run_local_pre_push
  exit 0
fi

if [[ "$#" -ge 2 && "${1:-}" == "origin" ]]; then
  run_local_pre_push
  exit 0
fi

resolve_rust_gate

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
