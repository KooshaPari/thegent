#!/usr/bin/env bash
# complexity-ratchet.sh — PostToolUse hook (Edit|Write) + Stop hook
# Tracks code complexity metrics and enforces a ratchet: complexity may not
# increase beyond thresholds. Measures function length, file length, nesting
# depth, cyclomatic complexity proxies, and cognitive complexity.
# Advisory only (always exits 0). Budget: <2s for single file.
#
# Optimized: single-pass awk per file, batched jq config/baseline reads,
# single jq baseline write. ~15 spawns for 10 files (down from ~85).
set -euo pipefail

# Ultra-fast cache check — before sourcing anything (Stop mode only).
# Uses HEAD_SHA pre-computed by stop-dispatcher. 10-min TTL for better reuse.
# Only triggers when HEAD_SHA is set (Stop dispatcher), not PostToolUse.
_CACHE_DIR="${TMPDIR:-/tmp}/claude-hook-cache-$(id -u)"
_CACHE_TTL="${HOOK_CACHE_TTL:-600}"
if [[ -n "${HEAD_SHA:-}" ]]; then
  _CACHE_FILE="${_CACHE_DIR}/complexity-ratchet-${HEAD_SHA}.result"
  if [[ -f "$_CACHE_FILE" ]]; then
    _age=$(( $(date +%s) - $(stat -f '%m' "$_CACHE_FILE" 2>/dev/null || stat -c '%Y' "$_CACHE_FILE" 2>/dev/null || echo 0) ))
    if (( _age < _CACHE_TTL )); then
      cat "$_CACHE_FILE"
      exit 0
    fi
  fi
else
  _CACHE_FILE=""
fi

HOOK_NAME="COMPLEXITY-RATCHET"
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# --- P1 optimization: Skip in Stop mode if no source files changed ---
# Only apply to Stop hooks (HEAD_SHA set), not PostToolUse (single file check)
if [[ -n "${HEAD_SHA:-}" ]] && ! any_source_changed; then
  echo "COMPLEXITY-RATCHET: skipped (no source files changed)"
  exit 0
fi

RATCHET_FILE="$HOME/.claude/.complexity-ratchet.json"
mkdir -p "$HOME/.claude"

# Clean up stale .tmp file on exit
trap 'rm -f "${RATCHET_FILE}.tmp"' EXIT

# ---------- Thresholds (configurable via .claude/quality.json) ----------
# Single jq call to read all 5 thresholds (was 5 separate jq invocations)
MAX_FILE_LINES=500
MAX_FUNCTION_LINES=50
MAX_NESTING_DEPTH=5
MAX_CYCLOMATIC=15
MAX_COGNITIVE=15

if [[ -f "$QUALITY_CONFIG" ]] && $JQ_CMD empty "$QUALITY_CONFIG" 2>/dev/null; then
  read -r MAX_FILE_LINES MAX_FUNCTION_LINES MAX_NESTING_DEPTH MAX_CYCLOMATIC MAX_COGNITIVE < <(
    $JQ_CMD -r '[
      .complexity.max_file_lines // 500,
      .complexity.max_function_lines // 50,
      .complexity.max_nesting_depth // 5,
      .complexity.max_cyclomatic // 15,
      .complexity.max_cognitive // 15
    ] | @tsv' "$QUALITY_CONFIG" 2>/dev/null
  ) || { MAX_FILE_LINES=500; MAX_FUNCTION_LINES=50; MAX_NESTING_DEPTH=5; MAX_CYCLOMATIC=15; MAX_COGNITIVE=15; }
fi

# ---------- Load baseline once into shell variable ----------
_baseline_content=""
_baseline_loaded=false

_load_baseline() {
  if [[ "$_baseline_loaded" == "true" ]]; then return; fi
  _baseline_loaded=true
  if [[ -f "$RATCHET_FILE" ]]; then
    _baseline_content="$(<"$RATCHET_FILE")" 2>/dev/null || _baseline_content='{"files":{}}'
    # Validate JSON
    if ! $JQ_CMD empty <<< "$_baseline_content" 2>/dev/null; then
      _baseline_content='{"files":{}}'
    fi
  else
    _baseline_content='{"files":{}}'
  fi
}

