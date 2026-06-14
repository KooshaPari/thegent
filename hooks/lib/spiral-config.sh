#!/usr/bin/env zsh
# Shared regression spiral guard configuration loader.
# Reads defaults from hooks/hook-config.yaml (settings.regression_spiral_guard).
# Intended to be sourced by hook scripts.

[[ -n "${_SPIRAL_CONFIG_LIB_LOADED:-}" ]] && return 0
_SPIRAL_CONFIG_LIB_LOADED=1

# Default values (used when config file/keys are missing).
SPIRAL_CFG_MAX_FAILED_TESTS_DEFAULT="10"
SPIRAL_CFG_MAX_FLAKY_TESTS_DEFAULT="8"
SPIRAL_CFG_MAX_MISSING_TEST_PAIRS_DEFAULT="0"
SPIRAL_CFG_MAX_MISSING_TEST_TYPES_DEFAULT="0"
SPIRAL_CFG_MAX_TEST_EVIDENCE_AGE_MINUTES_DEFAULT="90"
SPIRAL_CFG_MAX_BUILD_EVIDENCE_AGE_MINUTES_DEFAULT="90"
SPIRAL_CFG_MAX_E2E_EVIDENCE_AGE_MINUTES_DEFAULT="180"
SPIRAL_CFG_STREAK_TRIGGER_DEFAULT="2"
SPIRAL_CFG_REQUIRE_E2E_FIRST_DEFAULT="true"
SPIRAL_CFG_REQUIRE_ENV_READY_FIRST_DEFAULT="true"
SPIRAL_CFG_MAX_YELLOW_RETRIES_DEFAULT="2"
SPIRAL_CFG_MAX_RED_RETRIES_DEFAULT="2"
SPIRAL_CFG_YELLOW_COOLDOWN_MINUTES_DEFAULT="30"
SPIRAL_CFG_RED_COOLDOWN_MINUTES_DEFAULT="60"
SPIRAL_CFG_DIRECTIVE_GREEN_DEFAULT="continue_delivery"
SPIRAL_CFG_DIRECTIVE_YELLOW_DEFAULT="stabilize_before_new_changes"
SPIRAL_CFG_DIRECTIVE_RED_DEFAULT="hard_interrupt_remediate_now"

_spiral_yaml_get_value() {
  local cfg_file="$1"
  local wanted_key="$2"
  [[ -f "$cfg_file" ]] || return 1

  awk -v wanted_key="$wanted_key" '
    BEGIN {
      in_settings = 0
      in_spiral = 0
    }
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    {
      line = $0
    }
    !in_settings {
      if (line ~ /^[[:space:]]*settings:[[:space:]]*$/) {
        in_settings = 1
      }
      next
    }
    line ~ /^[[:space:]]*hooks:[[:space:]]*$/ { exit }
    !in_spiral {
      if (line ~ /^[[:space:]]{2}regression_spiral_guard:[[:space:]]*$/) {
        in_spiral = 1
      }
      next
    }
    in_spiral {
      if (line ~ /^[[:space:]]{2}[^[:space:]].*:[[:space:]]*$/ && line !~ /^[[:space:]]{4}/) {
        exit
      }
      pattern = "^[[:space:]]{4}" wanted_key ":[[:space:]]*"
      if (line ~ pattern) {
        sub(pattern, "", line)
        gsub(/^[\"\047]|[\"\047]$/, "", line)
        print line
        exit
      }
    }
  ' "$cfg_file"
}

resolve_hook_dispatcher_bin() {
  if [[ -n "${HOOK_DISPATCHER_BIN:-}" && -x "${HOOK_DISPATCHER_BIN:-}" ]]; then
    printf '%s\n' "$HOOK_DISPATCHER_BIN"
    return 0
  fi
  if [[ -n "${PROJECT_DIR:-}" && -x "${PROJECT_DIR}/hooks/bin/hook-dispatcher" ]]; then
    printf '%s\n' "${PROJECT_DIR}/hooks/bin/hook-dispatcher"
    return 0
  fi
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -x "${script_dir}/../bin/hook-dispatcher" ]]; then
    printf '%s\n' "${script_dir}/../bin/hook-dispatcher"
    return 0
  fi
  if command -v hook-dispatcher >/dev/null 2>&1; then
    command -v hook-dispatcher
    return 0
  fi
  return 1
}

