#!/usr/bin/env bash
# scripts/check_init_invariants.sh
#
# L30 Onboarding first-run wizard self-test (WL139).
#
# Invariants enforced:
#   1. The ``init_impl`` core module imports cleanly and exposes the canonical
#      surface (InitProfile enum, InitSummary dataclass, run_init_wizard).
#   2. The ``init_app`` Typer sub-app module imports cleanly and exposes the
#      ``init`` group registered with the root CLI.
#   3. The wizard's five canonical step labels match the contract:
#      preflight → probe → scaffold → contract → summary.
#   4. The DEFAULT_CONTRACT_VERSION is a non-empty SemVer-ish numeric string.
#   5. The contract-test suite ``tests/unit/onboarding/test_init_wizard.py``
#      exists and pins the wizard surface.
#   6. The root CLI advertises the ``init`` subcommand in ``--help`` output.
#
# Exits 0 on success, 1 on the first violation.
set -euo pipefail
# Disable shell-level grep auto-coloring (some envs export
# ``GREP_OPTIONS=--color=always`` or ``FORCE_COLOR=true`` which makes grep
# re-inject ANSI escape codes around matches even when piped).  Without
# this, the in-script regex would never see the literal ``init`` token
# because Rich's box-drawing + the inserted color codes break the match.
unset GREP_OPTIONS FORCE_COLOR 2>/dev/null || true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# `PY_RUNNER` resolves to either:
#   * the `uv run python` flavour when uv is on PATH (always preferred — the
#     repo's Python env lives in uv.lock and a system Python won't see the
#     editable install).
#   * a system `python3` fallback when uv is missing (CI runners without uv),
#     with PYTHONPATH adjusted so the src-layout import resolves.
if command -v uv >/dev/null 2>&1; then
  PY_RUNNER() { (cd "$ROOT" && uv run python "$@"); }
elif command -v python3 >/dev/null 2>&1; then
  PY_RUNNER() { PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" python3 "$@"; }
else
  PY_RUNNER() { python "$@"; }
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "ok   : $*"; }

# ---------------------------------------------------------------------------
# 1. ``init_impl`` core module imports cleanly with the canonical surface.
# ---------------------------------------------------------------------------
if ! PY_RUNNER - <<'PYEOF' >/dev/null 2>&1
from thegent.cli.commands.init_cmd import (
    DEFAULT_CONTRACT_VERSION,
    InitProfile,
    InitSummary,
    init_impl,
    run_init_wizard,
)
assert DEFAULT_CONTRACT_VERSION
assert {p.value for p in InitProfile} == {"minimal", "dev", "ci"}
assert callable(init_impl)
assert callable(run_init_wizard)
PYEOF
then
  fail "init_impl core module does not expose the canonical surface"
fi
ok "init_impl core module exposes the canonical surface"

# ---------------------------------------------------------------------------
# 2. ``init_app`` Typer sub-app module imports cleanly + root CLI registration.
# ---------------------------------------------------------------------------
root_groups="$(PY_RUNNER - <<'PYEOF'
from thegent.cli.apps.main import app
print("\n".join(sorted(getattr(g, "name", "") for g in app.registered_groups)))
PYEOF
)"
printf '%s\n' "$root_groups" | grep -Eq '^init$' \
  || fail "root CLI does not register the 'init' subcommand (groups=$root_groups)"
ok "root CLI registers the 'init' subcommand"

# The sub-app module itself must import without error (catches Typer refactors).
PY_RUNNER -c "from thegent.cli.apps.init_app import init_app, init_callback, init_check, init_verify" \
  >/dev/null \
  || fail "init_app module import failed"
ok "init_app sub-app module imports cleanly"

# ---------------------------------------------------------------------------
# 3. Five canonical step labels.
# ---------------------------------------------------------------------------
steps="$(PY_RUNNER - <<'PYEOF'
import json, tempfile, pathlib
with tempfile.TemporaryDirectory() as td:
    payload = __import__(
        "thegent.cli.commands.init_cmd", fromlist=["init_impl"]
    ).init_impl(target_dir=pathlib.Path(td))
print("\n".join(payload["steps"]))
PYEOF
)"
expected=$'preflight\nprobe\nscaffold\ncontract\nsummary'
if [ "$steps" != "$expected" ]; then
  fail "wizard step ladder drift (got='$steps', want='$expected')"
fi
ok "wizard step ladder is canonical"

# ---------------------------------------------------------------------------
# 4. DEFAULT_CONTRACT_VERSION is non-empty and SemVer-ish.
# ---------------------------------------------------------------------------
contract_version="$(PY_RUNNER - <<'PYEOF'
from thegent.cli.commands.init_cmd import DEFAULT_CONTRACT_VERSION
print(DEFAULT_CONTRACT_VERSION)
PYEOF
)"
if ! printf '%s' "$contract_version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  fail "DEFAULT_CONTRACT_VERSION='$contract_version' is not SemVer-ish (X.Y.Z)"
fi
ok "DEFAULT_CONTRACT_VERSION is SemVer-ish ($contract_version)"

# ---------------------------------------------------------------------------
# 5. Contract-test suite present.
# ---------------------------------------------------------------------------
TEST_FILE="$ROOT/tests/unit/onboarding/test_init_wizard.py"
if [ ! -f "$TEST_FILE" ]; then
  fail "missing contract test suite at $TEST_FILE"
fi
# Spot-check the pinned surface assertions.
for sym in init_impl run_init_wizard InitProfile InitSummary; do
  if ! grep -q "$sym" "$TEST_FILE"; then
    fail "contract test suite does not pin '$sym'"
  fi
done
ok "contract test suite pins the canonical surface"

# ---------------------------------------------------------------------------
# 6. Root CLI advertises the ``init`` subcommand in ``--help`` output.
# ---------------------------------------------------------------------------
if command -v thegent >/dev/null 2>&1; then
  help_out="$(COLUMNS=120 NO_COLOR=1 thegent --help 2>&1 || true)"
else
  help_out="$(cd "$ROOT" && COLUMNS=120 NO_COLOR=1 uv run thegent --help 2>&1 || PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" COLUMNS=120 NO_COLOR=1 python3 -m thegent --help 2>&1 || true)"
fi
# Strip ANSI escape codes from the help output and verify the ``init``
# row exists.  We delegate to scripts/strip_ansi.py for a robust strip
# (Rich's bold and dim codes confuse sed). The script is small + standalone
# so it does not depend on the repo's Python env.
plain="$(printf '%s' "$help_out" | python3 "$ROOT/scripts/strip_ansi.py" 2>/dev/null \
  || printf '%s' "$help_out" | sed -E 's/\x1b\[[0-9;?]*[A-Za-z]//g')"
# Rich renders the subcommand table with ``│`` border chars; the ``init``
# row is consistently ``│ init     <description> │``.  Match by anchoring on
# the canonical ``init`` token preceded by the box-drawing border.
if ! printf '%s' "$plain" | grep -Eq '^[[:space:]]*│[[:space:]]+init[[:space:]]+'; then
  fail "thegent --help does not advertise the 'init' subcommand"
fi
ok "thegent --help advertises the 'init' subcommand"

echo
echo "PASS: L30 first-run wizard invariants hold."