# Read a file's baseline metrics from the in-memory baseline (single jq call)
# Returns: cyclomatic file_lines (tab-separated)
_get_baseline() {
  local file_key="$1"
  $JQ_CMD -r --arg f "$file_key" \
    '[(.files[$f].cyclomatic // 0), (.files[$f].file_lines // 0)] | @tsv' \
    <<< "$_baseline_content" 2>/dev/null || printf '0\t0'
}

# Read baseline metrics for multiple files in a single jq call
# Args: file keys as separate arguments
# Output: one line per file: file_key\tcyclomatic\tfile_lines
_get_baselines_batch() {
  local files_json
  files_json=$(printf '%s\n' "$@" | $JQ_CMD -Rsc 'split("\n") | map(select(. != ""))')
  $JQ_CMD -r --argjson keys "$files_json" '
    . as $root |
    $keys[] |
    . as $k |
    [$k, ($root.files[$k].cyclomatic // 0), ($root.files[$k].file_lines // 0)] |
    @tsv
  ' <<< "$_baseline_content" 2>/dev/null || { echo "COMPLEXITY-RATCHET: batch baseline read failed ($?)" >&2; true; }
}

# ---------- Single-pass complexity measurement ----------
# Measures all 4 metrics (cyclomatic, cognitive, nesting, long functions) + line count
# in a single awk invocation per file. Returns: file_lines:cyclomatic:cognitive:nesting:long_funcs
#
# P4.4: For batch mode (Stop), measure_files_batch processes multiple same-language
# files in a single awk with FNR==1 boundary tracking. One awk per language group
# instead of one awk per file.
# Output: one line per file: FILENAME\tfile_lines:cyclomatic:cognitive:nesting:long_funcs

measure_file() {
  local file="$1"
  local max_func_lines="$2"
  local ext
  ext="$(file_ext "$file")"

  case "$ext" in
    py)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; max_nest=0; long_funcs=0; func_start=0 }
        /^[[:space:]]*$/ { next }
        /^[[:space:]]*#/ { next }
        {
          # Indentation-based nesting for Python
          match($0, /^[[:space:]]*/); spaces=RLENGTH; level=int(spaces/4)
          if (level > max_nest) max_nest = level

          # Cyclomatic: count branching keywords
          line = $0
          # Count each keyword occurrence
          n = gsub(/\<(if|elif|else|for|while|except|and|or|assert|with)\>/, "&", line)
          cyc += n

          # Cognitive: branching weighted by nesting
          if ($0 ~ /\<(if|elif|else|for|while|except|with)\>/) cog += (1 + level)
          if ($0 ~ /\<(and|or)\>/) cog += 1

          # Long function detection
          if ($0 ~ /^[[:space:]]*(def |class |async def )/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          # Check last function
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    sh|bash)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; depth=0; max_nest=0; long_funcs=0; func_start=0 }
        {
          # Cyclomatic
          line = $0
          n = gsub(/\<(if|elif|else|for|while|until|case)\>/, "&", line)
          cyc += n
          if ($0 ~ /(\|\||&&)/) { m=$0; gsub(/[^|&]/, "", m); cyc += int(length(m)/2) }

          # Cognitive: structural keywords add 1+depth, logical ops add 1
          if ($0 ~ /\<(if|for|while|until|case)\>/) { cog += (1 + depth); depth++ }
          if ($0 ~ /\<(fi|done|esac)\>/) { if (depth > 0) depth-- }
          if ($0 ~ /\<(elif|else)\>/) { cog += (1 + depth) }
          if ($0 ~ /(\|\||&&)/) cog += 1

          # Track max nesting separately (use a parallel counter)
          nest_line = $0
          n_open = gsub(/\<(if|for|while|case)\>/, "&", nest_line)
          for (i=0; i<n_open; i++) { nest_depth++ }
          if (nest_depth > max_nest) max_nest = nest_depth
          n_close = gsub(/\<(fi|done|esac)\>/, "&", nest_line)
          for (i=0; i<n_close; i++) { if (nest_depth > 0) nest_depth-- }

          # Long function detection
          if ($0 ~ /^[[:space:]]*(function[[:space:]]+[a-zA-Z_]|[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\(\))/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    ts|tsx|js|jsx)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; depth=0; max_nest=0; long_funcs=0; func_start=0 }
        {
          # Brace-based nesting
          for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == "}") { if (depth > 0) depth-- }
          }

          # Cyclomatic
          line = $0
          n = gsub(/\<(if|else|for|while|do|switch|case|catch|throw)\>/, "&", line)
          cyc += n
          if ($0 ~ /(\?\?|&&|\|\|)/) { m=$0; gsub(/[^?&|]/, "", m); cyc += int(length(m)/2) }

          # Cognitive
          if ($0 ~ /\<(if|else|for|while|do|switch|case|catch)\>/) cog += (1 + depth)
          if ($0 ~ /(\?\?|&&|\|\|)/) cog += 1

          # Long function detection
          if ($0 ~ /^[[:space:]]*(function[[:space:]]|export[[:space:]]+(default[[:space:]]+)?function|const[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]*(async[[:space:]]+)?\()/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    go)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; depth=0; max_nest=0; long_funcs=0; func_start=0 }
        {
          for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == "}") { if (depth > 0) depth-- }
          }

          line = $0
          n = gsub(/\<(if|else|for|switch|case|select)\>/, "&", line)
          cyc += n
          if ($0 ~ /(&&|\|\|)/) { m=$0; gsub(/[^&|]/, "", m); cyc += int(length(m)/2) }

          if ($0 ~ /\<(if|else|for|switch|case|select)\>/) cog += (1 + depth)
          if ($0 ~ /(&&|\|\|)/) cog += 1

          if ($0 ~ /^[[:space:]]*func[[:space:]]/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    rs)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; depth=0; max_nest=0; long_funcs=0; func_start=0 }
        {
          for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == "}") { if (depth > 0) depth-- }
          }

          line = $0
          n = gsub(/\<(if|else|for|while|loop|match)\>/, "&", line)
          cyc += n
          if ($0 ~ /(&&|\|\|)/) { m=$0; gsub(/[^&|]/, "", m); cyc += int(length(m)/2) }

          if ($0 ~ /\<(if|else|for|while|loop|match)\>/) cog += (1 + depth)
          if ($0 ~ /(&&|\|\|)/) cog += 1

          if ($0 ~ /^[[:space:]]*(pub[[:space:]]+)?(async[[:space:]]+)?fn[[:space:]]/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    rb)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; max_nest=0; long_funcs=0; func_start=0 }
        /^[[:space:]]*$/ { next }
        /^[[:space:]]*#/ { next }
        {
          match($0, /^[[:space:]]*/); spaces=RLENGTH; level=int(spaces/2)
          if (level > max_nest) max_nest = level

          line = $0
          n = gsub(/\<(if|elsif|else|unless|for|while|until|case|when|rescue|and|or)\>/, "&", line)
          cyc += n

          if ($0 ~ /\<(if|elsif|else|unless|for|while|until|case|when|rescue)\>/) cog += (1 + level)
          if ($0 ~ /\<(and|or)\>/) cog += 1

          if ($0 ~ /^[[:space:]]*def[[:space:]]/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    java|kt)
      awk -v max_func="$max_func_lines" '
        BEGIN { cyc=0; cog=0; depth=0; max_nest=0; long_funcs=0; func_start=0 }
        {
          for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == "}") { if (depth > 0) depth-- }
          }

          line = $0
          n = gsub(/\<(if|else|for|while|do|switch|case|catch|throw)\>/, "&", line)
          cyc += n
          if ($0 ~ /(&&|\|\|)/) { m=$0; gsub(/[^&|]/, "", m); cyc += int(length(m)/2) }

          if ($0 ~ /\<(if|else|for|while|do|switch|case|catch|throw)\>/) cog += (1 + depth)
          if ($0 ~ /(&&|\|\|)/) cog += 1

          if ($0 ~ /^[[:space:]]*(public|private|protected|internal|override|fun|static)[[:space:]]/) {
            if (func_start > 0) {
              body = NR - func_start
              if (body > max_func) long_funcs++
            }
            func_start = NR
          }
        }
        END {
          if (func_start > 0) {
            body = NR - func_start
            if (body > max_func) long_funcs++
          }
          print NR ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
        }
      ' "$file" 2>/dev/null || echo "0:0:0:0:0"
      ;;
    *)
      # Unsupported extension: return zeros with line count
      local lc
      lc=$(awk 'END{print NR}' "$file" 2>/dev/null) || lc=0
      echo "${lc}:0:0:0:0"
      ;;
  esac
}