load_spiral_guard_config() {
  local cfg_file="$1"

  CFG_SPIRAL_MAX_FAILED_TESTS="$SPIRAL_CFG_MAX_FAILED_TESTS_DEFAULT"
  CFG_SPIRAL_MAX_FLAKY_TESTS="$SPIRAL_CFG_MAX_FLAKY_TESTS_DEFAULT"
  CFG_SPIRAL_MAX_MISSING_TEST_PAIRS="$SPIRAL_CFG_MAX_MISSING_TEST_PAIRS_DEFAULT"
  CFG_SPIRAL_MAX_MISSING_TEST_TYPES="$SPIRAL_CFG_MAX_MISSING_TEST_TYPES_DEFAULT"
  CFG_SPIRAL_MAX_TEST_EVIDENCE_AGE_MINUTES="$SPIRAL_CFG_MAX_TEST_EVIDENCE_AGE_MINUTES_DEFAULT"
  CFG_SPIRAL_MAX_BUILD_EVIDENCE_AGE_MINUTES="$SPIRAL_CFG_MAX_BUILD_EVIDENCE_AGE_MINUTES_DEFAULT"
  CFG_SPIRAL_MAX_E2E_EVIDENCE_AGE_MINUTES="$SPIRAL_CFG_MAX_E2E_EVIDENCE_AGE_MINUTES_DEFAULT"
  CFG_SPIRAL_STREAK_TRIGGER="$SPIRAL_CFG_STREAK_TRIGGER_DEFAULT"
  CFG_REQUIRE_E2E_FIRST="$SPIRAL_CFG_REQUIRE_E2E_FIRST_DEFAULT"
  CFG_REQUIRE_ENV_READY_FIRST="$SPIRAL_CFG_REQUIRE_ENV_READY_FIRST_DEFAULT"
  CFG_SPIRAL_MAX_YELLOW_RETRIES="$SPIRAL_CFG_MAX_YELLOW_RETRIES_DEFAULT"
  CFG_SPIRAL_MAX_RED_RETRIES="$SPIRAL_CFG_MAX_RED_RETRIES_DEFAULT"
  CFG_SPIRAL_YELLOW_COOLDOWN_MINUTES="$SPIRAL_CFG_YELLOW_COOLDOWN_MINUTES_DEFAULT"
  CFG_SPIRAL_RED_COOLDOWN_MINUTES="$SPIRAL_CFG_RED_COOLDOWN_MINUTES_DEFAULT"
  CFG_SPIRAL_DIRECTIVE_GREEN="$SPIRAL_CFG_DIRECTIVE_GREEN_DEFAULT"
  CFG_SPIRAL_DIRECTIVE_YELLOW="$SPIRAL_CFG_DIRECTIVE_YELLOW_DEFAULT"
  CFG_SPIRAL_DIRECTIVE_RED="$SPIRAL_CFG_DIRECTIVE_RED_DEFAULT"

  local dispatcher
  dispatcher="$(resolve_hook_dispatcher_bin || true)"
  [[ -n "$dispatcher" ]] || return 0

  local raw
  raw="$("$dispatcher" governance spiral-config "$cfg_file" --format env 2>/dev/null || true)"
  [[ -n "$raw" ]] || return 0

  local line key value
  while IFS= read -r line; do
    [[ "$line" == *=* ]] || continue
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in
      CFG_SPIRAL_MAX_FAILED_TESTS) CFG_SPIRAL_MAX_FAILED_TESTS="$value" ;;
      CFG_SPIRAL_MAX_FLAKY_TESTS) CFG_SPIRAL_MAX_FLAKY_TESTS="$value" ;;
      CFG_SPIRAL_MAX_MISSING_TEST_PAIRS) CFG_SPIRAL_MAX_MISSING_TEST_PAIRS="$value" ;;
      CFG_SPIRAL_MAX_MISSING_TEST_TYPES) CFG_SPIRAL_MAX_MISSING_TEST_TYPES="$value" ;;
      CFG_SPIRAL_MAX_TEST_EVIDENCE_AGE_MINUTES) CFG_SPIRAL_MAX_TEST_EVIDENCE_AGE_MINUTES="$value" ;;
      CFG_SPIRAL_MAX_BUILD_EVIDENCE_AGE_MINUTES) CFG_SPIRAL_MAX_BUILD_EVIDENCE_AGE_MINUTES="$value" ;;
      CFG_SPIRAL_MAX_E2E_EVIDENCE_AGE_MINUTES) CFG_SPIRAL_MAX_E2E_EVIDENCE_AGE_MINUTES="$value" ;;
      CFG_SPIRAL_STREAK_TRIGGER) CFG_SPIRAL_STREAK_TRIGGER="$value" ;;
      CFG_REQUIRE_E2E_FIRST) CFG_REQUIRE_E2E_FIRST="$value" ;;
      CFG_REQUIRE_ENV_READY_FIRST) CFG_REQUIRE_ENV_READY_FIRST="$value" ;;
      CFG_SPIRAL_MAX_YELLOW_RETRIES) CFG_SPIRAL_MAX_YELLOW_RETRIES="$value" ;;
      CFG_SPIRAL_MAX_RED_RETRIES) CFG_SPIRAL_MAX_RED_RETRIES="$value" ;;
      CFG_SPIRAL_YELLOW_COOLDOWN_MINUTES) CFG_SPIRAL_YELLOW_COOLDOWN_MINUTES="$value" ;;
      CFG_SPIRAL_RED_COOLDOWN_MINUTES) CFG_SPIRAL_RED_COOLDOWN_MINUTES="$value" ;;
      CFG_SPIRAL_DIRECTIVE_GREEN) CFG_SPIRAL_DIRECTIVE_GREEN="$value" ;;
      CFG_SPIRAL_DIRECTIVE_YELLOW) CFG_SPIRAL_DIRECTIVE_YELLOW="$value" ;;
      CFG_SPIRAL_DIRECTIVE_RED) CFG_SPIRAL_DIRECTIVE_RED="$value" ;;
    esac
  done <<< "$raw"

  # Parse direct YAML keys for compatibility with loaders that do not yet emit
  # env lines for newer spiral config fields.
  local direct_key direct_value
  for direct_key in \
    max_yellow_retries \
    max_red_retries \
    yellow_cooldown_minutes \
    red_cooldown_minutes \
    directive_green \
    directive_yellow \
    directive_red; do
    direct_value="$(_spiral_yaml_get_value "$cfg_file" "$direct_key" || true)"
    [[ -n "$direct_value" ]] || continue
    case "$direct_key" in
      max_yellow_retries) CFG_SPIRAL_MAX_YELLOW_RETRIES="$direct_value" ;;
      max_red_retries) CFG_SPIRAL_MAX_RED_RETRIES="$direct_value" ;;
      yellow_cooldown_minutes) CFG_SPIRAL_YELLOW_COOLDOWN_MINUTES="$direct_value" ;;
      red_cooldown_minutes) CFG_SPIRAL_RED_COOLDOWN_MINUTES="$direct_value" ;;
      directive_green) CFG_SPIRAL_DIRECTIVE_GREEN="$direct_value" ;;
      directive_yellow) CFG_SPIRAL_DIRECTIVE_YELLOW="$direct_value" ;;
      directive_red) CFG_SPIRAL_DIRECTIVE_RED="$direct_value" ;;
    esac
  done

  return 0
}
