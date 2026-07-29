#!/usr/bin/env bash
# Secrets-invariants static checker for the L27 Infrastructure lane.
#
# Verifies the canonical secret-scanning surfaces are intact, in sync, and
# free of common drift / hygiene issues:
#
#   1. gitleaks.toml exists, is non-empty, and parseable as TOML.
#   2. gitleaks.toml declares an [allowlist] block.
#   3. gitleaks.toml allowlist covers the canonical dev/test placeholder
#      patterns (agileplus-dev, your-*-here, PLACEHOLDER_*, test-secret,
#      example-key, dummy-token, fake-api-key) so they don't trigger false
#      positives in unit-test fixtures.
#   4. gitleaks.toml declares at least five custom rules so the scanner
#      is not silently running with only the upstream default rule set.
#   5. trufflehog.yml exists, is non-empty, and enables at least one
#      detector (so a placeholder config does not silently no-op).
#   6. .gitignore excludes the canonical secret-bearing artefacts
#      (.env, .env.local, *.pem, *.key, *.p12, *.pfx, secrets.yaml).
#   7. No high-confidence live-key pattern (AWS / OpenAI / Anthropic /
#      GitHub-PAT) leaks in non-allowlisted tracked-tree paths (cheap
#      regex sniff — advisory, not a substitute for gitleaks itself).
#
# Designed to run in <50ms; safe to invoke from a pre-commit hook or
# `make secrets-scan`. Non-zero exit on the first hard violation; the
# final status block prints a numbered summary before exiting.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITLEAKS_CFG="$ROOT/gitleaks.toml"
TRUFFLEHOG_CFG="$ROOT/trufflehog.yml"
GITIGNORE="$ROOT/.gitignore"

fail=0
checks=0