# P4.4: Batch awk — process multiple same-language files in one awk invocation.
# Usage: measure_files_batch <ext> <max_func_lines> file1 file2 ...
# Output: one line per file: FILENAME\tfile_lines:cyclomatic:cognitive:nesting:long_funcs
# Uses FNR==1 for file-boundary tracking to reset counters between files.
measure_files_batch() {
  local ext="$1" max_func="$2"; shift 2
  [[ $# -eq 0 ]] && return

  # Common print_results + reset logic (injected into each awk script)
  local AWK_BOUNDARY='
    function print_results() {
      if (func_start > 0) {
        body = file_lines - func_start
        if (body > max_func) long_funcs++
      }
      print fname "\t" file_lines ":" cyc ":" cog+0 ":" max_nest ":" long_funcs
    }
    function reset() {
      cyc=0; cog=0; max_nest=0; long_funcs=0; func_start=0; file_lines=0
    }
    FNR==1 { if (NR!=1) print_results(); reset(); fname=FILENAME }
  '
  local AWK_END='
    END { print_results() }
  '

  case "$ext" in
    py)
      awk -v max_func="$max_func" "
        $AWK_BOUNDARY
        /^[[:space:]]*\$/ { file_lines=FNR; next }
        /^[[:space:]]*#/ { file_lines=FNR; next }
        {
          file_lines=FNR
          match(\$0, /^[[:space:]]*/); spaces=RLENGTH; level=int(spaces/4)
          if (level > max_nest) max_nest = level
          line = \$0
          n = gsub(/\<(if|elif|else|for|while|except|and|or|assert|with)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /\<(if|elif|else|for|while|except|with)\>/) cog += (1 + level)
          if (\$0 ~ /\<(and|or)\>/) cog += 1
          if (\$0 ~ /^[[:space:]]*(def |class |async def )/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    sh|bash)
      awk -v max_func="$max_func" "
        BEGIN { depth=0; nest_depth=0 }
        $AWK_BOUNDARY
        {
          file_lines=FNR
          line = \$0
          n = gsub(/\<(if|elif|else|for|while|until|case)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /(\\|\\||&&)/) { m=\$0; gsub(/[^|&]/, \"\", m); cyc += int(length(m)/2) }
          if (\$0 ~ /\<(if|for|while|until|case)\>/) { cog += (1 + depth); depth++ }
          if (\$0 ~ /\<(fi|done|esac)\>/) { if (depth > 0) depth-- }
          if (\$0 ~ /\<(elif|else)\>/) { cog += (1 + depth) }
          if (\$0 ~ /(\\|\\||&&)/) cog += 1
          nest_line = \$0
          n_open = gsub(/\<(if|for|while|case)\>/, \"&\", nest_line)
          for (i=0; i<n_open; i++) { nest_depth++ }
          if (nest_depth > max_nest) max_nest = nest_depth
          n_close = gsub(/\<(fi|done|esac)\>/, \"&\", nest_line)
          for (i=0; i<n_close; i++) { if (nest_depth > 0) nest_depth-- }
          if (\$0 ~ /^[[:space:]]*(function[[:space:]]+[a-zA-Z_]|[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*\\(\\))/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    ts|tsx|js|jsx)
      awk -v max_func="$max_func" "
        BEGIN { depth=0 }
        $AWK_BOUNDARY
        {
          file_lines=FNR
          for (i=1; i<=length(\$0); i++) {
            c = substr(\$0, i, 1)
            if (c == \"{\") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == \"}\") { if (depth > 0) depth-- }
          }
          line = \$0
          n = gsub(/\<(if|else|for|while|do|switch|case|catch|throw)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /(\\?\\?|&&|\\|\\|)/) { m=\$0; gsub(/[^?&|]/, \"\", m); cyc += int(length(m)/2) }
          if (\$0 ~ /\<(if|else|for|while|do|switch|case|catch)\>/) cog += (1 + depth)
          if (\$0 ~ /(\\?\\?|&&|\\|\\|)/) cog += 1
          if (\$0 ~ /^[[:space:]]*(function[[:space:]]|export[[:space:]]+(default[[:space:]]+)?function|const[[:space:]]+[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]*=[[:space:]]*(async[[:space:]]+)?\\()/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    go)
      awk -v max_func="$max_func" "
        BEGIN { depth=0 }
        $AWK_BOUNDARY
        {
          file_lines=FNR
          for (i=1; i<=length(\$0); i++) {
            c = substr(\$0, i, 1)
            if (c == \"{\") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == \"}\") { if (depth > 0) depth-- }
          }
          line = \$0
          n = gsub(/\<(if|else|for|switch|case|select)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /(&&|\\|\\|)/) { m=\$0; gsub(/[^&|]/, \"\", m); cyc += int(length(m)/2) }
          if (\$0 ~ /\<(if|else|for|switch|case|select)\>/) cog += (1 + depth)
          if (\$0 ~ /(&&|\\|\\|)/) cog += 1
          if (\$0 ~ /^[[:space:]]*func[[:space:]]/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    rs)
      awk -v max_func="$max_func" "
        BEGIN { depth=0 }
        $AWK_BOUNDARY
        {
          file_lines=FNR
          for (i=1; i<=length(\$0); i++) {
            c = substr(\$0, i, 1)
            if (c == \"{\") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == \"}\") { if (depth > 0) depth-- }
          }
          line = \$0
          n = gsub(/\<(if|else|for|while|loop|match)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /(&&|\\|\\|)/) { m=\$0; gsub(/[^&|]/, \"\", m); cyc += int(length(m)/2) }
          if (\$0 ~ /\<(if|else|for|while|loop|match)\>/) cog += (1 + depth)
          if (\$0 ~ /(&&|\\|\\|)/) cog += 1
          if (\$0 ~ /^[[:space:]]*(pub[[:space:]]+)?(async[[:space:]]+)?fn[[:space:]]/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    rb)
      awk -v max_func="$max_func" "
        $AWK_BOUNDARY
        /^[[:space:]]*\$/ { file_lines=FNR; next }
        /^[[:space:]]*#/ { file_lines=FNR; next }
        {
          file_lines=FNR
          match(\$0, /^[[:space:]]*/); spaces=RLENGTH; level=int(spaces/2)
          if (level > max_nest) max_nest = level
          line = \$0
          n = gsub(/\<(if|elsif|else|unless|for|while|until|case|when|rescue|and|or)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /\<(if|elsif|else|unless|for|while|until|case|when|rescue)\>/) cog += (1 + level)
          if (\$0 ~ /\<(and|or)\>/) cog += 1
          if (\$0 ~ /^[[:space:]]*def[[:space:]]/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    java|kt)
      awk -v max_func="$max_func" "
        BEGIN { depth=0 }
        $AWK_BOUNDARY
        {
          file_lines=FNR
          for (i=1; i<=length(\$0); i++) {
            c = substr(\$0, i, 1)
            if (c == \"{\") { depth++; if (depth > max_nest) max_nest = depth }
            if (c == \"}\") { if (depth > 0) depth-- }
          }
          line = \$0
          n = gsub(/\<(if|else|for|while|do|switch|case|catch|throw)\>/, \"&\", line)
          cyc += n
          if (\$0 ~ /(&&|\\|\\|)/) { m=\$0; gsub(/[^&|]/, \"\", m); cyc += int(length(m)/2) }
          if (\$0 ~ /\<(if|else|for|while|do|switch|case|catch|throw)\>/) cog += (1 + depth)
          if (\$0 ~ /(&&|\\|\\|)/) cog += 1
          if (\$0 ~ /^[[:space:]]*(public|private|protected|internal|override|fun|static)[[:space:]]/) {
            if (func_start > 0) { body = FNR - func_start; if (body > max_func) long_funcs++ }
            func_start = FNR
          }
        }
        $AWK_END
      " "$@" 2>/dev/null || true
      ;;
    *)
      # Unsupported: just count lines for each file
      awk '
        FNR==1 { if (NR!=1) print fname "\t" file_lines ":0:0:0:0"; file_lines=0; fname=FILENAME }
        { file_lines=FNR }
        END { print fname "\t" file_lines ":0:0:0:0" }
      ' "$@" 2>/dev/null || true
      ;;
  esac
}

# ---------- Mode: single file (PostToolUse) ----------
if [[ -n "$FILE_PATH" ]] && [[ -f "$FILE_PATH" ]]; then
  EXT="$(file_ext "$FILE_PATH")"
  case "$EXT" in
    py|sh|bash|ts|tsx|js|jsx|go|rs|rb|php|java|kt|swift) ;;
    *) exit 0 ;;
  esac
  case "$FILE_PATH" in
    */node_modules/*|*/.git/*|*/vendor/*|*/__pycache__/*|*/.venv/*|*/dist/*|*/build/*) exit 0 ;;
  esac

  BASENAME="$(file_basename "$FILE_PATH")"
  # Single awk pass measures all metrics (was 4 separate function calls)
  METRICS=$(measure_file "$FILE_PATH" "$MAX_FUNCTION_LINES")
  IFS=':' read -r FILE_LINES CYCLOMATIC COGNITIVE NESTING LONG_FUNCS <<< "$METRICS"

  WARNINGS=()

  [[ "$FILE_LINES" -gt "$MAX_FILE_LINES" ]] && \
    WARNINGS+=("FILE_LENGTH: ${BASENAME} has ${FILE_LINES} lines (max: ${MAX_FILE_LINES})")

  [[ "$CYCLOMATIC" -gt "$MAX_CYCLOMATIC" ]] && \
    WARNINGS+=("CYCLOMATIC: ${BASENAME} has complexity score ${CYCLOMATIC} (max: ${MAX_CYCLOMATIC})")

  [[ "$COGNITIVE" -gt "$MAX_COGNITIVE" ]] && \
    WARNINGS+=("COGNITIVE: ${BASENAME} has cognitive score ${COGNITIVE} (max: ${MAX_COGNITIVE})")

  [[ "$NESTING" -gt "$MAX_NESTING_DEPTH" ]] && \
    WARNINGS+=("NESTING_DEPTH: ${BASENAME} has nesting depth ${NESTING} (max: ${MAX_NESTING_DEPTH})")

  [[ "${LONG_FUNCS:-0}" -gt 0 ]] && \
    WARNINGS+=("FUNCTION_LENGTH: ${BASENAME} has ${LONG_FUNCS} function(s) exceeding ${MAX_FUNCTION_LINES} lines")

  # Ratchet check: load baseline once, read this file's entry (single jq call)
  _load_baseline
  read -r PREV_CC PREV_LINES < <(_get_baseline "$FILE_PATH") || { PREV_CC=0; PREV_LINES=0; }

  if [[ "$PREV_CC" -gt 0 ]] && [[ "$CYCLOMATIC" -gt "$PREV_CC" ]]; then
    INCREASE=$((CYCLOMATIC - PREV_CC))
    [[ "$INCREASE" -gt 3 ]] && \
      WARNINGS+=("RATCHET: ${BASENAME} cyclomatic complexity increased by ${INCREASE} (${PREV_CC} -> ${CYCLOMATIC})")
  fi

  if [[ "$PREV_LINES" -gt 0 ]] && [[ "$FILE_LINES" -gt "$PREV_LINES" ]]; then
    INCREASE=$((FILE_LINES - PREV_LINES))
    [[ "$INCREASE" -gt 50 ]] && \
      WARNINGS+=("RATCHET: ${BASENAME} grew by ${INCREASE} lines (${PREV_LINES} -> ${FILE_LINES})")
  fi

  # Update ratchet baseline: single jq write (in-memory -> file)
  $JQ_CMD --arg f "$FILE_PATH" \
     --argjson fl "$FILE_LINES" \
     --argjson cc "$CYCLOMATIC" \
     --argjson cg "$COGNITIVE" \
     --argjson nd "$NESTING" \
     --argjson lf "${LONG_FUNCS:-0}" \
     --arg ts "$now" \
     '.files[$f] = {file_lines: $fl, cyclomatic: $cc, cognitive: $cg, nesting_depth: $nd, long_functions: $lf, updated_at: $ts}' \
     <<< "$_baseline_content" > "${RATCHET_FILE}.tmp" && mv "${RATCHET_FILE}.tmp" "$RATCHET_FILE"

  if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo "Complexity Ratchet (${#WARNINGS[@]} warning(s) for ${BASENAME}):"
    for w in "${WARNINGS[@]}"; do
      echo "  $w"
    done
  fi

  exit 0
fi

# ---------- Mode: full scan (Stop event, no FILE_PATH) ----------

# Cache already checked at top of file (ultra-fast, pre-common.sh).
# Build changed files list for analysis.
_shared_changed_files=$(hook_shared_changed_files 2>/dev/null || true)

# Exclude build artifacts, coverage caches, and minified files that waste awk time.
CHANGED_FILES=""
CHANGED_FILES=$(echo "$_shared_changed_files" \
  | grep -E '\.(py|sh|bash|ts|js|tsx|jsx|go|rs|java|kt|rb)$' \
  | grep -vE '(coverage-cache|coverage/|\.min\.(js|css)|node_modules/|vendor/|__pycache__/|\.venv/|dist/|build/|out/|target/)' \
  || true)
unset _shared_changed_files

# Fallback to session log
if [[ -z "$CHANGED_FILES" ]] && [[ -f "$CHANGE_LOG" ]]; then
  CHANGED_FILES=$(grep -oE '[^ ]+\.(py|sh|bash|ts|js|tsx|jsx|go|rs|java|kt|rb)' \
    "$CHANGE_LOG" 2>/dev/null | sort_unique || true)
fi

[[ -z "$CHANGED_FILES" ]] && exit 0

_complexity_stop_main() {
# Load baseline once for all files (was: 1 jq read per file)
_load_baseline

# P4.4: Group files by language extension for batched awk processing.
# Instead of one awk per file, we run one awk per language group.
declare -A EXT_FILES=()        # ext -> space-separated full paths
declare -A FULLPATH_RELPATH=() # fullpath -> relpath mapping

while IFS= read -r rel_file; do
  [[ -z "$rel_file" ]] && continue
  local_file="$PROJECT_DIR/$rel_file"
  [[ -f "$local_file" ]] || continue

  # Skip build artifacts, minified files, coverage caches
  case "$rel_file" in
    coverage-cache/*|coverage/*|*.min.js|*.min.css|node_modules/*|vendor/*|__pycache__/*|.venv/*|dist/*|build/*|out/*|target/*) continue ;;
  esac

  EXT="$(file_ext "$rel_file")"
  case "$EXT" in
    py|sh|bash|ts|tsx|js|jsx|go|rs|rb|java|kt) ;;
    *) continue ;;
  esac

  FULLPATH_RELPATH["$local_file"]="$rel_file"
  # Group files by normalized extension for batch awk
  local norm_ext="$EXT"
  EXT_FILES["$norm_ext"]="${EXT_FILES[$norm_ext]:-} $local_file"
done <<< "$CHANGED_FILES"

[[ ${#FULLPATH_RELPATH[@]} -eq 0 ]] && return 0

# Collect all full paths for batch baseline read
declare -a ALL_FULLPATHS=()
for fp in "${!FULLPATH_RELPATH[@]}"; do
  ALL_FULLPATHS+=("$fp")
done

# Batch-read all baselines in a single jq call (was: 1 jq call per file)
declare -A PREV_CC_MAP=()
declare -A PREV_LINES_MAP=()

while IFS=$'\t' read -r bkey bcc bfl; do
  [[ -z "$bkey" ]] && continue
  PREV_CC_MAP["$bkey"]="$bcc"
  PREV_LINES_MAP["$bkey"]="$bfl"
done < <(_get_baselines_batch "${ALL_FULLPATHS[@]}")

TOTAL_WARNINGS=0
TOTAL_IMPROVEMENTS=0
TOTAL_NEW=0

_RATCHET_BUF=""

# P4.4: Batch awk — one invocation per language group, then process results.# measure_files_batch outputs: FILENAME\tfile_lines:cyclomatic:cognitive:nesting:long_funcs
declare -A METRICS_MAP=()  # fullpath -> file_lines:cyc:cog:nest:long_funcs

for ext in "${!EXT_FILES[@]}"; do
  # Convert space-separated list to array
  local -a files_arr=()
  read -ra files_arr <<< "${EXT_FILES[$ext]}"
  [[ ${#files_arr[@]} -eq 0 ]] && continue

  # Run batch awk for this language group (one awk invocation for all files)
  while IFS=$'\t' read -r batch_fname batch_metrics; do
    [[ -z "$batch_fname" || -z "$batch_metrics" ]] && continue
    METRICS_MAP["$batch_fname"]="$batch_metrics"
  done < <(measure_files_batch "$ext" "$MAX_FUNCTION_LINES" "${files_arr[@]}")
done

# Accumulate updates for batch baseline write
UPDATE_JQ_EXPR=""

for local_file in "${!FULLPATH_RELPATH[@]}"; do
  rel_file="${FULLPATH_RELPATH[$local_file]}"

  # Read metrics from batch results (fallback to single-file if missing)
  local metrics="${METRICS_MAP[$local_file]:-}"
  if [[ -z "$metrics" ]]; then
    metrics=$(measure_file "$local_file" "$MAX_FUNCTION_LINES")
  fi
  IFS=':' read -r FL CC CG ND LF <<< "$metrics"
  FL="${FL:-0}"; CC="${CC:-0}"; CG="${CG:-0}"; ND="${ND:-0}"; LF="${LF:-0}"

  PREV_CC="${PREV_CC_MAP[$local_file]:-0}"

  if [[ "$PREV_CC" -gt 0 ]]; then
    if [[ "$CC" -gt "$PREV_CC" ]]; then
      _RATCHET_BUF+="  [INCREASED] ${rel_file} cyc=${PREV_CC}->${CC} cog=${CG}"$'\n'
      TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
    elif [[ "$CC" -lt "$PREV_CC" ]]; then
      _RATCHET_BUF+="  [DECREASED] ${rel_file} cyc=${PREV_CC}->${CC} cog=${CG}"$'\n'
      TOTAL_IMPROVEMENTS=$((TOTAL_IMPROVEMENTS + 1))
    fi
  else
    _RATCHET_BUF+="  [NEW]       ${rel_file} cyc=${CC} cog=${CG}"$'\n'
    TOTAL_NEW=$((TOTAL_NEW + 1))
  fi

  # Ratchet: only ratchet down, never up
  new_cc="$CC"
  [[ "$PREV_CC" -gt 0 ]] && [[ "$CC" -gt "$PREV_CC" ]] && new_cc="$PREV_CC"

  # Accumulate jq update expression for batch write
  UPDATE_JQ_EXPR="${UPDATE_JQ_EXPR} | .files[\"$(_json_escape "$local_file")\"] = {file_lines: $FL, cyclomatic: $new_cc, cognitive: $CG, nesting_depth: $ND, long_functions: $LF, updated_at: \"$now\"}"
done

# Single jq write for ALL file updates (was: 1 jq call per file)
if [[ -n "$UPDATE_JQ_EXPR" ]]; then
  # Strip leading " | "
  UPDATE_JQ_EXPR="${UPDATE_JQ_EXPR# | }"
  $JQ_CMD "$UPDATE_JQ_EXPR" <<< "$_baseline_content" > "${RATCHET_FILE}.tmp" && mv "${RATCHET_FILE}.tmp" "$RATCHET_FILE"
fi

if [[ "$TOTAL_WARNINGS" -gt 0 ]]; then
  echo "Complexity Ratchet FAIL"
  echo "======================"
  printf '%s' "$_RATCHET_BUF"
  echo ""
  printf "Summary: %d warnings, %d improvements, %d new files\n" "$TOTAL_WARNINGS" "$TOTAL_IMPROVEMENTS" "$TOTAL_NEW"
  echo "Status: COMPLEXITY INCREASED"
else
  echo "Complexity: ok"
fi
} # end _complexity_stop_main

# Run main, capture output, cache result
_output=$(_complexity_stop_main 2>&1); _rc=$?

# Write to ultra-fast cache (checked at top before common.sh sourcing)
if [[ -n "${_CACHE_FILE:-}" ]]; then
  mkdir -p "$_CACHE_DIR" 2>/dev/null || true
  if [[ -n "$_output" ]]; then
    echo "$_output" > "$_CACHE_FILE"
  else
    : > "$_CACHE_FILE"
  fi
fi

[[ -n "$_output" ]] && echo "$_output"
if [[ "$_rc" -ne 0 ]]; then
  echo "COMPLEXITY-RATCHET FAIL: stop scan exited with code $_rc" >&2
fi
exit "$_rc"
