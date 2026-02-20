#!/usr/bin/env bash
# shell-audit.sh — Audit Zsh / shell configuration files in thegent.
#
# Usage:
#   scripts/shell-audit.sh [--dir DIR ...] [--output-consolidated PATH] [--json]
#
# Options:
#   --dir DIR               Directory to search (may be repeated; default: shell/ scripts/ hooks/)
#   --output-consolidated   Write the consolidated script to PATH instead of stdout
#   --json                  Print audit results as JSON (requires python3)
#   -h, --help              Show this help text
#
# Exit codes:
#   0  No issues found
#   1  Issues found (duplicates or sourcing problems)
#   2  Usage error or Python unavailable

set -euo pipefail

# ──────────────────────────────────────────────
# Defaults
# ──────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEARCH_DIRS=()
OUTPUT_CONSOLIDATED=""
JSON_MODE=0

# ──────────────────────────────────────────────
# Argument parsing
# ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)
      SEARCH_DIRS+=("$2")
      shift 2
      ;;
    --output-consolidated)
      OUTPUT_CONSOLIDATED="$2"
      shift 2
      ;;
    --json)
      JSON_MODE=1
      shift
      ;;
    -h|--help)
      sed -n '2,/^$/p' "$0" | sed 's/^# //' | sed 's/^#//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

# Default search directories
if [[ ${#SEARCH_DIRS[@]} -eq 0 ]]; then
  for d in shell scripts hooks; do
    [[ -d "$REPO_ROOT/$d" ]] && SEARCH_DIRS+=("$REPO_ROOT/$d")
  done
fi

# ──────────────────────────────────────────────
# Ensure Python 3 is available
# ──────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 is required but not found in PATH" >&2
  exit 2
fi

# ──────────────────────────────────────────────
# Run audit via Python module
# ──────────────────────────────────────────────
PYTHON_SCRIPT="$(cat <<'PYEOF'
import json
import sys
from pathlib import Path

# Add project src to path
repo_root = Path(sys.argv[1])
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from thegent.tools.shell_config import ShellConfigAuditor

search_dirs = [Path(d) for d in sys.argv[2:] if Path(d).is_dir()]
auditor = ShellConfigAuditor()
configs = auditor.audit(search_dirs)

duplicates = auditor.find_duplicates(configs)
alias_dupes = auditor.find_duplicate_aliases(configs)
issues = auditor.check_sourcing_order(configs)
graph = auditor.sourcing_graph(configs)

result = {
    "files_found": len(configs),
    "files": [str(c.path) for c in configs],
    "function_counts": {str(c.path): len(c.functions) for c in configs},
    "alias_counts": {str(c.path): len(c.aliases) for c in configs},
    "duplicate_functions": {k: [str(p) for p in v] for k, v in duplicates.items()},
    "duplicate_aliases": {k: [str(p) for p in v] for k, v in alias_dupes.items()},
    "sourcing_issues": issues,
    "sourcing_graph": graph,
}

print(json.dumps(result, indent=2))
PYEOF
)"

RAW_JSON="$(python3 -c "$PYTHON_SCRIPT" "$REPO_ROOT" "${SEARCH_DIRS[@]}")"

if [[ $JSON_MODE -eq 1 ]]; then
  echo "$RAW_JSON"
  exit 0
fi

# ──────────────────────────────────────────────
# Human-readable report
# ──────────────────────────────────────────────
FILES_FOUND="$(echo "$RAW_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['files_found'])")"
ISSUE_COUNT="$(echo "$RAW_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['duplicate_functions'])+len(d['sourcing_issues']))")"

echo "====================================================="
echo " thegent Shell Config Audit"
echo "====================================================="
echo " Search dirs: ${SEARCH_DIRS[*]}"
echo " Files found: $FILES_FOUND"
echo "====================================================="
echo ""

# List files
echo "--- Discovered Files ---"
echo "$RAW_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for f in d['files']:
    funcs = d['function_counts'].get(f, 0)
    aliases = d['alias_counts'].get(f, 0)
    print(f'  {f}  ({funcs} functions, {aliases} aliases)')
"
echo ""

# Duplicate functions
DUPES="$(echo "$RAW_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
dupes = d['duplicate_functions']
if dupes:
    print('--- Duplicate Function Definitions ---')
    for name, paths in dupes.items():
        print(f'  {name}:')
        for p in paths:
            print(f'    {p}')
else:
    print('--- No duplicate function definitions found ---')
")"
echo "$DUPES"
echo ""

# Duplicate aliases
ALIAS_DUPES="$(echo "$RAW_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
dupes = d['duplicate_aliases']
if dupes:
    print('--- Duplicate Alias Definitions ---')
    for name, paths in dupes.items():
        print(f'  {name}:')
        for p in paths:
            print(f'    {p}')
else:
    print('--- No duplicate alias definitions found ---')
")"
echo "$ALIAS_DUPES"
echo ""

# Sourcing graph
echo "--- Sourcing Graph ---"
echo "$RAW_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
graph = d['sourcing_graph']
if graph:
    for fname, sources in graph.items():
        print(f'  {fname}:')
        for s in sources:
            print(f'    -> {s}')
else:
    print('  (no sourcing relationships detected)')
"
echo ""

# Issues
ISSUES="$(echo "$RAW_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
issues = d['sourcing_issues']
if issues:
    print('--- Sourcing Issues ---')
    for issue in issues:
        print(f'  [WARN] {issue}')
else:
    print('--- No sourcing issues found ---')
")"
echo "$ISSUES"
echo ""

# Consolidated output
if [[ -n "$OUTPUT_CONSOLIDATED" ]]; then
  echo "--- Generating Consolidated Config -> $OUTPUT_CONSOLIDATED ---"
  python3 -c "
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
src_path = repo_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from thegent.tools.shell_config import ShellConfigAuditor
search_dirs = [Path(d) for d in sys.argv[2:] if Path(d).is_dir()]
auditor = ShellConfigAuditor()
configs = auditor.audit(search_dirs)
merged = auditor.generate_consolidated(configs)
Path(sys.argv[0]).write_text(merged, encoding='utf-8')
" "$OUTPUT_CONSOLIDATED" "$REPO_ROOT" "${SEARCH_DIRS[@]}"
  echo "  Written: $OUTPUT_CONSOLIDATED"
  echo ""
fi

echo "====================================================="
if [[ "$ISSUE_COUNT" -gt 0 ]]; then
  echo " RESULT: $ISSUE_COUNT issue(s) found"
  echo "====================================================="
  exit 1
else
  echo " RESULT: Clean — no issues found"
  echo "====================================================="
  exit 0
fi
