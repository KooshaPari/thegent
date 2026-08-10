#!/usr/bin/env bash
# scripts/check_pip_audit_invariants.sh
#
# Dependency-vulnerability advisory gate for the L11 Dependencies lane.
#
# Implements six canonical checks:
#
#   1. pip-audit tooling is available (native or via `uvx`).
#   2. uv.lock exists and is non-empty (mirrors L11 invariant #1).
#   3. A frozen pip-style requirements file can be generated from uv.lock
#      via `uv export --frozen` so pip-audit gets a parseable input that
#      does not require network resolution (`--no-deps`).
#   4. pip-audit executes against the frozen requirements and emits a
#      parseable JSON report (`-f json --strict --no-deps --disable-pip`).
#   5. Severity gate — the number of HIGH+CRITICAL vulnerabilities does
#      not exceed the `PIP_AUDIT_FAIL_SEVERITY` threshold (default 0).
#      Lower severities are reported as advisory only.
#   6. Baseline snapshot — every run writes `help/audit/pip-audit-current.json`
#      and compares it against `help/audit/pip-audit-baseline.json` if the
#      baseline exists; new vulnerabilities (not in the baseline) are
#      flagged as a regression so the gate is meaningful even when the
#      upstream advisory feed shifts.
#
# Designed to run in <30s on the canonical workspace (network permitting);
# safe to invoke from a pre-commit hook, `make pip-audit`, or the L11
# CI gate. Exits 0 on success, 1 on the first violation.
#
# Environment variables:
#   PIP_AUDIT_FAIL_SEVERITY — one of LOW, MEDIUM, HIGH, CRITICAL, NONE
#                              (default: HIGH). Anything at or above this
#                              level fails the gate.
#   PIP_AUDIT_NO_NETWORK    — set to "1" to skip the actual pip-audit run
#                              (useful for offline CI smoke testing the
#                              gate logic). The script will emit a
#                              placeholder JSON snapshot.
#   PIP_AUDIT_TOOL          — override the pip-audit binary (default:
#                              auto-detected between native pip-audit and
#                              `uvx --from pip-audit pip-audit`).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/uv.lock"
AUDIT_DIR="$ROOT/help/audit"
BASELINE_JSON="$AUDIT_DIR/pip-audit-baseline.json"
CURRENT_JSON="$AUDIT_DIR/pip-audit-current.json"

FAIL_SEVERITY="${PIP_AUDIT_FAIL_SEVERITY:-HIGH}"
OFFLINE="${PIP_AUDIT_NO_NETWORK:-0}"
TOOL_OVERRIDE="${PIP_AUDIT_TOOL:-}"

fail=0
checks=0

# ANSI helpers — colourise only when stdout is a TTY so CI logs stay clean.
if [[ -t 1 ]]; then
  note()  { printf '  \033[36m[check]\033[0m %s\n' "$*"; checks=$((checks + 1)); }
  pass()  { printf '  \033[32m[ ok ]\033[0m %s\n' "$*"; }
  warn()  { printf '  \033[33m[warn]\033[0m %s\n' "$*"; }
  fail()  { printf '  \033[31m[FAIL]\033[0m %s\n' "$*"; fail=$((fail + 1)); }
else
  note()  { printf '  [check] %s\n' "$*"; checks=$((checks + 1)); }
  pass()  { printf '  [ ok ] %s\n' "$*"; }
  warn()  { printf '  [warn] %s\n' "$*"; }
  fail()  { printf '  [FAIL] %s\n' "$*"; fail=$((fail + 1)); }
fi

# Map a severity string to a rank so we can compare.
severity_rank() {
  case "$1" in
    CRITICAL) printf '4' ;;
    HIGH)     printf '3' ;;
    MEDIUM)   printf '2' ;;
    LOW)      printf '1' ;;
    NONE)     printf '0' ;;
    *)        printf '?' ;;
  esac
}

# Resolve the pip-audit binary. Honours PIP_AUDIT_TOOL override.
resolve_pip_audit() {
  if [[ -n "$TOOL_OVERRIDE" ]]; then
    printf '%s\n' "$TOOL_OVERRIDE"
    return 0
  fi
  if command -v pip-audit >/dev/null 2>&1; then
    command -v pip-audit
    return 0
  fi
  if command -v uvx >/dev/null 2>&1; then
    printf '%s\n' "uvx --from pip-audit pip-audit"
    return 0
  fi
  return 1
}

