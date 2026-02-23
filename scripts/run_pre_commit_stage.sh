#!/usr/bin/env bash

set -euo pipefail

STAGE="${1:?Usage: $0 <pre-commit|pre-push>}"
case "$STAGE" in
  pre-commit|pre-push)
    ;;
  *)
    echo "Unsupported pre-commit stage: $STAGE" >&2
    exit 1
    ;;
esac

run_scope="${THEGENT_PRE_COMMIT_SCOPE:-changed}"
if [[ "$run_scope" == "full" || "${THEGENT_PRE_COMMIT_FULL:-0}" == "1" ]]; then
  exec uv run pre-commit run --all-files --hook-stage "$STAGE"
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

raw_candidates="$(mktemp)"
uniq_candidates="$(mktemp)"
trap 'rm -f "$raw_candidates" "$uniq_candidates"' EXIT

if [ -n "${THEGENT_PRE_COMMIT_FILES:-}" ]; then
  printf '%s\n' "$THEGENT_PRE_COMMIT_FILES" > "$raw_candidates"
else
  if [ "$STAGE" = "pre-commit" ]; then
    git diff --cached --name-only > "$raw_candidates"
  else
    base_ref="${THEGENT_PRE_PUSH_BASE_REF:-origin/main}"
    if git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
      merge_base="$(git merge-base HEAD "$base_ref")"
      git diff --name-only "${merge_base}..HEAD" > "$raw_candidates"
    else
      git diff --cached --name-only > "$raw_candidates"
    fi
  fi
fi

awk 'NF { if (!seen[$0]++) print }' "$raw_candidates" > "$uniq_candidates"

uniq_files=()
while IFS= read -r candidate; do
  [ -n "$candidate" ] || continue
  uniq_files+=("$candidate")
done < "$uniq_candidates"

if [ "${#uniq_files[@]}" -eq 0 ]; then
  echo "No files detected for pre-commit stage '$STAGE'; skipping."
  exit 0
fi

uv run pre-commit run --hook-stage "$STAGE" --files "${uniq_files[@]}"
