#!/bin/zsh
# qa-preflight.sh — SessionStart hook
# Auto-detects stacks, checks tool availability, loads quality config,
# writes qa-state.json for downstream hooks. Must exit 0, target <80ms.
# Zero subprocess forks in dispatched mode.
set -euo pipefail

trap 'echo "QA-PREFLIGHT FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  printf -v _now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
  QA_STATE="${PROJECT_DIR:-.}/.claude/qa-state.json"
else
  HOOK_NAME="QA-PREFLIGHT"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
  printf -v _now '%(%Y-%m-%dT%H:%M:%SZ)T' -1
fi

_PD="${PROJECT_DIR:-.}"

# ---------- Stack detection (pure [[ -f ]], zero forks) ----------
_stacks_json="[" _stack_list="" _sep=""
_add_stack() {
  _stacks_json+="${_sep}\"$1\""; _stack_list+="${_sep}$1"; _sep=","
}

[[ -f "$_PD/pyproject.toml" || -f "$_PD/setup.py" || -f "$_PD/requirements.txt" ]] && _add_stack python
[[ -f "$_PD/package.json" ]] && _add_stack typescript
[[ -f "$_PD/go.mod" ]] && _add_stack go
[[ -f "$_PD/Cargo.toml" ]] && _add_stack rust
# Shell: check for scripts/ or test/ dir existence as proxy (skip compgen counting)
[[ -d "$_PD/scripts" || -d "$_PD/test" ]] && _add_stack shell
[[ -f "$_PD/CMakeLists.txt" ]] && _add_stack c_cpp
[[ -f "$_PD/pom.xml" || -f "$_PD/build.gradle" ]] && _add_stack java
[[ -f "$_PD/build.gradle.kts" ]] && _add_stack kotlin
[[ -f "$_PD/Package.swift" ]] && _add_stack swift
[[ -f "$_PD/Gemfile" ]] && _add_stack ruby
[[ -f "$_PD/composer.json" ]] && _add_stack php
[[ -f "$_PD/pubspec.yaml" ]] && _add_stack dart
[[ -f "$_PD/build.sbt" ]] && _add_stack scala
[[ -f "$_PD/mix.exs" ]] && _add_stack elixir
[[ -f "$_PD/Dockerfile" ]] && _add_stack dockerfile
[[ -f "$_PD/buf.yaml" ]] && _add_stack protobuf
_stacks_json+="]"

# ---------- Tool availability (command -v is bash builtin, ~1ms each) ----------
# Only check tools relevant to detected stacks to reduce iterations
_tool_pairs="" _available_list="" _tsep=""
_check_tool() {
  local name="$1" cmd="${2:-$1}"
  if command -v "$cmd" >/dev/null 2>&1; then
    _tool_pairs+="\"$name\":true,"
    _available_list+="${_tsep}$name"; _tsep=", "
  else
    _tool_pairs+="\"$name\":false,"
  fi
}

# Core tools (always checked — small set, ~5ms total)
_check_tool jq
_check_tool semgrep
_check_tool bats

# Stack-conditional tool checks
[[ "$_stack_list" == *python* ]] && { _check_tool ruff; _check_tool pytest; _check_tool bandit; }
[[ "$_stack_list" == *typescript* ]] && _check_tool oxlint
[[ "$_stack_list" == *shell* ]] && _check_tool shellcheck
[[ "$_stack_list" == *go* ]] && _check_tool golangci-lint
[[ "$_stack_list" == *rust* ]] && _check_tool cargo-clippy cargo

_tools_json="{${_tool_pairs%,}}"

# ---------- Config + FR check ----------
CONFIG_PATH=""
[[ -f "$_PD/.qa-config.json" ]] && CONFIG_PATH="$_PD/.qa-config.json"
[[ -z "$CONFIG_PATH" && -f "$HOME/.claude/qa-config.json" ]] && CONFIG_PATH="$HOME/.claude/qa-config.json"

HAS_FR=false
[[ -f "$_PD/FUNCTIONAL_REQUIREMENTS.md" ]] && HAS_FR=true

# ---------- Write qa-state.json (printf, no cat heredoc fork) ----------
[[ -d "$_PD/.claude" ]] || mkdir -p "$_PD/.claude" 2>/dev/null || true
printf '{"version":"1.0","timestamp":"%s","project_dir":"%s","stacks":%s,"tools":%s,"config_path":"%s","has_functional_requirements":%s}\n' \
  "$_now" "$_PD" "$_stacks_json" "$_tools_json" "$CONFIG_PATH" "$HAS_FR" \
  > "${QA_STATE:-$_PD/.claude/qa-state.json}"

# ---------- Summary ----------
echo "QA PREFLIGHT: stacks=[$_stack_list] tools=[$_available_list]"
[[ -n "$CONFIG_PATH" ]] && echo "QA CONFIG: $CONFIG_PATH"
[[ "$HAS_FR" == true ]] && echo "QA TRACEABILITY: FR spec found, traceability checks enabled"

# ---------- Pre-warm caches on session start (P2 optimization) ----------
# Non-blocking: fork and exit. Speeds up subsequent Stop hooks.
if [[ -z "${_HOOK_DISPATCHED:-}" ]] && type hook_config_true hook_prewarm_all &>/dev/null; then
  if hook_config_true "prewarm_on_session_start" 2>/dev/null; then
    (hook_prewarm_all &) 2>/dev/null
  fi
fi

# ---------- P8: Start hook watcher daemon when daemon_mode: true ----------
if [[ -z "${_HOOK_DISPATCHED:-}" ]] && type hook_config_true &>/dev/null; then
  if hook_config_true "daemon_mode" 2>/dev/null; then
    watcher_script="${BASH_SOURCE[0]%/*}/hook-watcher.sh"
    if [[ -f "$watcher_script" ]]; then
      ("$watcher_script" "$_PD" &) 2>/dev/null
    fi
  fi
fi

exit 0
