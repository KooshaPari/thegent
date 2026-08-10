#!/usr/bin/env bash
# scripts/check_makefile_invariants.sh
#
# Makefile self-test for L2 Dev Loop + L30 Onboarding.
#
# Invariants enforced:
#   1. Every target declared in the leading `.PHONY` line exists in the body.
#   2. Every public (non-internal) target carries a `## <description>` docstring.
#   3. No target uses `sudo`, `rm -rf /`, `mkfs`, `dd`, or `shutdown` (safety rails).
#   4. The `help` target uses the canonical `awk` pattern so `make help` lists everything.
#   5. Every `task_if` call passes a non-empty task name and uv fallback.
#
# Exits 0 on success, 1 on the first violation.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAKEFILE="$ROOT/Makefile"

if [ ! -f "$MAKEFILE" ]; then
  echo "FAIL: Makefile not found at $MAKEFILE" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "ok   : $*"; }

# ---------------------------------------------------------------------------
# 1. Every .PHONY target must exist as a body rule.
# ---------------------------------------------------------------------------
# The .PHONY declaration may span multiple lines via backslash continuations.
# Use Python (always available) for a robust multi-line parse.
phony_targets="$(python3 - "$MAKEFILE" <<'PYEOF'
import re, sys
text = open(sys.argv[1]).read()
m = re.search(r"^\.PHONY:\s*(.+?)(?=^\S|\Z)", text, re.DOTALL | re.MULTILINE)
if not m:
    sys.exit(2)
block = m.group(1)
# Collapse backslash-newline continuations and all whitespace.
clean = re.sub(r"\\\s*\n\s*", " ", block)
tokens = [t for t in clean.split() if t and re.match(r"^[A-Za-z0-9_-]+$", t)]
print(" ".join(tokens))
PYEOF
)"
[ -n "$phony_targets" ] || fail ".PHONY list is empty or unparseable"

missing=0
for target in $phony_targets; do
  # A body rule is `^<target>:` at column 0.
  if ! grep -qE "^${target}:" "$MAKEFILE"; then
    echo "  missing body rule for .PHONY target: $target" >&2
    missing=1
  fi
done
[ "$missing" -eq 0 ] || fail "one or more .PHONY targets have no body rule"
ok "all .PHONY targets have body rules"

# ---------------------------------------------------------------------------
# 2. Every public target must carry `## <description>` after the colon.
# ---------------------------------------------------------------------------
undocumented=0
for target in $phony_targets; do
  # Skip internal-only targets (helpers starting with underscore or template literal).
  case "$target" in
    _*) continue ;;
  esac
  if ! grep -qE "^${target}:.*##[[:space:]]" "$MAKEFILE"; then
    echo "  undocumented public target: $target" >&2
    undocumented=1
  fi
done
[ "$undocumented" -eq 0 ] || fail "one or more public targets lack '##' docstring"
ok "all public targets are documented"

# ---------------------------------------------------------------------------
# 3. Safety rails — no dangerous shell commands anywhere in the Makefile.
# ---------------------------------------------------------------------------
forbidden_patterns=( 'sudo ' 'rm[[:space:]]+-rf[[:space:]]+/' 'mkfs' 'dd[[:space:]]+if=' 'shutdown' 'reboot' ':(){:|:&};:' )
for pat in "${forbidden_patterns[@]}"; do
  if grep -qE "$pat" "$MAKEFILE"; then
    fail "forbidden shell pattern detected: $pat"
  fi
done
ok "no forbidden shell patterns"

# ---------------------------------------------------------------------------
# 4. `help` target uses the canonical awk pattern.
# ---------------------------------------------------------------------------
if ! grep -qE 'awk .*FS.*:.*##.*printf' "$MAKEFILE"; then
  fail "help target missing canonical awk pattern (FS = ':.*?## ')"
fi
ok "help target uses canonical awk pattern"

# ---------------------------------------------------------------------------
# 5. Every `task_if` call passes two non-empty arguments.
# ---------------------------------------------------------------------------
bad_task_if=0
# Match lines like `$(call task_if,<name>,<fallback>)` and ensure both are non-empty.
while IFS= read -r line; do
  body="${line#*task_if,}"
  name="${body%%,*}"
  rest="${body#*,}"
  fallback="${rest%)*}"
  if [ -z "$name" ] || [ -z "$fallback" ]; then
    echo "  task_if call missing argument: $line" >&2
    bad_task_if=1
  fi
done < <(grep -E 'task_if,' "$MAKEFILE" || true)
[ "$bad_task_if" -eq 0 ] || fail "one or more task_if calls have empty arguments"
ok "every task_if call has both arguments"

# ---------------------------------------------------------------------------
# 6. `make help` must list every public target.
# ---------------------------------------------------------------------------
help_output="$(make help 2>/dev/null || true)"
[ -n "$help_output" ] || fail "make help produced no output"
# Strip ANSI color codes (the help target wraps each target in cyan).
help_plain="$(printf '%s\n' "$help_output" | sed -E 's/\x1b\[[0-9;]*[A-Za-z]//g')"
undocumented=0
for target in $phony_targets; do
  case "$target" in
    _*) continue ;;
  esac
  # `make help` prints lines like "  install            <doc>"; match the bare target
  # with leading whitespace, then either ANSI-then-padding or padding alone.
  pattern="^[[:space:]]+(\x1b\\[[0-9;]*m)?${target}([[:space:]]|\\x1b)"
  if ! printf '%s\n' "$help_plain" | grep -qE "$pattern"; then
    echo "  help output missing target: $target" >&2
    undocumented=1
  fi
done
[ "$undocumented" -eq 0 ] || fail "make help does not list every public target"
ok "make help lists every public target"

echo
echo "PASS: Makefile pass-through invariants hold."
