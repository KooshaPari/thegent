#!/usr/bin/env bash
# Audit docs/**/*.md for convert phase: H1, frontmatter, See also/Related.
# See: docs/research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md §5.2
set -euo pipefail
DOCS_DIR="${1:-docs}"
echo "=== Docs convert audit: $DOCS_DIR ==="
total=0
has_h1=0
has_fm=0
has_see=0
missing_h1=""
missing_fm=""
missing_see=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  total=$((total + 1))
  h1=0
  fm=0
  see=0
  head -20 "$f" | grep -q '^# ' && h1=1
  head -1 "$f" | grep -q '^---$' && fm=1
  (grep -q 'See also' "$f" || grep -q 'Related' "$f" || grep -q 'References' "$f") 2>/dev/null && see=1
  [ "$h1" -eq 1 ] && has_h1=$((has_h1 + 1)) || missing_h1="$missing_h1  $f\n"
  [ "$fm" -eq 1 ] && has_fm=$((has_fm + 1)) || missing_fm="$missing_fm  $f\n"
  [ "$see" -eq 1 ] && has_see=$((has_see + 1)) || missing_see="$missing_see  $f\n"
done < <(find "$DOCS_DIR" -name '*.md' -type f 2>/dev/null | sort)
echo "Total .md: $total"
echo "Has H1:   $has_h1"
echo "Has frontmatter (---): $has_fm"
echo "Has See also/Related/References: $has_see"
echo ""
if [ -n "$missing_h1" ]; then
  echo "--- Missing H1 (first 20) ---"
  echo -e "$missing_h1" | head -20
fi
if [ -n "$missing_see" ]; then
  echo "--- Missing See also/Related (first 20) ---"
  echo -e "$missing_see" | head -20
fi
echo ""
echo "By directory:"
find "$DOCS_DIR" -name '*.md' -type f 2>/dev/null | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn
echo "Done. Add 'See also' to missing_see files; add frontmatter where needed."