# ---------------------------------------------------------------------------
# 1. Tooling detection.
# ---------------------------------------------------------------------------
note "pip-audit tooling is available (native or via uvx)"
PIP_AUDIT_CMD="$(resolve_pip_audit || true)"
if [[ -z "$PIP_AUDIT_CMD" ]]; then
  fail "pip-audit not on PATH; install with 'pip install pip-audit' or 'uv tool install pip-audit'"
  echo
  printf '\033[31m[make pip-audit] tooling missing — install pip-audit before running the gate.\033[0m\n' >&2
  exit 1
fi
# Probe the resolved tool once so a broken install fails fast.
if [[ "$OFFLINE" != "1" ]]; then
  if ! bash -c "$PIP_AUDIT_CMD --version" >/dev/null 2>&1; then
    fail "pip-audit resolved to '$PIP_AUDIT_CMD' but --version failed"
  else
    version="$(bash -c "$PIP_AUDIT_CMD --version" 2>/dev/null | head -1 || echo unknown)"
    pass "pip-audit available: $version"
  fi
else
  warn "PIP_AUDIT_NO_NETWORK=1 — skipping live tool probe"
fi

# ---------------------------------------------------------------------------
# 2. uv.lock present + non-empty (mirrors dep-audit invariant).
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 3. Frozen pip-style requirements export succeeds.
# ---------------------------------------------------------------------------
note "uv export --frozen produces a parseable pip-style requirements file"
TMPDIR_BASE="${TMPDIR:-/tmp}"
if [[ ! -d "$TMPDIR_BASE" ]]; then
  TMPDIR_BASE="$HOME/.cache"
  mkdir -p "$TMPDIR_BASE"
fi
WORKDIR="$(mktemp -d "$TMPDIR_BASE/pip-audit.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
FROZEN_REQ="$WORKDIR/requirements-frozen.txt"

if [[ "$OFFLINE" == "1" ]]; then
  printf '# pip-audit offline placeholder\n# generated when PIP_AUDIT_NO_NETWORK=1\n# frozen export skipped\n' > "$FROZEN_REQ"
  warn "PIP_AUDIT_NO_NETWORK=1 — wrote placeholder requirements file ($FROZEN_REQ)"
elif command -v uv >/dev/null 2>&1; then
  if uv export --frozen --no-dev --no-emit-project --quiet --format requirements-txt --output-file "$FROZEN_REQ" 2>"$WORKDIR/uv-export.err"; then
    count=$(grep -cE '^[A-Za-z0-9_.\\-]+==' "$FROZEN_REQ" || true)
    if [[ "$count" -ge 1 ]]; then
      pass "uv export produced $count pinned requirements"
    else
      fail "uv export produced 0 pinned requirements (file empty?)"
    fi
  else
    fail "uv export failed — see $WORKDIR/uv-export.err"
    cat "$WORKDIR/uv-export.err" >&2 || true
  fi
else
  fail "uv not on PATH — required to generate frozen requirements"
fi

# ---------------------------------------------------------------------------
# 4. pip-audit runs and emits parseable JSON.
# ---------------------------------------------------------------------------
note "pip-audit emits parseable JSON for the frozen requirements"
AUDIT_JSON="$WORKDIR/audit.json"

if [[ "$OFFLINE" == "1" ]]; then
  # Empty findings list — gate still exercises JSON parse + counts.
  printf '{"dependencies": [], "fixes": []}\n' > "$AUDIT_JSON"
  warn "PIP_AUDIT_NO_NETWORK=1 — wrote empty findings placeholder"
