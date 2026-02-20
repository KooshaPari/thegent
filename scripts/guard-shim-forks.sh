#!/usr/bin/env zsh
set -euo pipefail

# Guardrail: fail when a shim can recursively re-invoke a shim or dispatch the
# wrong tool from a generic wrapper.
BIN_DIR="${1:-${HOME}/.local/bin}"
TARGETS=(cat du find git grep jq node npm npx pip pip3 python python3 rg uv yarn)
TIMEOUT_SECONDS=2

is_text_shim() {
  local _file="$1"
  local _line
  read -r _line < "$_file" || true
  [[ "${_line:0:2}" == "#!" ]]
}

flag_if_bad_dispatch() {
  local shim_path="$1"
  local expected_tool="$2"

  if awk -v tool="$expected_tool" '
    {
      for (i = 1; i <= NF; i++) {
        if ($i != "command" && $i != "exec") {
          continue
        }
        for (j = i + 1; j <= NF; j++) {
          if ($j ~ /^-/) {
            continue
          }
          if ($j == tool) {
            exit 1
          }
          break
        }
      }
    }
  ' "$shim_path"; then
    :
  else
    echo "FORK-GUARD BLOCK: $shim_path contains direct command/exec of $expected_tool"
    return 1
  fi

  return 0
}

flag_wrong_tool_dispatch() {
  local shim_path="$1"
  local expected_tool="$2"

  if [[ "$expected_tool" != "npm" ]]; then
    if grep -Fq "type -t npm" "$shim_path" || \
      grep -Fq "REAL_NPM" "$shim_path" || \
      grep -Fq 'npm "$@"' "$shim_path"; then
      echo "FORK-GUARD BLOCK: $shim_path appears to dispatch to npm from $expected_tool shim"
      return 1
    fi
  fi

  return 0
}

run_with_timeout() {
  local -a cmd=("$@")
  local pid=""
  local waited=0
  local rc=0

  PATH="$BIN_DIR:${PATH}" "${cmd[@]}" >/dev/null 2>&1 &
  pid=$!

  while (( waited < TIMEOUT_SECONDS * 10 )); do
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid"
      rc=$?
      break
    fi
    sleep 0.1
    ((waited++))
  done

  if kill -0 "$pid" 2>/dev/null; then
    kill -TERM "$pid" 2>/dev/null || true
    sleep 0.1
    kill -KILL "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
    return 124
  fi

  return "$rc"
}

flag_if_binary_hangs() {
  local tool="$1"
  local -a args=()

  case "$tool" in
    git)
      args=(rev-parse --show-toplevel)
      ;;
    cat|du|find|grep|jq|npm|npx|pip|pip3|python|python3|rg|node|uv|yarn)
      args=(--version)
      ;;
    *)
      return 0
      ;;
  esac

  local rc=0
  run_with_timeout "$tool" "${args[@]}"
  rc=$?
  if (( rc == 124 )); then
    echo "FORK-GUARD BLOCK: $tool binary shim probe hangs"
    return 1
  fi
  if (( rc != 0 )); then
    echo "FORK-GUARD BLOCK: $tool binary shim probe failed with rc=$rc"
    return 1
  fi
  return 0
}

shim_target() {
  local shim="$1"
  if [[ -L "$shim" ]]; then
    if command -v readlink >/dev/null 2>&1; then
      readlink -f "$shim" || readlink "$shim" || echo "$shim"
    else
      readlink "$shim" || echo "$shim"
    fi
  else
    echo "$shim"
  fi
}

status=0
for tool in "${TARGETS[@]}"; do
  shim="$BIN_DIR/$tool"
  [[ -x "$shim" ]] || continue
  [[ -e "$shim" ]] || continue

  target_path="$(shim_target "$shim")"
  [[ -f "$target_path" ]] || continue
  # skip opaque binaries
  if ! is_text_shim "$target_path"; then
    if [[ "$(basename "$target_path")" == "runtime-dispatch" || "$(basename "$target_path")" == "ultra-shim" ]]; then
      if ! flag_if_binary_hangs "$tool"; then
        status=1
      fi
    fi
    continue
  fi

  if ! flag_if_bad_dispatch "$target_path" "$tool"; then
    status=1
  fi

  if ! flag_wrong_tool_dispatch "$target_path" "$tool"; then
    status=1
  fi

  # Legacy ultra-shims may use a fixed dispatch path; only validate TOOL_NAME
  # based dispatch when the guard variable is present, to avoid false positives.
  if [[ "$(basename "$target_path")" == "ultra-shim" ]]; then
    if grep -Fq 'TOOL_NAME=' "$target_path" && \
      ! grep -Fq 'TOOL_NAME="$(basename "${0##*/}")"' "$target_path" \
      && ! grep -Fq 'TOOL_NAME="$(basename "$0")"' "$target_path"; then
      echo "FORK-GUARD BLOCK: $shim (ultra-shim target) lacks basename-driven dispatch"
      status=1
    fi
  fi
done

exit "$status"
