#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -n "${PRE_COMMIT_FROM_REF-}" ] && [ -n "${PRE_COMMIT_TO_REF-}" ]; then
  STAGE="pre-push"
  CHANGED_FILES_CMD=(git diff --name-only "$PRE_COMMIT_FROM_REF" "$PRE_COMMIT_TO_REF")
else
  STAGE="pre-commit"
  CHANGED_FILES_CMD=(git diff --cached --name-only --diff-filter=ACM)
fi

if command -v ggshield >/dev/null 2>&1; then
  GGSHIELD=(ggshield)
elif command -v uvx >/dev/null 2>&1; then
  GGSHIELD=(uvx ggshield)
elif command -v uv >/dev/null 2>&1; then
  GGSHIELD=(uv tool run ggshield)
else
  echo "ERROR: ggshield not installed. Install with: pipx install ggshield or uv tool install ggshield" >&2
  exit 1
fi

echo "[security-guard] Running ggshield secret scan for $STAGE"
if [ "$STAGE" = "pre-push" ]; then
  "${GGSHIELD[@]}" secret scan pre-push --from-ref "$PRE_COMMIT_FROM_REF" --to-ref "$PRE_COMMIT_TO_REF"
else
  echo "[security-guard] Running ggshield secret scan"
  "${GGSHIELD[@]}" secret scan pre-commit
fi

changed_files=$(
  if [ "${CHANGED_FILES_CMD[0]}" = "git" ]; then
    "${CHANGED_FILES_CMD[@]}" 2>/dev/null || true
  else
    printf ""
  fi
)

if [ -z "${changed_files}" ] && [ "$STAGE" = "pre-commit" ]; then
  changed_files=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || true)
fi

if command -v codespell >/dev/null 2>&1; then
  if [ -n "${changed_files}" ]; then
    echo "[security-guard] Running optional codespell fast pass"
    while IFS= read -r changed_file; do
      case "$changed_file" in
        *.md|*.txt|*.py|*.ts|*.tsx|*.js|*.go|*.rs|*.kt|*.java|*.yaml|*.yml)
          codespell -q 2 -L "hte,teh" "$changed_file" || true
          ;;
        *)
          ;;
      esac
    done <<< "${changed_files}"
  fi
fi
