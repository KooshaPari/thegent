#!/usr/bin/env bash
# Append "See also" section to all docs/**/*.md that don't already have See also|Related|References.
# Skip docs/index.md (VitePress). Run from repo root.
set -euo pipefail
cd "$(dirname "$0")/.."
list=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  (grep -q 'See also' "$f" || grep -q 'Related' "$f" || grep -q 'References' "$f") 2>/dev/null && continue
  [ "$f" = "docs/index.md" ] && continue
  echo "$f"
done < <(find docs -name '*.md' -type f | sort) | while IFS= read -r f; do
  dir=$(dirname "$f")
  if [ "$dir" = "docs" ]; then
    subdir=""
  else
    subdir="${dir#docs/}"
  fi
  depth=0
  [ -n "$subdir" ] && depth=$(($(echo "$subdir" | tr -cd / | wc -c) + 1))
  prefix=""
  for ((i=0;i<depth;i++)); do prefix="../$prefix"; done
  base=$(basename "$f")
  if [ "$base" = "WORK_STREAM.md" ]; then
    block="

---
## See also

- [00-MASTER-INDEX.md](${prefix}plans/00-MASTER-INDEX.md) — plan index
- [RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md](${prefix}research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) — research sprawl and convert phase
"
  else
    block="

---
## See also

- [WORK_STREAM.md](${prefix}reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](${prefix}plans/00-MASTER-INDEX.md) — plan index
"
  fi
  printf '%s\n' "$block" >> "$f"
  echo "Added: $f"
done