note()  { printf '  \033[36m[check]\033[0m %s\n' "$*"; checks=$((checks + 1)); }
pass()  { printf '  \033[32m[ ok ]\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m[warn]\033[0m %s\n' "$*"; }
fail()  { printf '  \033[31m[FAIL]\033[0m %s\n' "$*"; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# 1. gitleaks.toml exists, non-empty, parseable.
# ---------------------------------------------------------------------------
note "gitleaks.toml exists, non-empty, parseable"
if [[ -s "$GITLEAKS_CFG" ]]; then
  size=$(wc -c < "$GITLEAKS_CFG" | tr -d ' ')
  if uv run python - "$GITLEAKS_CFG" <<'PY' 2>/dev/null
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
data = tomllib.load(open(sys.argv[1], "rb"))
sys.exit(0 if isinstance(data, dict) else 2)
PY
  then
    pass "gitleaks.toml present ($size bytes, TOML parses)"
  else
    fail "gitleaks.toml failed to parse as TOML"
  fi
else
  fail "gitleaks.toml is missing or empty at $GITLEAKS_CFG"
fi

# ---------------------------------------------------------------------------
# 2. gitleaks.toml declares an [allowlist] block.
# ---------------------------------------------------------------------------
note "gitleaks.toml declares an [allowlist] block"
if uv run python - "$GITLEAKS_CFG" <<'PY' 2>/dev/null
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
data = tomllib.load(open(sys.argv[1], "rb"))
sys.exit(0 if "allowlist" in data else 2)
PY
then
  pass "gitleaks.toml has [allowlist] block"
else
  fail "gitleaks.toml is missing the [allowlist] table"
fi

# ---------------------------------------------------------------------------
# 3. gitleaks.toml allowlist covers the canonical dev/test placeholder set.
# ---------------------------------------------------------------------------
note "gitleaks.toml allowlist covers canonical dev/test placeholder patterns"
required_placeholders=(
  "^agileplus-dev$"
  "^your-.+-here$"
  "^PLACEHOLDER_"
  "^test-secret$"
  "^example-key$"
  "^dummy-token$"
  "^fake-api-key$"
)
missing_placeholders=()
present=$(uv run python - "$GITLEAKS_CFG" <<'PY' 2>/dev/null || true
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
data = tomllib.load(open(sys.argv[1], "rb"))
allow = data.get("allowlist", {})
for r in allow.get("regexes", []) or []:
    print(r)
PY
)
for pat in "${required_placeholders[@]}"; do
  if ! grep -Fxq "$pat" <<<"$present"; then
    missing_placeholders+=("$pat")
  fi
done
if [[ "${#missing_placeholders[@]}" -eq 0 ]]; then
  pass "gitleaks allowlist covers all ${#required_placeholders[@]} canonical placeholders"
else
  fail "gitleaks allowlist missing placeholders: ${missing_placeholders[*]}"
fi

# ---------------------------------------------------------------------------
# 4. gitleaks.toml declares at least five custom [[rules]] so the config
#    is not silently relying on the upstream defaults alone.
# ---------------------------------------------------------------------------
note "gitleaks.toml declares >= 5 custom [[rules]]"
rule_count=$(uv run python - "$GITLEAKS_CFG" <<'PY' 2>/dev/null || echo 0
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
data = tomllib.load(open(sys.argv[1], "rb"))
print(len(data.get("rules", []) or []))
PY
)
if [[ "$rule_count" -ge 5 ]]; then
  pass "gitleaks.toml has $rule_count custom rules"
else
  fail "gitleaks.toml only has $rule_count custom rules (expected >= 5)"
fi

# ---------------------------------------------------------------------------
# 5. trufflehog.yml exists, non-empty, has at least one detector enabled.
# ---------------------------------------------------------------------------
note "trufflehog.yml exists, non-empty, has detectors enabled"
if [[ -s "$TRUFFLEHOG_CFG" ]]; then
  size=$(wc -c < "$TRUFFLEHOG_CFG" | tr -d ' ')
  detector_count=$(grep -cE '^[[:space:]]*-[[:space:]]*[a-zA-Z]' "$TRUFFLEHOG_CFG" || true)
  if [[ "$detector_count" -ge 1 ]]; then
    pass "trufflehog.yml present ($size bytes, $detector_count detectors)"
  else
    fail "trufflehog.yml has no detectors enabled"
  fi
else
  fail "trufflehog.yml is missing or empty at $TRUFFLEHOG_CFG"
fi

# ---------------------------------------------------------------------------
# 6. .gitignore excludes canonical secret-bearing artefacts.
# ---------------------------------------------------------------------------
note ".gitignore excludes canonical secret-bearing artefacts"
# Each entry: pattern → list of gitignore globs that already cover it.
# A pattern is considered covered if ANY of its globs is present in
# .gitignore as a literal line. This lets `.env.*` cover `.env.local`
# without forcing both globs to be present.
declare -A ignore_coverage=(
  [".env"]=".env"
  [".env.local"]=".env.local .env.*"
  ["*.pem"]="*.pem"
  ["*.key"]="*.key"
  ["*.p12"]="*.p12"
  ["*.pfx"]="*.pfx"
  ["secrets.yaml"]="secrets.yaml"
)
if [[ -f "$GITIGNORE" ]]; then
  missing_ignores=()
  # Disable pathname expansion so `.env.*` is treated as a literal pattern
  # rather than glob-expanded to `.env.example`, `.env.template`, etc.
  set -f
  for pat in "${!ignore_coverage[@]}"; do
    covered=false
    for glob in ${ignore_coverage[$pat]}; do
      if grep -qxF "$glob" "$GITIGNORE"; then
        covered=true
        break
      fi
    done
    if [[ "$covered" != "true" ]]; then
      missing_ignores+=("$pat")
    fi
  done
  set +f
  if [[ "${#missing_ignores[@]}" -eq 0 ]]; then
    pass ".gitignore covers all ${#ignore_coverage[@]} canonical secret-bearing patterns"
  else
    fail ".gitignore missing patterns: ${missing_ignores[*]}"
  fi
else
  fail ".gitignore is missing at $GITIGNORE"
fi

# ---------------------------------------------------------------------------
# 7. Cheap regex sniff for live-key patterns leaking outside allowlisted
#    paths. Advisory — gitleaks remains the source of truth.
# ---------------------------------------------------------------------------
note "no live-key pattern leaks outside allowlisted paths (advisory sniff)"
LEAK_PATTERNS=(
  'AKIA[0-9A-Z]{16}'                              # AWS access key
  'sk-or-v1-[a-f0-9]{32,}'                        # OpenRouter
  'sk-[a-zA-Z0-9]{48}'                            # OpenAI
  'sk-ant-[a-zA-Z0-9]{32,}'                      # Anthropic
  'ghp_[a-zA-Z0-9]{36,}'                         # GitHub PAT
  'github_pat_[a-zA-Z0-9_]{22,}'                 # GitHub fine-grained
  'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}'         # Slack
)
# Combine the regex patterns with alternation.
COMBINED=$(IFS='|'; echo "${LEAK_PATTERNS[*]}")
# Allowlisted path segments — match anywhere in the path so fixtures
# nested under `crates/*/tests/`, `apps/*/tests/`, etc. are filtered.
# `case` glob matching is used (not bash regex) so the path-globs are
# unambiguous and free of the ERE single-vs-double-backslash gotcha.
path_is_allowlisted() {
  local p="$1"
  case "$p" in
    .env.example|.env.template|.env.local.example) return 0 ;;
    docs/*|.github/*|tests/*|examples/*|fixtures/*|__tests__/*) return 0 ;;
    */docs/*|*/.github/*|*/tests/*|*/examples/*|*/fixtures/*|*/__tests__/*) return 0 ;;
    *.md|*_test.py|*_test.go|test_*.py) return 0 ;;
  esac
  return 1
}
# Allowlisted content substrings — known public placeholder keys that
# never represent live credentials (AWS docs canonical example, etc.).
content_is_allowlisted() {
  local c="$1"
  [[ "$c" == *"AKIAIOSFODNN7EXAMPLE"* ]]
}
leaks=0
while IFS= read -r hit; do
  # `git grep -IEn` prints "<path>:<line>:<content>".
  rel="${hit%%:*}"
  rest="${hit#*:}"
  content="${rest#*:}"
  if path_is_allowlisted "$rel"; then continue; fi
  if content_is_allowlisted "$content"; then continue; fi
  echo "    potential leak: $hit" >&2
  leaks=$((leaks + 1))
done < <(git -C "$ROOT" --no-pager grep -IEn --no-color "$COMBINED" -- ':!*.lock' ':!**/*.lock' ':!gitleaks.toml' ':!trufflehog.yml' ':!scripts/check_secrets_invariants.sh' 2>/dev/null || true)
if [[ "$leaks" -eq 0 ]]; then
  pass "no live-key pattern leaks in tracked, non-allowlisted paths"
else
  warn "found $leaks potential live-key pattern(s) outside allowlisted paths"
  warn "  (advisory; gitleaks is the source of truth — verify before committing)"
  # Don't fail the build on the advisory sniff; keep it warn-only so
  # CI doesn't break on a known-allowlisted fixture.
fi

echo
if [[ "$fail" -eq 0 ]]; then
  printf '\033[32m[make secrets-scan] OK — %s checks passed.\033[0m\n' "$checks"
  exit 0
else
  printf '\033[31m[make secrets-scan] %s of %s checks failed.\033[0m\n' "$fail" "$checks"
  exit 1
fi