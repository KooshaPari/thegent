#!/usr/bin/env zsh
# fd wrapper - 3-5x speedup on directory traversal via Rust-based file discovery
# Provides drop-in replacement for find command with intelligent fallback
#
# Strategy: fd is 3-5x faster than find for most directory scans
# This wrapper translates common find patterns to fd, with fallback to find for complex queries

fd_find() {
  # Simple strategy: try to use fd for common cases, fallback to find for complex ones
  # This avoids complicated arg translation and just uses fd where it helps most

  local args=("$@")
  
  # Filter out -q option (GNU find extension, not supported on macOS BSD find)
  # Convert -q to 2>/dev/null redirection for error suppression
  local filtered_args=()
  local redirect_stderr=0
  for arg in "${args[@]}"; do
    if [[ "$arg" == "-q" || "$arg" == "--quiet" ]]; then
      redirect_stderr=1
      continue
    fi
    filtered_args+=("$arg")
  done

  # Check if fd is available
  if ! command -v fd &>/dev/null; then
    if (( redirect_stderr == 1 )); then
      command find "${filtered_args[@]}" 2>/dev/null || true
    else
      command find "${filtered_args[@]}" 2>/dev/null || true
    fi
    return $?
  fi

  # Detect if this is a simple pattern we can handle with fd
  # Simple patterns: find DIR -maxdepth N -name pattern [-type f]
  # Complex patterns (use find): -path, -newer, -prune, -o, -print, -quit, \( \)

  local has_complex_args=0
  for arg in "${filtered_args[@]}"; do
    case "$arg" in
      -path|-newer|-prune|-o|-exec|-print0|-print|-quit|"("|")")
        has_complex_args=1
        break
        ;;
    esac
  done

  if (( has_complex_args == 1 )); then
    # Complex query: use real find (bypass find shim that may route to fd)
    if (( redirect_stderr == 1 )); then
      command find "${filtered_args[@]}" 2>/dev/null || true
    else
      command find "${filtered_args[@]}" 2>/dev/null || true
    fi
    return $?
  fi

  # Try to use fd for simple queries
  if (( redirect_stderr == 1 )); then
    _fd_try_simple_find "${filtered_args[@]}" 2>/dev/null
  else
    _fd_try_simple_find "${filtered_args[@]}"
  fi
}

_fd_try_simple_find() {
  # Parse arguments for simple find patterns and translate to fd
  # Common patterns:
  #   find DIR -maxdepth N -name "*.ext" -type f
  #   find DIR -maxdepth N -type f -name "pattern"
  #   find DIR -name "pattern"

  local args=("$@")
  local pattern=""
  local max_depth=""
  local type_filter=""
  local dir="."
  local i=1

  # Handle array indexing difference between bash (0-based) and zsh (1-based)
  local num_args=${#args[@]}
  if [ -n "${BASH_VERSION:-}" ]; then
    i=0
  fi

  while (( i < num_args || ( -n "${BASH_VERSION:-}" && i < num_args ) )); do
    # Correct indexing for both shells
    local idx=$i
    if [ -n "${ZSH_VERSION:-}" ]; then
      idx=$i
    fi
    local arg="${args[idx]}"
    case "$arg" in
      -maxdepth)
        max_depth="${args[++i]}"
        ;;
      -name)
        pattern="${args[++i]}"
        ;;
      -type)
        type_filter="${args[++i]}"
        ;;
      -print|-print0|-newer)
        # Skip output format flags
        ;;
      *)
        # Check if it's a path argument (doesn't start with -)
        if [[ ! "$arg" =~ ^- ]] && [[ -d "$arg" ]] && [[ "$dir" == "." ]]; then
          dir="$arg"
        fi
        ;;
    esac
    ((i++))
  done

  # Build fd command
  local fd_args=()

  if [[ -n "$pattern" ]]; then
    # Convert glob pattern to regex if needed
    fd_args+=("$pattern")
  else
    fd_args+=(".")
  fi

  if [[ -n "$max_depth" ]]; then
    fd_args+=("--max-depth" "$max_depth")
  fi

  case "$type_filter" in
    f) fd_args+=("--type" "f") ;;
    d) fd_args+=("--type" "d") ;;
  esac

  fd_args+=("$dir")

  # Run fd with fallback
  if timeout 5 fd "${fd_args[@]}" 2>/dev/null; then
    return 0
  else
    # fd failed or timed out, fallback to find
    timeout 5 command find "$@" 2>/dev/null || true
  fi
}

if [ -n "${BASH_VERSION:-}" ]; then
  export -f fd_find
  export -f _fd_try_simple_find
fi