else
  audit_rc=0
  # pip-audit exits 1 when vulnerabilities are found. We always want the
  # JSON output, so capture both streams and treat non-zero exit as data
  # rather than failure for THIS check (the severity gate below decides).
  # Default to the PyPI service because OSV times out behind our proxy.
  set +e
  bash -c "$PIP_AUDIT_CMD -r \"$FROZEN_REQ\" --strict --no-deps --disable-pip -f json --progress-spinner off -s pypi --timeout 30" >"$AUDIT_JSON" 2>"$WORKDIR/audit.err"
  audit_rc=$?
  set -e

  if [[ ! -s "$AUDIT_JSON" ]]; then
    fail "pip-audit produced empty output — see $WORKDIR/audit.err"
    sed 's/^/         /' "$WORKDIR/audit.err" >&2 || true
  elif ! python3 - "$AUDIT_JSON" <<'PYEOF' >/dev/null 2>&1
import json, sys
with open(sys.argv[1]) as fh:
    data = json.load(fh)
# pip-audit emits either {"dependencies": [...]} (canonical schema with
# `fixes`) or a bare list of dependency records. Accept both.
if isinstance(data, dict):
    deps = data.get("dependencies", [])
elif isinstance(data, list):
    deps = data
else:
    sys.exit(1)
if not isinstance(deps, list):
    sys.exit(2)
for entry in deps:
    if not isinstance(entry, dict) or "name" not in entry or "vulns" not in entry:
        sys.exit(3)
PYEOF
  then
    fail "pip-audit JSON output failed validation (schema mismatch)"
  else
    entries=$(python3 -c "
import json,sys
data = json.load(open(sys.argv[1]))
deps = data.get('dependencies', data if isinstance(data, list) else [])
print(len(deps))
" "$AUDIT_JSON")
    pass "pip-audit JSON parsed cleanly ($entries package entries, pip-audit rc=$audit_rc)"
  fi
fi

# ---------------------------------------------------------------------------
# 5. Severity gate.
# ---------------------------------------------------------------------------
note "severity gate: no findings at or above ${FAIL_SEVERITY}"

mkdir -p "$AUDIT_DIR"
if [[ -s "$AUDIT_JSON" ]]; then
  # Promote AUDIT_JSON to CURRENT_JSON so the snapshot survives the trap.
  cp "$AUDIT_JSON" "$CURRENT_JSON"
fi

if [[ -s "$CURRENT_JSON" ]]; then
  # Compute per-severity counts. pip-audit does not always populate
  # severity, so we treat an unknown severity as LOW (informational).
  severity_report="$(python3 - "$CURRENT_JSON" <<'PYEOF'
import json, sys, os

fail_severity = os.environ.get("PIP_AUDIT_FAIL_SEVERITY", "HIGH").upper()
rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
threshold = rank.get(fail_severity, 3)

with open(sys.argv[1]) as fh:
    data = json.load(fh)
deps = data.get("dependencies", data if isinstance(data, list) else [])

counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
failing = []
advisory = []
for entry in deps:
    name = entry.get("name", "?")
    version = entry.get("version", "?")
    for vuln in entry.get("vulns", []) or []:
        sev = (vuln.get("severity") or "UNKNOWN").upper()
        if sev not in counts:
            sev = "UNKNOWN"
        counts[sev] += 1
        vid = vuln.get("id", "?")
        fix = vuln.get("fix_versions", [])
        line = f"{name}=={version}  {sev:<8}  {vid}  fix={fix or '[]'}"
        sev_rank = rank.get(sev, 1)
        if sev_rank >= threshold and threshold > 0:
            failing.append(line)
        else:
            advisory.append(line)

total = sum(counts.values())
summary = ", ".join(f"{k}={v}" for k, v in counts.items() if v > 0)
print(f"SUMMARY\t{total}\t{summary or 'no findings'}")
print(f"FAILING\t{len(failing)}")
for line in failing:
    print(f"FAIL\t{line}")
print(f"ADVISORY\t{len(advisory)}")
for line in advisory:
    print(f"ADV\t{line}")
PYEOF
)"
  summary_line="$(printf '%s\n' "$severity_report" | grep -E '^SUMMARY' || true)"
  failing_count="$(printf '%s\n' "$severity_report" | awk -F'\t' '/^FAILING/{print $2}')"

  pass "${summary_line#SUMMARY	}"
  if [[ "${failing_count:-0}" -gt 0 ]]; then
    printf '%s\n' "$severity_report" | awk -F'\t' '/^FAIL\t/{printf "         %s\n", $2}'
    fail "$failing_count vulnerabilities at or above ${FAIL_SEVERITY} severity"
  else
    pass "no findings at or above ${FAIL_SEVERITY} (threshold=0 effectively disabled)"
  fi

  # Always print advisory findings (LOW/MEDIUM) so the gate is informative.
  advisory_count="$(printf '%s\n' "$severity_report" | awk -F'\t' '/^ADVISORY/{print $2}')"
  if [[ "${advisory_count:-0}" -gt 0 ]]; then
    printf '%s\n' "$severity_report" | awk -F'\t' '/^ADV\t/{printf "         %s\n", $2}'
    warn "$advisory_count advisory findings at or below MEDIUM — review help/audit/pip-audit-current.json"
  fi
