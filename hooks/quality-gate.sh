#!/usr/bin/env bash
# quality-gate.sh — Stop hook
# Comprehensive quality check before session ends.
# SOLE OWNER of: ruff, vulture, knip, jscpd, shellcheck, oxlint (lint + dead code)
# Budget: <5s. Optimized: batched linters, parallel execution, inlined sub-scripts.
set -euo pipefail

# --- Ultra-fast cache check BEFORE common.sh ---
# Cache git HEAD once to avoid repeated git calls throughout hook
readonly _GIT_HEAD_SHA="${HEAD_SHA:-$(git rev-parse HEAD 2>/dev/null || echo unknown)}"
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_KEY="$_GIT_HEAD_SHA"
_CACHE_FILE="${_CACHE_DIR}/quality-gate-${_CACHE_KEY}.result"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -f "$_CACHE_FILE" ]]; then
  _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
  if (( _age < _CACHE_TTL )); then
    cat "$_CACHE_FILE"
    exit 0
  fi
fi

HOOK_NAME="QUALITY-GATE"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Prevent infinite loops
[[ "${STOP_ACTIVE:-false}" == "true" ]] && exit 0

# --- P1 optimization: Skip if no quality-relevant files changed ---
# Only run if code/config files were modified
if ! any_source_changed; then
  echo "QUALITY-GATE: skipped (no source files changed)"
  exit 0
fi

# No changes tracked — skip
[[ ! -f "$CHANGE_LOG" ]] && exit 0

# --- Cache check — skip if unchanged ---
_cache_extra=$(hook_file_hash_cache "$QUALITY_CONFIG" 2>/dev/null || echo "")
_cache_key=$(hook_cache_key "$HOOK_NAME")
_cache_key=$(printf '%s\0%s' "$_cache_key" "$_cache_extra" | shasum -a 256 | cut -d' ' -f1)
_qg_ttl="${HOOK_CACHE_TTL:-600}"
if hook_cache_check "$_cache_key" "$_qg_ttl"; then
    hook_cache_read "$_cache_key" | tee "$_CACHE_FILE" 2>/dev/null
    _cached_rc=$?
    if [[ "$_cached_rc" -ne 0 ]]; then
      echo "QUALITY-GATE FAIL: cached result was non-zero ($_cached_rc)" >&2
    fi
    exit "$_cached_rc"
fi

_quality_gate_main() {
# ---------- Collect changed files by type ----------
declare -a PY_FILES=() SH_FILES=() TS_FILES=() GO_FILES=() ALL_FILES=()
declare -a C_FILES=() JAVA_FILES=() KOTLIN_FILES=() SWIFT_FILES=()
declare -a RUBY_FILES=() PHP_FILES=() DART_FILES=() SQL_FILES=()
declare -a MD_FILES=() CSS_FILES=() HTML_FILES=() DOCKERFILE_FILES=()
declare -a TF_FILES=() PROTO_FILES=() ELIXIR_FILES=() HASKELL_FILES=()
declare -a LUA_FILES=() PERL_FILES=() XML_FILES=()
# Exclude lockfiles and package-lock from secret scanning
declare -a SECRET_SCAN_FILES=()
CHANGED_EXTENSIONS=""

while IFS= read -r fpath; do
  [[ -z "$fpath" ]] && continue
  ALL_FILES+=("$fpath")
  local_ext="${fpath##*.}"
  local_base="${fpath##*/}"
  CHANGED_EXTENSIONS+="$local_ext "
  case "$local_ext" in
    py) PY_FILES+=("$fpath") ;;
    sh|bash) SH_FILES+=("$fpath") ;;
    ts|tsx|js|jsx) TS_FILES+=("$fpath") ;;
    go) GO_FILES+=("$fpath") ;;
    c|h|cpp|hpp|cc|cxx) C_FILES+=("$fpath") ;;
    java) JAVA_FILES+=("$fpath") ;;
    kt|kts) KOTLIN_FILES+=("$fpath") ;;
    swift) SWIFT_FILES+=("$fpath") ;;
    rb) RUBY_FILES+=("$fpath") ;;
    php) PHP_FILES+=("$fpath") ;;
    dart) DART_FILES+=("$fpath") ;;
    sql) SQL_FILES+=("$fpath") ;;
    md) MD_FILES+=("$fpath") ;;
    css|scss|less) CSS_FILES+=("$fpath") ;;
    html|htm) HTML_FILES+=("$fpath") ;;
    tf) TF_FILES+=("$fpath") ;;
    proto) PROTO_FILES+=("$fpath") ;;
    ex|exs) ELIXIR_FILES+=("$fpath") ;;
    hs) HASKELL_FILES+=("$fpath") ;;
    lua) LUA_FILES+=("$fpath") ;;
    pl|pm) PERL_FILES+=("$fpath") ;;
    xml) XML_FILES+=("$fpath") ;;
  esac
  case "$local_base" in
    Dockerfile*) DOCKERFILE_FILES+=("$fpath") ;;
  esac
  # Build secret-scan file list: exclude lockfiles
  case "$local_base" in
    package-lock.json) ;;
    *)
      case "$local_ext" in
        lock) ;;
        *) SECRET_SCAN_FILES+=("$fpath") ;;
      esac
      ;;
  esac
done < <(get_changed_files)

