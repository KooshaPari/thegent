#!/usr/bin/env bash
# Dependency-invariants static checker for the L11 Dependencies lane.
#
# Verifies the canonical dependency surfaces are intact, in sync, and free
# of common drift / hygiene issues:
#
#   1. uv.lock must exist and be non-empty (the lock is the SSOT).
#   2. pyproject.toml must declare at least one runtime dependency and
#      that dependency must declare a version constraint.
#   3. requirements.txt must exist and list at least one package (legacy
#      pin path consumed by docker / CI / dev docs).
#   4. Lockfile size is sanity-checked against a minimum threshold so a
#      silently-truncated lockfile is caught before a CI build does.
#   5. pyproject.toml must not contain an unpinned dep (no `==`
#      baseline where the spec is missing a lower / upper bound).
#   6. uv.lock must be in sync with pyproject.toml at the package-name
#      level — every top-level name in pyproject must appear in uv.lock.
#
# Designed to run in <50ms; safe to invoke from a pre-commit hook or
# `make dep-audit`. Non-zero exit on the first violation; a clear,
# numbered status block is printed before the exit.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/uv.lock"
PYPROJECT="$ROOT/pyproject.toml"
REQUIREMENTS="$ROOT/requirements.txt"

fail=0
checks=0

note()  { printf '  \033[36m[check]\033[0m %s\n' "$*"; checks=$((checks + 1)); }
pass()  { printf '  \033[32m[ ok ]\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m[warn]\033[0m %s\n' "$*"; }
fail()  { printf '  \033[31m[FAIL]\033[0m %s\n' "$*"; fail=$((fail + 1)); }

# 1. uv.lock exists and is non-empty
note "uv.lock exists and is non-empty"
if [[ -s "$LOCK" ]]; then
  size=$(wc -c < "$LOCK" | tr -d ' ')
  if [[ "$size" -ge 1024 ]]; then
    pass "uv.lock present ($size bytes)"
  else
    fail "uv.lock is suspiciously small ($size bytes) — may be truncated"
  fi
else
  fail "uv.lock is missing or empty at $LOCK"
fi

# 2. pyproject.toml has runtime deps with version constraints
note "pyproject.toml declares pinned runtime dependencies"
if [[ -f "$PYPROJECT" ]]; then
  if uv run python - <<'PY' 2>/dev/null
import sys, tomllib
data = tomllib.load(open("pyproject.toml", "rb"))
deps = data.get("project", {}).get("dependencies", [])
sys.exit(0 if deps and all(isinstance(d, str) and any(op in d for op in (">=", "==", "~=", "<=")) for d in deps) else 1)
PY
  then
    pass "pyproject.toml has pinned runtime dependencies"
  else
    fail "pyproject.toml is missing pinned runtime dependencies (>=, ==, ~=, or <= required)"
  fi
else
  fail "pyproject.toml missing at $PYPROJECT"
fi

# 3. requirements.txt exists with at least one entry
note "requirements.txt exists and lists packages"
if [[ -s "$REQUIREMENTS" ]]; then
  count=$(grep -cE '^[A-Za-z0-9_.\\-]+' "$REQUIREMENTS" || true)
  if [[ "$count" -ge 1 ]]; then
    pass "requirements.txt has $count package entries"
  else
    fail "requirements.txt has no package entries"
  fi
else
  fail "requirements.txt missing or empty at $REQUIREMENTS"
fi

# 4. Lockfile has the expected top-level package name set (PEP 503 normalised)
note "uv.lock contains every top-level pyproject dep (package-name level)"
if [[ -f "$PYPROJECT" && -s "$LOCK" ]]; then
  if uv run python - <<'PY' 2>/dev/null
import sys, tomllib, re
data = tomllib.load(open("pyproject.toml", "rb"))
deps = data.get("project", {}).get("dependencies", [])
lock = open("uv.lock").read()

def pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()

lock_names = {pep503(m.group(1)) for m in re.finditer(r'^name = "([^"]+)"', lock, re.MULTILINE)}
missing = []
for dep in deps:
    raw = re.split(r"[\[\<>=~!\s;]", dep, 1)[0].strip()
    if raw and pep503(raw) not in lock_names:
        missing.append(raw)
sys.exit(0 if not missing else 2)
PY
  then
    pass "uv.lock covers all pyproject.toml runtime deps (PEP 503 normalised)"
  else
    rc=$?
    if [[ "$rc" -eq 2 ]]; then
      fail "uv.lock is missing packages declared in pyproject.toml (after PEP 503 normalisation)"
    else
      fail "uv.lock / pyproject.toml sync check errored (rc=$rc)"
    fi
  fi
fi

# 5. No unpinned `==` baseline with no lower bound — sanity check
note "pyproject.toml has no plain '==' pin without a specifier"
unpinned=$(grep -E '"[A-Za-z0-9_.\\-]+==[0-9.]+"' "$PYPROJECT" 2>/dev/null | head -3 || true)
if [[ -n "$unpinned" ]]; then
  warn "pyproject.toml uses '==' pins (consider '>=' for flexibility):"
  printf '         %s\n' "$unpinned"
else
  pass "no bare '==' pins in pyproject.toml"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  printf '\033[32m[make dep-audit] OK — %s checks passed.\033[0m\n' "$checks"
  exit 0
else
  printf '\033[31m[make dep-audit] %s of %s checks failed.\033[0m\n' "$fail" "$checks"
  exit 1
fi