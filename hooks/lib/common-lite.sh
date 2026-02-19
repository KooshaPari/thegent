#!/bin/zsh
# Lightweight hook library for dispatched hooks (_HOOK_DISPATCHED=1).
# Provides ONLY report-writing and state helpers. No stdin parsing,
# no tool detection, no caching infrastructure, no subprocess spawns.
# Source time target: < 1ms.

# Double-source guard
[[ -n "${_HOOK_LITE_LOADED:-}" ]] && return 0
_HOOK_LITE_LOADED=1

# --- Timestamp (printf builtin, zero subprocesses) ---
printf -v now '%(%Y-%m-%dT%H:%M:%SZ)T' -1

# --- JSON escape (pure bash string ops) ---
_json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

# --- Report writers (printf only, zero subprocesses) ---
write_pass_report() {
  local report_path="$1"
  local g; g="$(_json_escape "${2:-${HOOK_NAME:-unknown}}")"
  printf '{"generated_at":"%s","gate":"%s","status":"pass","pass":true,"error_count":0}\n' \
    "$now" "$g" > "$report_path"
}

write_na_report() {
  local report_path="$1"
  local g; g="$(_json_escape "${2:-${HOOK_NAME:-unknown}}")"
  printf '{"generated_at":"%s","gate":"%s","status":"not_applicable","pass":true,"error_count":0}\n' \
    "$now" "$g" > "$report_path"
}

write_fail_report() {
  local report_path="$1"
  local gate_name="${2:-${HOOK_NAME:-unknown}}"
  local error_count="${3:-1}"
  shift 3
  local errors_json='[]'
  if [[ $# -gt 0 ]]; then
    local items="" e
    for e in "$@"; do
      local escaped; escaped="$(_json_escape "$e")"
      [[ -z "$items" ]] && items="\"$escaped\"" || items="$items,\"$escaped\""
    done
    errors_json="[$items]"
  fi
  local g; g="$(_json_escape "$gate_name")"
  printf '{"generated_at":"%s","gate":"%s","status":"fail","pass":false,"error_count":%d,"errors":%s}\n' \
    "$now" "$g" "$error_count" "$errors_json" > "$report_path"
}

# --- State helpers ---
is_done_state() {
  case "${1:-}" in
    released|accepted|verified|done|completed) return 0 ;;
    *) return 1 ;;
  esac
}

file_ext() { echo "${1##*.}"; }
file_basename() { echo "${1##*/}"; }

# --- sort_unique (prefers huniq if HUNIQ_CMD set by dispatcher) ---
sort_unique() {
  if [[ -n "${HUNIQ_CMD:-}" ]]; then "$HUNIQ_CMD"; else sort -u; fi
}

# --- tool_available (simple command -v, no qa-state.json lookup) ---
tool_available() {
  command -v "$1" >/dev/null 2>&1 && echo true || echo false
}