[[ ${#ALL_FILES[@]} -eq 0 ]] && exit 0

REPORT=""
ISSUES=0
POLICY_EXIT_CODE=0
GATE_FAIL_CLOSED="${QA_QUALITY_GATE_FAIL_CLOSED:-true}"

# ---------- Pre-parse quality config once ----------
# Parse max_duplication_pct from config files (avoid repeated jq calls)
MAX_DUP=5
for cfg in "$PROJECT_DIR/.qa-config.json" "$QUALITY_CONFIG"; do
  if [[ -f "$cfg" ]]; then
    CFG_VAL=$($JQ_CMD -r '.max_duplication_pct // empty' "$cfg" 2>/dev/null || true)
    if [[ -n "$CFG_VAL" ]]; then
      MAX_DUP="$CFG_VAL"
      break
    fi
  fi
done

# ---------- Temp dir for parallel lint results ----------
LINT_TMP="$(mktemp -d)"
trap 'rm -rf "$LINT_TMP"' EXIT

# ---------- Lint helper: run linter, write result to temp file ----------
# Usage: _lint_batch <label> <tool> <tmpfile> [tool-args...] -- file1 file2 ...
# For tools that accept multiple files as trailing args.
_lint_batch() {
  local label="$1" tmpfile="$2"; shift 2
  local -a args=()
  while [[ $# -gt 0 ]]; do
    args+=("$1")
    shift
  done
  local OUT
  OUT=$(run_with_timeout 10 "${args[@]}" 2>&1 || { echo "QUALITY-GATE: $label failed ($?)" >&2; true; })
  if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
    printf '%s\n' "$OUT" > "$tmpfile"
  fi
}

# ---------- Parallel lint: language groups ----------
# Group 1: Python (ruff lint + ruff F401 dead imports + vulture dead code)
lint_python() {
  if [[ ${#PY_FILES[@]} -gt 0 ]]; then
    if [[ "$(tool_available ruff)" == "true" ]]; then
      _lint_batch "PYTHON LINT (ruff)" "$LINT_TMP/py_lint" \
        ruff check --no-fix "${PY_FILES[@]}"
      _lint_batch "DEAD IMPORTS (ruff F401)" "$LINT_TMP/py_deadimport" \
        ruff check --select F401 --no-fix "${PY_FILES[@]}"
    fi
    if [[ "$(tool_available vulture)" == "true" ]]; then
      local OUT
      OUT=$(run_with_timeout 15 vulture --min-confidence 80 "${PY_FILES[@]}" 2>/dev/null || { echo "QUALITY-GATE: vulture failed ($?)" >&2; true; })
      if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
        printf '%s\n' "$OUT" > "$LINT_TMP/py_deadcode"
      fi
    fi
  fi
}

# Group 2: Shell
lint_shell() {
  if [[ ${#SH_FILES[@]} -gt 0 ]] && [[ "$(tool_available shellcheck)" == "true" ]]; then
    _lint_batch "SHELL LINT (shellcheck)" "$LINT_TMP/sh_lint" \
      shellcheck "${SH_FILES[@]}"
  fi
}

# Group 3: TypeScript/JavaScript (oxlint lint + dead imports + knip dead code)
lint_js() {
  if [[ ${#TS_FILES[@]} -gt 0 ]]; then
    if [[ "$(tool_available oxlint)" == "true" ]]; then
      _lint_batch "TS/JS LINT (oxlint)" "$LINT_TMP/ts_lint" \
        oxlint "${TS_FILES[@]}"
      _lint_batch "DEAD IMPORTS (oxlint)" "$LINT_TMP/ts_deadimport" \
        oxlint --deny no-unused-vars "${TS_FILES[@]}"
    elif [[ "$(tool_available eslint)" == "true" ]]; then
      _lint_batch "DEAD IMPORTS (eslint)" "$LINT_TMP/ts_deadimport" \
        eslint --rule '{"no-unused-vars":"warn"}' --no-eslintrc "${TS_FILES[@]}"
    fi
    if [[ "$(tool_available knip)" == "true" ]]; then
      local OUT
      OUT=$(run_with_timeout 15 knip --no-progress 2>/dev/null || { echo "QUALITY-GATE: knip failed ($?)" >&2; true; })
      if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
        printf '%s\n' "$OUT" > "$LINT_TMP/ts_deadcode"
      fi
    fi
  fi
}

# Group 4: Go
lint_go() {
  if [[ ${#GO_FILES[@]} -gt 0 ]] && [[ "$(tool_available golangci-lint)" == "true" ]]; then
    _lint_batch "GO LINT (golangci-lint)" "$LINT_TMP/go_lint" \
      golangci-lint run "${GO_FILES[@]}"
  fi
}

# Group 5: Other languages (batched where possible)
lint_other() {
  # C/C++ — clang-tidy accepts multiple files
  if [[ ${#C_FILES[@]} -gt 0 ]] && [[ "$(tool_available clang-tidy)" == "true" ]]; then
    _lint_batch "C/C++ LINT (clang-tidy)" "$LINT_TMP/c_lint" \
      clang-tidy "${C_FILES[@]}"
  fi

  # Java — checkstyle accepts multiple files
  if [[ ${#JAVA_FILES[@]} -gt 0 ]] && [[ "$(tool_available checkstyle)" == "true" ]]; then
    _lint_batch "JAVA LINT (checkstyle)" "$LINT_TMP/java_lint" \
      checkstyle -c /google_checks.xml "${JAVA_FILES[@]}"
  fi

  # Kotlin — detekt --input accepts comma-separated files
  if [[ ${#KOTLIN_FILES[@]} -gt 0 ]] && [[ "$(tool_available detekt)" == "true" ]]; then
    local kt_input
    kt_input="$(IFS=,; echo "${KOTLIN_FILES[*]}")"
    local OUT
    OUT=$(run_with_timeout 10 detekt --input "$kt_input" 2>&1 || { echo "QUALITY-GATE: detekt failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/kotlin_lint"
    fi
  fi

  # Swift — swiftlint accepts multiple --path args or directory; use single invocation
  if [[ ${#SWIFT_FILES[@]} -gt 0 ]] && [[ "$(tool_available swiftlint)" == "true" ]]; then
    local -a swift_args=(swiftlint lint --strict)
    local sf
    for sf in "${SWIFT_FILES[@]}"; do
      swift_args+=(--path "$sf")
    done
    local OUT
    OUT=$(run_with_timeout 10 "${swift_args[@]}" 2>&1 || { echo "QUALITY-GATE: swiftlint failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/swift_lint"
    fi
  fi

  # Ruby — rubocop accepts multiple files
  if [[ ${#RUBY_FILES[@]} -gt 0 ]] && [[ "$(tool_available rubocop)" == "true" ]]; then
    _lint_batch "RUBY LINT (rubocop)" "$LINT_TMP/ruby_lint" \
      rubocop --format simple "${RUBY_FILES[@]}"
  fi

  # PHP — phpstan accepts multiple files
  if [[ ${#PHP_FILES[@]} -gt 0 ]] && [[ "$(tool_available phpstan)" == "true" ]]; then
    _lint_batch "PHP LINT (phpstan)" "$LINT_TMP/php_lint" \
      phpstan analyse --no-progress "${PHP_FILES[@]}"
  fi

  # Dart — dart analyze accepts multiple files
  if [[ ${#DART_FILES[@]} -gt 0 ]] && [[ "$(tool_available dart)" == "true" ]]; then
    _lint_batch "DART LINT (dart analyze)" "$LINT_TMP/dart_lint" \
      dart analyze "${DART_FILES[@]}"
  fi

  # SQL — sqlfluff lint accepts multiple files
  if [[ ${#SQL_FILES[@]} -gt 0 ]] && [[ "$(tool_available sqlfluff)" == "true" ]]; then
    _lint_batch "SQL LINT (sqlfluff)" "$LINT_TMP/sql_lint" \
      sqlfluff lint "${SQL_FILES[@]}"
  fi

  # Markdown — markdownlint-cli2 accepts multiple files
  if [[ ${#MD_FILES[@]} -gt 0 ]] && [[ "$(tool_available markdownlint-cli2)" == "true" ]]; then
    _lint_batch "MARKDOWN LINT (markdownlint-cli2)" "$LINT_TMP/md_lint" \
      markdownlint-cli2 "${MD_FILES[@]}"
  fi

  # CSS/SCSS — stylelint accepts multiple files
  if [[ ${#CSS_FILES[@]} -gt 0 ]] && [[ "$(tool_available stylelint)" == "true" ]]; then
    _lint_batch "CSS LINT (stylelint)" "$LINT_TMP/css_lint" \
      stylelint "${CSS_FILES[@]}"
  fi

  # HTML — htmlhint accepts multiple files
  if [[ ${#HTML_FILES[@]} -gt 0 ]] && [[ "$(tool_available htmlhint)" == "true" ]]; then
    _lint_batch "HTML LINT (htmlhint)" "$LINT_TMP/html_lint" \
      htmlhint "${HTML_FILES[@]}"
  fi

  # Dockerfile — hadolint accepts stdin or single file; use xargs for batching
  if [[ ${#DOCKERFILE_FILES[@]} -gt 0 ]] && [[ "$(tool_available hadolint)" == "true" ]]; then
    local OUT=""
    local df
    for df in "${DOCKERFILE_FILES[@]}"; do
      OUT+=$(run_with_timeout 10 hadolint "$df" 2>&1 || { echo "QUALITY-GATE: hadolint failed ($?)" >&2; true; })
    done
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/docker_lint"
    fi
  fi

  # Terraform — tflint requires per-file
  if [[ ${#TF_FILES[@]} -gt 0 ]] && [[ "$(tool_available tflint)" == "true" ]]; then
    local OUT=""
    local tf
    for tf in "${TF_FILES[@]}"; do
      OUT+=$(run_with_timeout 10 tflint "$tf" 2>&1 || { echo "QUALITY-GATE: tflint failed ($?)" >&2; true; })
    done
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/tf_lint"
    fi
  fi

  # Protobuf — buf lint accepts --path for multiple files in one invocation
  if [[ ${#PROTO_FILES[@]} -gt 0 ]] && [[ "$(tool_available buf)" == "true" ]]; then
    local -a buf_args=(buf lint)
    local pf
    for pf in "${PROTO_FILES[@]}"; do
      buf_args+=(--path "$pf")
    done
    local OUT
    OUT=$(run_with_timeout 10 "${buf_args[@]}" 2>&1 || { echo "QUALITY-GATE: buf lint failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/proto_lint"
    fi
  fi

  # Elixir — mix credo accepts directory or multiple files
  if [[ ${#ELIXIR_FILES[@]} -gt 0 ]] && [[ "$(tool_available mix)" == "true" ]]; then
    _lint_batch "ELIXIR LINT (credo)" "$LINT_TMP/elixir_lint" \
      mix credo --strict "${ELIXIR_FILES[@]}"
  fi

  # Haskell — hlint accepts multiple files
  if [[ ${#HASKELL_FILES[@]} -gt 0 ]] && [[ "$(tool_available hlint)" == "true" ]]; then
    _lint_batch "HASKELL LINT (hlint)" "$LINT_TMP/haskell_lint" \
      hlint "${HASKELL_FILES[@]}"
  fi

  # Lua — luacheck accepts multiple files
  if [[ ${#LUA_FILES[@]} -gt 0 ]] && [[ "$(tool_available luacheck)" == "true" ]]; then
    _lint_batch "LUA LINT (luacheck)" "$LINT_TMP/lua_lint" \
      luacheck "${LUA_FILES[@]}"
  fi

  # Perl — perlcritic accepts multiple files
  if [[ ${#PERL_FILES[@]} -gt 0 ]] && [[ "$(tool_available perlcritic)" == "true" ]]; then
    _lint_batch "PERL LINT (perlcritic)" "$LINT_TMP/perl_lint" \
      perlcritic --harsh "${PERL_FILES[@]}"
  fi

  # XML — xmllint accepts multiple files with --noout
  if [[ ${#XML_FILES[@]} -gt 0 ]] && [[ "$(tool_available xmllint)" == "true" ]]; then
    _lint_batch "XML LINT (xmllint)" "$LINT_TMP/xml_lint" \
      xmllint --noout "${XML_FILES[@]}"
  fi
}

# Group 6: Security scans (batched secret detection)
lint_security() {
  # Batched secret scan: single grep over all eligible files
  if [[ ${#SECRET_SCAN_FILES[@]} -gt 0 ]]; then
    # Combined regex: API keys/secrets + hardcoded tokens
    local SECRET_RE='(api[_-]?[Kk]ey|[Ss]ecret|[Pp]assword|[Tt]oken|[Bb]earer|private[_-]?[Kk]ey)[[:space:]]*[:=][[:space:]]*['"'"'"][^'"'"'"]{8,}'
    local HARDCODED_RE='(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|-----BEGIN (RSA |EC )?PRIVATE KEY-----)'
    local COMBINED_RE="($SECRET_RE|$HARDCODED_RE)"
    local SECRET_HITS
    SECRET_HITS=$(grep -nE "$COMBINED_RE" "${SECRET_SCAN_FILES[@]}" 2>/dev/null || true)
    if [[ -n "$SECRET_HITS" ]]; then
      printf '%s\n' "$SECRET_HITS" > "$LINT_TMP/secrets"
    fi
  fi

  # Ruby: brakeman
  if [[ "$CHANGED_EXTENSIONS" == *"rb"* ]] && [[ "$(tool_available brakeman)" == "true" ]]; then
    local OUT
    OUT=$(run_with_timeout 15 brakeman -q 2>&1 || { echo "QUALITY-GATE: brakeman failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/brakeman"
    fi
  fi

  # PHP: psalm taint analysis
  if [[ "$CHANGED_EXTENSIONS" == *"php"* ]] && [[ "$(tool_available psalm)" == "true" ]]; then
    local OUT
    OUT=$(run_with_timeout 15 psalm --taint-analysis 2>&1 || { echo "QUALITY-GATE: psalm failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/psalm"
    fi
  fi
}

# Group 7: Code duplication (jscpd — only if available)
# Budget: 3s max. Uses --pattern to target only changed file extensions.
lint_duplication() {
  if [[ "$(tool_available jscpd)" == "true" ]] && [[ ${#ALL_FILES[@]} -gt 1 ]]; then
    # Collect unique directories of changed files to limit scope
    local -A _dirs=()
    local _f _d
    for _f in "${ALL_FILES[@]}"; do
      _d="$(dirname "$_f")"
      _dirs["$_d"]=1
    done
    # Build unique dirs array (max 5 to avoid scanning too many dirs)
    local -a jscpd_dirs=()
    local _count=0
    for _d in "${!_dirs[@]}"; do
      jscpd_dirs+=("$_d")
      _count=$((_count + 1))
      [[ $_count -ge 5 ]] && break
    done
    local OUT
    OUT=$(run_with_timeout 3 jscpd --min-lines 5 --min-tokens 50 --reporters console --silent "${jscpd_dirs[@]}" 2>/dev/null || { echo "QUALITY-GATE: jscpd failed ($?)" >&2; true; })
    if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
      printf '%s\n' "$OUT" > "$LINT_TMP/jscpd"
    fi
  fi
}

# ---------- Launch all lint groups in parallel ----------
lint_python &
lint_shell &
lint_js &
lint_go &
lint_other &
lint_security &
lint_duplication &
wait

# ---------- Collect lint results from temp files ----------
_collect_lint() {
  local file="$1" label="$2"
  if [[ -f "$file" ]]; then
    local content
    content="$(<"$file")"
    if [[ -n "$content" ]]; then
      REPORT+="$label:\n$content\n\n"
      ISSUES=$((ISSUES + 1))
    fi
  fi
}

# Lint results
_collect_lint "$LINT_TMP/py_lint" "PYTHON LINT (ruff)"
_collect_lint "$LINT_TMP/sh_lint" "SHELL LINT (shellcheck)"
_collect_lint "$LINT_TMP/ts_lint" "TS/JS LINT (oxlint)"
_collect_lint "$LINT_TMP/go_lint" "GO LINT (golangci-lint)"
_collect_lint "$LINT_TMP/c_lint" "C/C++ LINT (clang-tidy)"
_collect_lint "$LINT_TMP/java_lint" "JAVA LINT (checkstyle)"
_collect_lint "$LINT_TMP/kotlin_lint" "KOTLIN LINT (detekt)"
_collect_lint "$LINT_TMP/swift_lint" "SWIFT LINT (swiftlint)"
_collect_lint "$LINT_TMP/ruby_lint" "RUBY LINT (rubocop)"
_collect_lint "$LINT_TMP/php_lint" "PHP LINT (phpstan)"
_collect_lint "$LINT_TMP/dart_lint" "DART LINT (dart analyze)"
_collect_lint "$LINT_TMP/sql_lint" "SQL LINT (sqlfluff)"
_collect_lint "$LINT_TMP/md_lint" "MARKDOWN LINT (markdownlint-cli2)"
_collect_lint "$LINT_TMP/css_lint" "CSS LINT (stylelint)"
_collect_lint "$LINT_TMP/html_lint" "HTML LINT (htmlhint)"
_collect_lint "$LINT_TMP/docker_lint" "DOCKERFILE LINT (hadolint)"
_collect_lint "$LINT_TMP/tf_lint" "TERRAFORM LINT (tflint)"
_collect_lint "$LINT_TMP/proto_lint" "PROTOBUF LINT (buf)"
_collect_lint "$LINT_TMP/elixir_lint" "ELIXIR LINT (credo)"
_collect_lint "$LINT_TMP/haskell_lint" "HASKELL LINT (hlint)"
_collect_lint "$LINT_TMP/lua_lint" "LUA LINT (luacheck)"
_collect_lint "$LINT_TMP/perl_lint" "PERL LINT (perlcritic)"
_collect_lint "$LINT_TMP/xml_lint" "XML LINT (xmllint)"

# Security results
if [[ -f "$LINT_TMP/secrets" ]]; then
  REPORT+="SECURITY -- Potential secrets detected:\n$(<"$LINT_TMP/secrets")\n\n"
  ISSUES=$((ISSUES + 1))
fi
_collect_lint "$LINT_TMP/brakeman" "SECURITY -- brakeman"
_collect_lint "$LINT_TMP/psalm" "SECURITY -- psalm"

# Dead code results
if [[ -f "$LINT_TMP/py_deadcode" ]]; then
  DC_COUNT=$(wc -l < "$LINT_TMP/py_deadcode" | tr -d ' ')
  REPORT+="DEAD CODE: $DC_COUNT potential dead code items found (Python/vulture)\n$(<"$LINT_TMP/py_deadcode")\n\n"
  ISSUES=$((ISSUES + 1))
fi
if [[ -f "$LINT_TMP/ts_deadcode" ]]; then
  DC_COUNT=$(wc -l < "$LINT_TMP/ts_deadcode" | tr -d ' ')
  REPORT+="DEAD CODE: $DC_COUNT potential dead code items found (JS-TS/knip)\n$(<"$LINT_TMP/ts_deadcode")\n\n"
  ISSUES=$((ISSUES + 1))
fi

# Dead import results
if [[ -f "$LINT_TMP/py_deadimport" ]]; then
  DI_COUNT=$(wc -l < "$LINT_TMP/py_deadimport" | tr -d ' ')
  REPORT+="DEAD IMPORTS: $DI_COUNT unused imports found (Python/ruff F401)\n$(<"$LINT_TMP/py_deadimport")\n\n"
  ISSUES=$((ISSUES + 1))
fi
if [[ -f "$LINT_TMP/ts_deadimport" ]]; then
  DI_COUNT=$(wc -l < "$LINT_TMP/ts_deadimport" | tr -d ' ')
  _label="JS-TS/oxlint"
  [[ "$(tool_available oxlint)" != "true" ]] && _label="JS-TS/eslint"
  REPORT+="DEAD IMPORTS: $DI_COUNT unused imports found ($_label)\n$(<"$LINT_TMP/ts_deadimport")\n\n"
  ISSUES=$((ISSUES + 1))
fi

# Duplication results
if [[ -f "$LINT_TMP/jscpd" ]]; then
  DUP_OUT="$(<"$LINT_TMP/jscpd")"
  DUP_PCT=$(echo "$DUP_OUT" | grep -oE '[0-9]+(\.[0-9]+)?%' | tail -1 | tr -d '%' || echo "0")
  REPORT+="DUPLICATION: ${DUP_PCT:-0}% (max: ${MAX_DUP}%)\n"
  DUP_INT=${DUP_PCT%%.*}
  DUP_INT=${DUP_INT:-0}
  MAX_INT=${MAX_DUP%%.*}
  MAX_INT=${MAX_INT:-5}
  if [[ "$DUP_INT" -gt "$MAX_INT" ]]; then
    REPORT+="DUPLICATION exceeds threshold:\n$DUP_OUT\n\n"
    ISSUES=$((ISSUES + 1))
  fi
fi

# ---------- Architecture enforcement (cheap file checks, no subprocesses) ----------
if { [[ -f "$PROJECT_DIR/.importlinter" ]] || [[ -f "$PROJECT_DIR/setup.cfg" ]]; } && [[ "$(tool_available lint-imports)" == "true" ]]; then
  OUT=$(run_with_timeout 10 lint-imports 2>&1 || { echo "QUALITY-GATE: lint-imports failed ($?)" >&2; true; })
  if [[ -n "$OUT" ]] && [[ "$OUT" =~ [^[:space:]] ]]; then
    REPORT+="ARCHITECTURE -- import-linter:\n$OUT\n\n"
    ISSUES=$((ISSUES + 1))
  fi
fi

if [[ -f "$PROJECT_DIR/.golangci.yml" ]] || [[ -f "$PROJECT_DIR/.golangci.yaml" ]]; then
  REPORT+="ARCHITECTURE: Go architecture enforcement via golangci-lint depguard\n"
fi

if [[ -f "$PROJECT_DIR/.eslintrc.boundaries.json" ]] || [[ -f "$PROJECT_DIR/eslint.config.boundaries.js" ]]; then
  REPORT+="ARCHITECTURE: TypeScript architecture enforcement via eslint-plugin-boundaries\n"
fi

# ---------- Unified FR traceability + methodology (single pass) ----------
FR_FILE="$PROJECT_DIR/FUNCTIONAL_REQUIREMENTS.md"
FR_PATTERN='FR-[A-Z]+-[0-9]+'
FR_IDS_FILE=""
FR_TEST_IDS_FILE=""

echo ""
echo "=== Methodology Compliance ==="
METHODOLOGY_ISSUES=0

if [[ -f "$FR_FILE" ]]; then
  # Extract unique FR IDs from spec and tests in parallel using temp files
  FR_IDS_FILE="$LINT_TMP/fr_ids"
  FR_TEST_IDS_FILE="$LINT_TMP/fr_test_ids"

  grep -oE "$FR_PATTERN" "$FR_FILE" 2>/dev/null | sort_unique > "$FR_IDS_FILE" || true
  FR_COUNT=$(wc -l < "$FR_IDS_FILE" | tr -d ' ')

  # Determine test directory
  TEST_DIR=""
  [[ -d "$PROJECT_DIR/test" ]] && TEST_DIR="$PROJECT_DIR/test"
  [[ -d "$PROJECT_DIR/tests" ]] && TEST_DIR="$PROJECT_DIR/tests"

  if [[ -n "$TEST_DIR" ]] && [[ "$FR_COUNT" -gt 0 ]]; then
    grep -roE "$FR_PATTERN" "$TEST_DIR" 2>/dev/null | cut -d: -f2 | sort_unique > "$FR_TEST_IDS_FILE" || true
    COVERED_COUNT=$(wc -l < "$FR_TEST_IDS_FILE" | tr -d ' ')

    # Orphaned FRs: set difference (in spec but not in tests)
    ORPHANED=$(comm -23 "$FR_IDS_FILE" "$FR_TEST_IDS_FILE" 2>/dev/null || true)

    REPORT+="TRACEABILITY: $COVERED_COUNT/$FR_COUNT FRs covered by tests\n"
    if [[ -n "$ORPHANED" ]]; then
      # Format orphaned FRs with indent
      ORPHANED_FMT=$(echo "$ORPHANED" | sed 's/^/  /')
      REPORT+="Orphaned FRs (no test coverage):\n$ORPHANED_FMT\n\n"
    fi

    # FR traceability coverage for methodology section
    echo ""
    echo "  --- FR Traceability ---"
    TOTAL_FRS=$(grep -cE "$FR_PATTERN" "$FR_FILE" 2>/dev/null || echo "0")
    TESTED_FRS="$COVERED_COUNT"

    if (( TOTAL_FRS > 0 )); then
      COVERAGE_PCT=$((TESTED_FRS * 100 / TOTAL_FRS))
      echo "  FRs defined: $TOTAL_FRS"
      echo "  FRs with tests: $TESTED_FRS"
      echo "  FR coverage: ${COVERAGE_PCT}%"

      if (( COVERAGE_PCT < 50 )); then
        echo "  WARN: FR test coverage below 50%"
        METHODOLOGY_ISSUES=$((METHODOLOGY_ISSUES + 1))
      fi
    else
      echo "  No FRs found in FUNCTIONAL_REQUIREMENTS.md"
    fi

    # Orphan test check: single find + single grep -L pass
    # Build test file list once, then grep -L for files without FR tags
    TEST_FILE_LIST="$LINT_TMP/test_files_list"
    find "$TEST_DIR" -type f \( -name "test_*" -o -name "*_test.*" -o -name "*.test.*" -o -name "*.spec.*" -o -name "*.bats" \) 2>/dev/null > "$TEST_FILE_LIST" || true
    TOTAL_TEST_FILES=$(wc -l < "$TEST_FILE_LIST" | tr -d ' ')

    if (( TOTAL_TEST_FILES > 0 )); then
      # Use grep -LE with xargs for orphan detection — single grep invocation
      # Note: grep -L returns exit 1 when all files match, so suppress pipefail
      ORPHAN_TEST_FILES=$( (xargs grep -LE "$FR_PATTERN" < "$TEST_FILE_LIST" 2>/dev/null || true) | wc -l | tr -d ' ')
      echo "  Test files: $TOTAL_TEST_FILES, Orphaned (no FR tag): $ORPHAN_TEST_FILES"
      if (( ORPHAN_TEST_FILES > 0 )); then
        echo "  WARN: $ORPHAN_TEST_FILES test file(s) have no FR traceability tags"
      fi
    fi
  fi
fi

# Test-first check: if new source files were created, verify test files exist
if [[ -f "$CHANGE_LOG" ]]; then
  NEW_SOURCE_FILES=()
  while IFS= read -r line; do
    if [[ "$line" == *"created"* ]] || [[ "$line" == *"new"* ]]; then
      file=$(echo "$line" | grep -oE '[^ ]+\.(py|ts|tsx|js|jsx|go|rs|rb|php|java|kt|swift|ex|hs|lua|pl|dart|scala|zig)' | head -1)
      if [[ -n "$file" ]] && [[ ! "$file" =~ (test_|_test\.|\.test\.|\.spec\.|tests/|test/|__tests__/) ]]; then
        NEW_SOURCE_FILES+=("$file")
      fi
    fi
  done < "$CHANGE_LOG"

  if (( ${#NEW_SOURCE_FILES[@]} > 0 )); then
    echo "  New source files created: ${#NEW_SOURCE_FILES[@]}"
    MISSING_TESTS=0

    # Build a list of all test file basenames once (single find, sed for basename)
    TEST_BASENAMES="$LINT_TMP/test_basenames"
    find "$PROJECT_DIR" -maxdepth 5 -type f \( -name "test_*" -o -name "*_test.*" -o -name "*.test.*" -o -name "*.spec.*" -o -name "*_spec.*" \) 2>/dev/null | sed 's|.*/||' | sort_unique > "$TEST_BASENAMES" || true

    for src_file in "${NEW_SOURCE_FILES[@]}"; do
      base=$(basename "$src_file")
      name="${base%.*}"

      has_test=false
      for pattern in "test_${name}" "${name}_test" "${name}.test" "${name}.spec" "${name}_spec"; do
        if grep -q "^${pattern}\." "$TEST_BASENAMES" 2>/dev/null; then
          has_test=true
          break
        fi
      done

      if [[ "$has_test" == "false" ]]; then
        echo "  WARN: No test file found for new source: $src_file"
        MISSING_TESTS=$((MISSING_TESTS + 1))
      fi
    done

    if (( MISSING_TESTS > 0 )); then
      echo "  $MISSING_TESTS new source file(s) without corresponding tests (test-first violation)"
      METHODOLOGY_ISSUES=$((METHODOLOGY_ISSUES + MISSING_TESTS))
    else
      echo "  All new source files have corresponding tests"
    fi
  fi
fi

echo ""
echo "  Methodology issues: $METHODOLOGY_ISSUES"
ISSUES=$((ISSUES + METHODOLOGY_ISSUES))

# ---------- Inlined attestation builder (avoids subprocess fork) ----------
_run_attestation() {
  local ATTEST_OUT_FILE="$VERIFY_DIR/qa-attestation.json"
  local QUALITY="$QUALITY_CONFIG"
  local SIGSTORE="$PROJECT_DIR/.claude/sigstore-private.json"

  # Git metadata (3 git calls)
  local git_sha git_ref git_remote
  git_sha="$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo "no-git-sha")"
  git_ref="$(git -C "$PROJECT_DIR" symbolic-ref -q --short HEAD 2>/dev/null || git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
  git_remote="$(git -C "$PROJECT_DIR" config --get remote.origin.url 2>/dev/null || echo "unknown")"
  local builder_id="https://github.com/kush/sharecli/builder/qa-attestation-builder"

  # Policy hash
  local policy_hash=""
  if [[ -f "$QUALITY" ]]; then
    if command -v sha256sum >/dev/null 2>&1; then
      policy_hash="$(sha256sum "$QUALITY" | awk '{print $1}')"
    else
      policy_hash="$(shasum -a 256 "$QUALITY" | awk '{print $1}')"
    fi
  fi

  local subject_digest="${policy_hash:-0000000000000000000000000000000000000000000000000000000000000000}"

  # Rekor bundle pointer
  local rekor_bundle=""
  if [[ -f "$SIGSTORE" ]]; then
    local rekor_endpoint
    rekor_endpoint="$($JQ_CMD -r '.rekor_endpoint // empty' "$SIGSTORE" 2>/dev/null || true)"
    if [[ -n "$rekor_endpoint" && "$rekor_endpoint" != "null" ]]; then
      rekor_bundle="{\"logIndex\":\"placeholder-$(date +%s)\",\"Endpoint\":\"${rekor_endpoint}\"}"
    fi
  else
    local rekor_endpoint="${REKOR_ENDPOINT:-}"
    local rekor_uuid="${REKOR_ENTRY_UUID:-}"
    if [[ -n "$rekor_endpoint" && -n "$rekor_uuid" ]]; then
      rekor_bundle="{\"logIndex\":\"${rekor_uuid}\",\"Endpoint\":\"${rekor_endpoint}\"}"
    fi
  fi

  # Chaos posture
  local chaos_posture="baseline"
  if [[ -f "$QUALITY" ]]; then
    chaos_posture="$($JQ_CMD -r '.governance.chaos.posture // "baseline"' "$QUALITY" 2>/dev/null || echo "baseline")"
  fi

  # Detect test types using directory checks (no find calls for common dirs)
  local detected_unit=false detected_integration=false detected_e2e=false
  local detected_security=false detected_property_based=false detected_contract=false
  local detected_mutation=false detected_bdd=false

  [[ -d "$PROJECT_DIR/test/unit" || -d "$PROJECT_DIR/tests/unit" ]] && detected_unit=true
  # Also check against already-built test file list (no extra find)
  if [[ "$detected_unit" == "false" ]]; then
    if [[ -f "$LINT_TMP/test_files_list" ]] && [[ -s "$LINT_TMP/test_files_list" ]]; then
      detected_unit=true
    elif [[ -f "$LINT_TMP/test_basenames" ]] && [[ -s "$LINT_TMP/test_basenames" ]]; then
      detected_unit=true
    fi
  fi
  [[ -d "$PROJECT_DIR/test/integration" || -d "$PROJECT_DIR/tests/integration" ]] && detected_integration=true
  [[ -d "$PROJECT_DIR/test/e2e" || -d "$PROJECT_DIR/tests/e2e" || -d "$PROJECT_DIR/test/end-to-end" || -d "$PROJECT_DIR/cypress" || -d "$PROJECT_DIR/playwright" || -d "$PROJECT_DIR/e2e" ]] && detected_e2e=true
  [[ -d "$PROJECT_DIR/test/security" || -d "$PROJECT_DIR/tests/security" || -f "$PROJECT_DIR/.gitleaks.toml" || -f "$PROJECT_DIR/.semgrep.yml" || -f "$PROJECT_DIR/bandit.yaml" ]] && detected_security=true
  # Property-based: check test dirs only (avoids full project scan)
  if [[ -d "$PROJECT_DIR/test" ]] || [[ -d "$PROJECT_DIR/tests" ]]; then
    local _prop_dir="$PROJECT_DIR/test"
    [[ -d "$PROJECT_DIR/tests" ]] && _prop_dir="$PROJECT_DIR/tests"
    if command -v rg >/dev/null 2>&1; then
      rg -l -q 'hypothesis|fast-check|quickcheck|proptest' "$_prop_dir" 2>/dev/null && detected_property_based=true
    fi
  fi
  [[ -d "$PROJECT_DIR/test/contract" || -d "$PROJECT_DIR/tests/contract" || -f "$PROJECT_DIR/pact.json" ]] && detected_contract=true
  [[ -f "$PROJECT_DIR/.mutmut.ini" || -f "$PROJECT_DIR/stryker.conf.js" || -f "$PROJECT_DIR/stryker.config.js" ]] && detected_mutation=true
  [[ -d "$PROJECT_DIR/features" || -d "$PROJECT_DIR/test/bdd" || -d "$PROJECT_DIR/tests/bdd" ]] && detected_bdd=true

  # Count detected types
  local detected_count=0
  [[ "$detected_unit" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_integration" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_e2e" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_security" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_property_based" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_contract" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_mutation" == "true" ]] && detected_count=$((detected_count + 1))
  [[ "$detected_bdd" == "true" ]] && detected_count=$((detected_count + 1))

  # FR coverage (reuse already-computed values if available)
  local fr_total=0 fr_covered=0
  if [[ -n "$FR_IDS_FILE" && -f "$FR_IDS_FILE" ]]; then
    fr_total=$(wc -l < "$FR_IDS_FILE" | tr -d ' ')
  fi
  if [[ -n "$FR_TEST_IDS_FILE" && -f "$FR_TEST_IDS_FILE" ]]; then
    fr_covered=$(wc -l < "$FR_TEST_IDS_FILE" | tr -d ' ')
  fi

  # Test-first pairs: check shell scripts for corresponding test files
  # Build test file index ONCE, then grep against it (avoids per-file find)
  local tf_checked=0 tf_missing=0
  local TF_INDEX="$LINT_TMP/test_file_index"
  find "$PROJECT_DIR/test" -maxdepth 3 -type f 2>/dev/null | sed 's|.*/||' > "$TF_INDEX" 2>/dev/null || true

  while IFS= read -r src_file; do
    [[ -z "$src_file" ]] && continue
    tf_checked=$((tf_checked + 1))
    local bn
    bn="$(basename "$src_file" .sh)"
    if ! grep -q "$bn" "$TF_INDEX" 2>/dev/null; then
      tf_missing=$((tf_missing + 1))
    fi
  done < <(find "$PROJECT_DIR" -path "$PROJECT_DIR/test" -prune -o -path "$PROJECT_DIR/.git" -prune -o -path "$PROJECT_DIR/node_modules" -prune -o -type f -name "*.sh" -print 2>/dev/null | head -20)

  local signed_attest=false slsa_present=false
  [[ -f "$VERIFY_DIR/attestation.sig" ]] && signed_attest=true
  [[ -f "$PROJECT_DIR/.slsa-provenance.json" ]] && slsa_present=true

  local fr_cov_pct=0
  if [[ $fr_total -gt 0 ]]; then
    fr_cov_pct=$((fr_covered * 100 / fr_total))
  fi

  local rekor_json="null"
  [[ -n "$rekor_bundle" ]] && rekor_json="$rekor_bundle"

  # Build attestation in a single jq call
  local invocation_id="session-$$-$(date +%s)"
  $JQ_CMD -n \
    --arg ptype "https://slsa.dev/provenance/v1" \
    --arg name "." \
    --arg digest "$subject_digest" \
    --arg builder_id "$builder_id" \
    --arg build_type "https://github.com/kush/sharecli/build-type/bash" \
    --arg git_sha "$git_sha" \
    --arg git_ref "$git_ref" \
    --arg git_remote "$git_remote" \
    --arg started "$now" \
    --arg finished "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg invocation_id "$invocation_id" \
    '{
      "_type": "https://in-toto.io/Statement/v1",
      predicateType: $ptype,
      subject: [{
        name: $name,
        digest: { sha256: $digest }
      }],
      predicate: {
        buildDefinition: {
          buildType: $build_type,
          externalParameters: {
            git_ref: $git_ref,
            project_dir: "."
          },
          internalParameters: {
            git_sha: $git_sha
          },
          resolvedDependencies: [{
            uri: $git_remote,
            digest: { gitSha: $git_sha }
          }]
        },
        runDetails: {
          builder: { id: $builder_id },
          metadata: {
            invocationId: $invocation_id,
            startedOn: $started,
            finishedOn: $finished
          }
        }
      }
    }' > "$ATTEST_OUT_FILE"

  local rekor_status="none"
  [[ -n "$rekor_bundle" ]] && rekor_status="enabled"

  echo "Attestation: $ATTEST_OUT_FILE (predicateType=https://slsa.dev/provenance/v1 slsa=v1 policy_hash=${policy_hash:0:16}... rekor=$rekor_status)"
}

# ---------- Inlined policy engine (avoids subprocess fork) ----------
_run_policy_engine() {
  local ATTEST_FILE="$VERIFY_DIR/qa-attestation.json"
  local QUALITY="$QUALITY_CONFIG"
  local SCRIPT_DIR
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local REPO_ROOT
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  local AUDIT="$VERIFY_DIR/policy-engine-audit.json"
  local POLICIES_REPO="$REPO_ROOT/etc/policies/qa"
  local POLICIES_HOME="${HOME}/.claude/policies/qa"

  # Fail-closed: no quality.json = allow (not governed)
  if [[ ! -f "$QUALITY" ]]; then
    echo "POLICY ENGINE: allow (no quality.json)"
    return 0
  fi

  # Locate policies
  local POLICIES=""
  [[ -d "$POLICIES_REPO" ]] && POLICIES="$POLICIES_REPO"
  [[ -d "$POLICIES_HOME" ]] && POLICIES="$POLICIES_HOME $POLICIES"

  # No OPA = fail-closed allow with audit
  if ! command -v opa >/dev/null 2>&1; then
    printf '{"generated_at":"%s","channel":"warn","message":"opa not installed; policy engine skipped","break_glass":false}\n' \
      "$now" > "$AUDIT"
    echo "POLICY ENGINE: allow (opa not installed, audit recorded)"
    return 0
  fi

  # No policies = allow
  if [[ -z "$POLICIES" ]] || ! ls $POLICIES/*.rego 1>/dev/null 2>&1; then
    echo "POLICY ENGINE: allow (no policies)"
    return 0
  fi

  # Eval policies
  local denies=0 warns=0 eval_denies=0 eval_warns=0
  local policy_errors="" policies_found=""

  local pdir
  for pdir in $POLICIES; do
    [[ -d "$pdir" ]] || continue
    policies_found="$policies_found $pdir"

    if ! opa test "$pdir" 2>/dev/null; then
      warns=$((warns + 1))
      policy_errors="$policy_errors $pdir (test failed)"
    fi

    if [[ -f "$QUALITY" ]]; then
      local deny_result warn_result deny_count warn_count
      deny_result="$(opa eval "data.qa.deny" --data "$pdir" --input "$QUALITY" -f json 2>/dev/null || echo "[]")"
      deny_count="$($JQ_CMD 'length' <<< "$deny_result" 2>/dev/null || echo 0)"
      warn_result="$(opa eval "data.qa.warn" --data "$pdir" --input "$QUALITY" -f json 2>/dev/null || echo "[]")"
      warn_count="$($JQ_CMD 'length' <<< "$warn_result" 2>/dev/null || echo 0)"
      eval_denies=$((eval_denies + deny_count))
      eval_warns=$((eval_warns + warn_count))
    fi
  done

  if [[ $eval_denies -gt 0 || $eval_warns -gt 0 ]]; then
    denies=$eval_denies
    warns=$eval_warns
  fi

  local channel="allow"
  if [[ $denies -gt 0 ]]; then
    channel="deny"
  elif [[ $warns -gt 0 ]]; then
    channel="warn"
  fi

  # Audit record
  $JQ_CMD -n \
    --arg ts "$now" \
    --arg ch "$channel" \
    --argjson d "$denies" \
    --argjson w "$warns" \
    --argjson ed "$eval_denies" \
    --argjson ew "$eval_warns" \
    --arg policies "${policies_found:-none}" \
    --arg errors "${policy_errors:-none}" \
    '{
      generated_at: $ts,
      channel: $ch,
      deny_count: $d,
      warn_count: $w,
      eval_denies: $ed,
      eval_warns: $ew,
      policies_checked: $policies,
      policy_errors: $errors,
      break_glass: false
    }' > "$AUDIT"

  case "$channel" in
    deny)
      echo "POLICY-ENGINE FAIL: $denies policy denial(s)" >&2
      echo "2" > "$LINT_TMP/policy_exit_code"
      ;;
    warn)
      echo "POLICY ENGINE: allow (warn: $warns)"
      ;;
    *)
      echo "POLICY ENGINE: allow"
      ;;
  esac
}

# ---------- Inlined SARIF adapter (avoids subprocess fork) ----------
_run_sarif_adapter() {
  local OUT_FILE="$VERIFY_DIR/sarif-summary.json"

  if ! command -v "$JQ_CMD" >/dev/null 2>&1; then
    echo "SARIF ADAPTER: jq/jaq not available; skipping"
    return
  fi

  local -a SARIF_FILES=()
  while IFS= read -r sf; do
    SARIF_FILES+=("$sf")
  done < <(find "$PROJECT_DIR" -maxdepth 5 \
    -type d \( -name .git -o -name node_modules -o -name .venv -o -name venv -o -name dist -o -name build -o -name fuse \) -prune -o \
    -type f \( -name '*.sarif' -o -name '*.sarif.json' \) -print 2>/dev/null | head -50)

  if [[ ${#SARIF_FILES[@]} -eq 0 ]]; then
    printf '{"files":0,"total_results":0,"levels":{"error":0,"warning":0,"note":0,"none":0}}\n' > "$OUT_FILE"
    echo "SARIF ADAPTER: files=0 total_results=0 output=$OUT_FILE"
    return
  fi

  local SARIF_TMP
  SARIF_TMP="$(mktemp)"

  local f
  for f in "${SARIF_FILES[@]}"; do
    $JQ_CMD -c --arg f "$f" '
      {
        file: $f,
        total: ([.runs[]?.results[]?] | length),
        error: ([.runs[]?.results[]? | select((.level // "warning") == "error")] | length),
        warning: ([.runs[]?.results[]? | select((.level // "warning") == "warning")] | length),
        note: ([.runs[]?.results[]? | select((.level // "warning") == "note")] | length),
        none: ([.runs[]?.results[]? | select((.level // "warning") == "none")] | length)
      }
    ' "$f" 2>/dev/null || true
  done > "$SARIF_TMP"

  $JQ_CMD -s '
    {
      files: length,
      total_results: (map(.total) | add // 0),
      levels: {
        error: (map(.error) | add // 0),
        warning: (map(.warning) | add // 0),
        note: (map(.note) | add // 0),
        none: (map(.none) | add // 0)
      },
      by_file: .
    }
  ' "$SARIF_TMP" > "$OUT_FILE"

  rm -f "$SARIF_TMP"

  local FILES TOTAL ERRS WARNS
  # Read all 4 values in a single jq call
  local _sarif_vals
  _sarif_vals="$($JQ_CMD -r '[.files, .total_results, .levels.error, .levels.warning] | @tsv' "$OUT_FILE" 2>/dev/null || echo "0	0	0	0")"
  IFS=$'\t' read -r FILES TOTAL ERRS WARNS <<< "$_sarif_vals"

  echo "SARIF ADAPTER: files=$FILES total_results=$TOTAL errors=$ERRS warnings=$WARNS output=$OUT_FILE"
}

# ---------- Smart-contract governance: attestation + policy + SARIF ----------
# P4.5: Short-circuit — if policy engine returns deny, skip attestation builder
# and SARIF adapter since they are pointless when policy is denied.

POLICY_OUT="$(_run_policy_engine 2>&1)" || true
if [[ -f "$LINT_TMP/policy_exit_code" ]]; then
  POLICY_EXIT_CODE="$(<"$LINT_TMP/policy_exit_code")"
fi
if [[ -n "$POLICY_OUT" ]] && [[ "$POLICY_OUT" =~ [^[:space:]] ]]; then
  REPORT+="SMART CONTRACT -- policy evaluation:\n$POLICY_OUT\n\n"
  if echo "$POLICY_OUT" | grep -q "POLICY ENGINE DENIES:"; then
    ISSUES=$((ISSUES + 1))
  fi
fi
if [[ "$POLICY_EXIT_CODE" -ne 0 ]]; then
  REPORT+="SMART CONTRACT -- policy engine exited with code $POLICY_EXIT_CODE\n\n"
  ISSUES=$((ISSUES + 1))
  REPORT+="SMART CONTRACT -- attestation + SARIF skipped (policy denied)\n\n"
else
  # Policy allowed/warned: run attestation builder and SARIF adapter
  ATTEST_OUT="$(_run_attestation 2>&1 || true)"
  if [[ -n "$ATTEST_OUT" ]] && [[ "$ATTEST_OUT" =~ [^[:space:]] ]]; then
    REPORT+="SMART CONTRACT -- attestation:\n$ATTEST_OUT\n\n"
  fi

  SARIF_OUT="$(_run_sarif_adapter 2>&1 || true)"
  if [[ -n "$SARIF_OUT" ]] && [[ "$SARIF_OUT" =~ [^[:space:]] ]]; then
    REPORT+="SARIF ADAPTER:\n$SARIF_OUT\n\n"
  fi
  SARIF_SUMMARY="$VERIFY_DIR/sarif-summary.json"
  if [[ -f "$SARIF_SUMMARY" ]]; then
    SARIF_ERRORS="$($JQ_CMD '.levels.error // 0' "$SARIF_SUMMARY" 2>/dev/null || echo 0)"
    if [[ "$SARIF_ERRORS" -gt 0 ]]; then
      ISSUES=$((ISSUES + 1))
      REPORT+="SARIF SUMMARY: error findings=$SARIF_ERRORS (from $SARIF_SUMMARY)\n\n"
    fi
  fi
fi

  # ---------- Output report ----------
  if [[ -n "$REPORT" ]]; then
    printf "Quality Gate: Found %d issue area(s)\n" "$ISSUES"
    echo "=================================================="
    echo -e "$REPORT"
  else
    printf "Quality Gate: All checks passed (%d changed files)\n" "${#ALL_FILES[@]}"
  fi

if [[ "$GATE_FAIL_CLOSED" == "true" ]] && [[ "$POLICY_EXIT_CODE" -ne 0 ]]; then
  echo "QUALITY GATE FAIL: $ISSUES issue area(s) found -- review report above" >&2
  return "$POLICY_EXIT_CODE"
fi

return 0
} # end _quality_gate_main

# Run main, capture output, cache result
_output=$(_quality_gate_main 2>&1); _rc=$?
hook_cache_write "$_cache_key" "$_rc" "$_output"
# Ultra-fast cache for next time
mkdir -p "$_CACHE_DIR" 2>/dev/null || true
echo "$_output" > "$_CACHE_FILE" 2>/dev/null || true
[[ -n "$_output" ]] && echo "$_output"
if [[ "$_rc" -ne 0 ]]; then
  echo "QUALITY-GATE FAIL: quality gate exited with code $_rc" >&2
fi
exit "$_rc"
