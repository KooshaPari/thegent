#!/usr/bin/env zsh
# grep wrapper - 2-10x speedup on recursive/search via ripgrep
# Routes grep -r style invocations to rg when semantics align; fallback to grep otherwise.
#
# Strategy: rg is 2-10x faster than grep -r for recursive searches and respects .gitignore.
# Only intercepts patterns we can safely translate; unknown patterns use system grep.
#
# Timeout: RG_TIMEOUT_SEC (default 30) caps rg runtime to avoid 4m+ runs. Set to 0 to disable.

# Check if rg is available (use RG_CMD from dispatcher/cache if set)
_rg_for_grep() {
  local rg="${RG_CMD:-}"
  [[ -z "$rg" ]] && rg="$(command -v rg 2>/dev/null)"
  echo "$rg"
}

# Run rg with optional timeout (avoids 4m+ runs on large trees)
# Sanitizes environment to avoid config errors from problematic env vars
_run_rg() {
  local timeout_sec="${RG_TIMEOUT_SEC:-30}"
  # Use full path to rg to avoid shell aliases/functions
  local rg_cmd="${RG_CMD:-$(command -v rg 2>/dev/null || echo rg)}"
  
  # Run rg with clean environment and --no-config
  # Suppress stderr config errors (they're harmless but noisy)
  local result=0
  if [[ "$timeout_sec" -gt 0 ]] && command -v timeout >/dev/null 2>&1; then
    timeout "$timeout_sec" env -u GREP_OPTIONS -u GREP_COLOR -u GREP_COLORS "$rg_cmd" --no-config "$@" 2> >(command grep -v "grep config error" >&2) || result=$?
  else
    env -u GREP_OPTIONS -u GREP_COLOR -u GREP_COLORS "$rg_cmd" --no-config "$@" 2> >(command grep -v "grep config error" >&2) || result=$?
  fi
  
  return $result
}

# grep() override - routes to rg for recursive and common single-file patterns
grep() {
  local args=("$@")
  local rg_cmd
  rg_cmd=$(_rg_for_grep)

  # No rg available - use system grep
  if [[ -z "$rg_cmd" ]]; then
    command grep "${args[@]}"
    return $?
  fi

  # Detect patterns we should NOT route to rg (fallback to grep)
  local use_grep=0
  for arg in "${args[@]}"; do
    case "$arg" in
      -P|--perl-regexp|--include=*|--include-dir=*)
        use_grep=1
        break
        ;;
    esac
  done
  [[ $use_grep -eq 1 ]] && { command grep "${args[@]}"; return $?; }

  # Recursive: grep -r, -rE, -roE, -rHoE, -rEl, -rEh etc.
  local is_recursive=0
  local i=1
  if [ -n "${BASH_VERSION:-}" ]; then i=0; fi
  local num_args=${#args[@]}
  while (( i <= num_args )); do
    local arg="${args[i]}"
    case "$arg" in
      -r|-rE|-ro|-roE|-rH|-rHo|-rHoE|-rEl|-rEh|-rn|-R)
        is_recursive=1
        break
        ;;
    esac
    ((i++))
  done

  if [[ $is_recursive -eq 1 ]]; then
    _grep_to_rg_recursive "${args[@]}"
    return $?
  fi

  # Single-file / multi-file non-recursive: -nE, -oE, -cE, -q, -l, -L, -m1, -qm1
  # For these, rg is often faster on large files; try translation
  _grep_to_rg_simple "${args[@]}"
}

