#!/bin/zsh
# qa-prdset-compiler.sh
# Stop hook: compile PRD-set docs into generated contract items + refresh ledger.
set -euo pipefail

INPUT="$(cat)"
CWD="$(jq -r '.cwd // empty' <<< "$INPUT")"
PROJECT_DIR="${CWD:-$(pwd)}"

if [[ ! -d "$PROJECT_DIR" ]]; then
  exit 0
fi

[[ -x "$HOME/.claude/contracts/prdset-compile.sh" ]] || exit 0

"$HOME/.claude/contracts/prdset-compile.sh" "$PROJECT_DIR" >/dev/null 2>&1 || true
"$HOME/.claude/contracts/ledger-init.sh" "$PROJECT_DIR" >/dev/null 2>&1 || true
"$HOME/.claude/contracts/dag-compile.sh" "$PROJECT_DIR" >/dev/null 2>&1 || true

echo "PRDSET COMPILER: refreshed contracts artifacts for $PROJECT_DIR"
exit 0