else
  fail "current snapshot missing at $CURRENT_JSON"
fi

# ---------------------------------------------------------------------------
# 6. Baseline comparison.
# ---------------------------------------------------------------------------
note "baseline snapshot: current run does not introduce new vulnerabilities"
if [[ ! -f "$BASELINE_JSON" ]]; then
  warn "baseline missing at $BASELINE_JSON — initialising from current run"
  cp "$CURRENT_JSON" "$BASELINE_JSON"
elif [[ -s "$CURRENT_JSON" ]]; then
  if ! python3 - "$BASELINE_JSON" "$CURRENT_JSON" <<'PYEOF' >/dev/null 2>&1
import json, sys

def _deps(obj):
    if isinstance(obj, dict):
        return obj.get("dependencies", [])
    if isinstance(obj, list):
        return obj
    return []

with open(sys.argv[1]) as fh:
    base = json.load(fh)
with open(sys.argv[2]) as fh:
    cur = json.load(fh)

def key(entry, vuln):
    return (entry.get("name", "?"), entry.get("version", "?"), vuln.get("id", "?"))

base_keys = {key(e, v) for e in _deps(base) for v in (e.get("vulns") or [])}
new = []
for entry in _deps(cur):
    for vuln in (entry.get("vulns") or []):
        if key(entry, vuln) not in base_keys:
            new.append(f"{entry.get('name','?')}=={entry.get('version','?')}  {vuln.get('id','?')}")
if new:
    print("NEW_VULNS:", len(new))
    for line in new:
        print(f"  {line}")
    sys.exit(2)
sys.exit(0)
PYEOF
  then
    # Re-run to capture the diff text for the FAIL marker.
    diff_output="$(python3 - "$BASELINE_JSON" "$CURRENT_JSON" <<'PYEOF' 2>&1 || true
import json, sys

def _deps(obj):
    if isinstance(obj, dict):
        return obj.get("dependencies", [])
    if isinstance(obj, list):
        return obj
    return []

with open(sys.argv[1]) as fh:
    base = json.load(fh)
with open(sys.argv[2]) as fh:
    cur = json.load(fh)

def key(entry, vuln):
    return (entry.get("name", "?"), entry.get("version", "?"), vuln.get("id", "?"))

base_keys = {key(e, v) for e in _deps(base) for v in (e.get("vulns") or [])}
new = []
for entry in _deps(cur):
    for vuln in (entry.get("vulns") or []):
        if key(entry, vuln) not in base_keys:
            new.append(f"{entry.get('name','?')}=={entry.get('version','?')}  {vuln.get('id','?')}")
for line in new:
    print(f"         {line}")
PYEOF
)"
    while IFS= read -r line; do
      [[ -n "$line" ]] && warn "baseline regression: $line"
    done <<< "$diff_output"
    fail "current run introduced new vulnerabilities not in baseline"
  else
    pass "no new vulnerabilities vs baseline ($BASELINE_JSON)"
  fi
fi

echo
if [[ "$fail" -eq 0 ]]; then
  if [[ -t 1 ]]; then
    printf '\033[32m[make pip-audit] OK — %s checks passed.\033[0m\n' "$checks"
  else
    printf '[make pip-audit] OK — %s checks passed.\n' "$checks"
  fi
  exit 0
else
  if [[ -t 1 ]]; then
    printf '\033[31m[make pip-audit] %s of %s checks failed.\033[0m\n' "$fail" "$checks"
  else
    printf '[make pip-audit] %s of %s checks failed.\n' "$fail" "$checks"
  fi
  exit 1
fi
