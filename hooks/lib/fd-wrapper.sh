#!/usr/bin/env bash
# fd wrapper - 3-5x speedup on directory traversal via Rust-based file discovery
# Provides drop-in replacement for find command with intelligent fallback
#
# Strategy: fd is 3-5x faster than find for most directory scans
# This wrapper translates common find patterns to fd, with fallback to find for complex queries

fd_find() {
  # Simple strategy: try to use fd for common cases, fallback to find for complex ones
  # This avoids complicated arg translation and just uses fd where it helps most

  local args=("$@")

  # Check if fd is available
  if ! command -v fd &>/dev/null; then
    # Fallback to system find with timeout
    timeout 5 find "${args[@]}" 2>/dev/null || true
    return $?
  fi

  # Detect if this is a simple pattern we can handle with fd
  # Simple patterns: find DIR -maxdepth N -name pattern [-type f]
  # Complex patterns (use find): -path, -newer, -prune, multiple -name with -o

  local has_complex_args=0
  for arg in "${args[@]}"; do
    case "$arg" in
      -path|-newer|-prune|-o|-exec|-print0)
        has_complex_args=1
        break
        ;;
    esac
  done

  if (( has_complex_args == 1 )); then
    # Complex query, use find
    timeout 5 find "${args[@]}" 2>/dev/null || true
    return $?
  fi

  # Try to use fd for simple queries
  _fd_try_simple_find "$@"
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
  local i=0

  while (( i < ${#args[@]} )); do
    local arg="${args[i]}"
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
    timeout 5 find "$@" 2>/dev/null || true
  fi
}

# Export for use in scripts
export -f fd_find
export -f _fd_try_simple_find