# Convert grep recursive args to rg
_grep_to_rg_recursive() {
  local args=("$@")
  local rg_args=()
  local pattern=""
  local paths=()
  local i=1
  if [ -n "${BASH_VERSION:-}" ]; then i=0; fi
  local has_o=0 has_n=0 has_l=0 has_L=0 has_q=0 has_H=0
  local exclude_dirs=()
  local num_args=${#args[@]}

  while (( i <= num_args )); do
    local arg="${args[i]}"
    case "$arg" in
      -r|-R|-rE|-ro|-roE|-rH|-rHo|-rHoE|-rEl|-rEh|-rn)
        # Skip recursive flag
        [[ "$arg" == *o* ]] && has_o=1
        [[ "$arg" == *n* ]] && has_n=1
        [[ "$arg" == *l* ]] && has_l=1
        [[ "$arg" == *H* ]] && has_H=1
        ;;
      -o|-oE) has_o=1 ;;
      -n|-nE) has_n=1 ;;
      -l|-lE) has_l=1 ;;
      -L|-LE) has_L=1 ;;
      -q|-qE) has_q=1 ;;
      -h) has_H=0 ;;  # rg shows filename by default with multiple files; -h suppresses
      --exclude-dir=*)
        exclude_dirs+=("-g" "!${arg#--exclude-dir=}")
        ;;
      -e)
        ((i++))
        pattern="${args[i]}"
        ;;
      *)
        if [[ "$arg" =~ ^- ]]; then
          :  # Skip other flags
        elif [[ -z "$pattern" ]]; then
          pattern="$arg"
        else
          paths+=("$arg")
        fi
        ;;
    esac
    ((i++))
  done

  [[ -z "$pattern" ]] && { command grep "${args[@]}"; return $?; }

  rg_args=()
  [[ $has_n -eq 1 ]] && rg_args+=( -n )
  [[ $has_o -eq 1 ]] && rg_args+=( -o )
  [[ $has_l -eq 1 ]] && rg_args+=( -l )
  [[ $has_L -eq 1 ]] && rg_args+=( -L )
  [[ $has_q -eq 1 ]] && rg_args+=( -q )
  [[ $has_H -eq 0 ]] && rg_args+=( --no-heading )  # grep -h behavior
  rg_args+=( "${exclude_dirs[@]}" )
  # Default excludes when none specified (matches hook EXCLUDE_DIRS)
  if [ ${#exclude_dirs[@]} -eq 0 ]; then
    rg_args+=( -g '!node_modules' -g '!vendor' -g '!.git' -g '!target' -g '!out' -g '!dist' -g '!build' -g '!coverage' -g '!__pycache__' -g '!.venv' )
  fi
  rg_args+=( "$pattern" )
  if [ ${#paths[@]} -gt 0 ]; then
    rg_args+=( "${paths[@]}" )
  else
    rg_args+=( "." )
  fi

  _run_rg "${rg_args[@]}" 2>/dev/null || command grep "${args[@]}"
}

# Convert simple grep args to rg (single/multi file, non-recursive)
_grep_to_rg_simple() {
  local args=("$@")
  local rg_args=()
  local pattern=""
  local files=()
  local i=1
  if [ -n "${BASH_VERSION:-}" ]; then i=0; fi
  local has_n=0 has_o=0 has_c=0 has_q=0 has_l=0 has_L=0 has_v=0 has_i=0
  local max_count=""
  local num_args=${#args[@]}

  while (( i <= num_args )); do
    local arg="${args[i]}"
    case "$arg" in
      -n|-nE|-En) has_n=1 ;;
      -o|-oE|-Eo) has_o=1 ;;
      -c|-cE|-Ec) has_c=1 ;;
      -q|-qE|-Eq) has_q=1 ;;
      -l|-lE|-El) has_l=1 ;;
      -L|-LE|-EL) has_L=1 ;;
      -v|-vE|-Ev) has_v=1 ;;
      -i|-iE|-Ei) has_i=1 ;;
      -E) ;; # Skip -E (rg is always ERE)
      -m)
        ((i++))
        max_count="${args[i]}"
        ;;
      -e)
        ((i++))
        pattern="${args[i]}"
        ;;
      *)
        if [[ "$arg" =~ ^- ]]; then
          :  # Skip
        elif [[ -z "$pattern" ]]; then
          pattern="$arg"
        else
          files+=("$arg")
        fi
        ;;
    esac
    ((i++))
  done

  [[ -z "$pattern" ]] && { command grep "${args[@]}"; return $?; }

  rg_args=(--no-config)
  [[ $has_n -eq 1 ]] && rg_args+=( -n )
  [[ $has_o -eq 1 ]] && rg_args+=( -o )
  [[ $has_c -eq 1 ]] && rg_args+=( -c )
  [[ $has_q -eq 1 ]] && rg_args+=( -q )
  [[ $has_l -eq 1 ]] && rg_args+=( -l )
  [[ $has_L -eq 1 ]] && rg_args+=( -L )
  [[ $has_v -eq 1 ]] && rg_args+=( -v )
  [[ $has_i -eq 1 ]] && rg_args+=( -i )
  [[ -n "$max_count" ]] && rg_args+=( --max-count "$max_count" )
  rg_args+=( "$pattern" )
  rg_args+=( "${files[@]}" )

  _run_rg "${rg_args[@]}" 2>/dev/null || command grep "${args[@]}"
}

if [ -n "${BASH_VERSION:-}" ]; then
  export -f grep
  export -f _run_rg
  export -f _grep_to_rg_recursive
  export -f _grep_to_rg_simple
  export -f _rg_for_grep
fi
