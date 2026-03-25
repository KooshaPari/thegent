# thegent worktree governance (managed)
# Goal:
# - Keep the primary repository checkout on main.
# - Do all feature work in dedicated worktrees.

thg_new_worktree() {
  if [[ $# -lt 1 ]]; then
    cat >&2 <<'USAGE'
Usage: thg_new_worktree <path|new|state|list|prune|check> ...
  path <domain> <scale> <change-anchor> <state>
  new <domain> <scale> <change-anchor> [start-point]
  state <change-anchor> <new-state>
  list
  prune [--dry-run]
  check
USAGE
    return 1
  fi

  local repo_root current_branch
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "[FAIL] Not inside a git repository." >&2
    return 1
  }

  current_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null)" || return 1
  if [[ -f "$repo_root/.thegent-primary-main" ]] && [[ "$current_branch" != "main" ]]; then
    echo "[FAIL] Primary checkout must remain on main. Use structured worktree governance commands: path/new/state/list/prune/check." >&2
    return 1
  fi

  case "$1" in
    path|new|state|list|prune|check) ;;
    *)
      echo "[FAIL] Unsupported worktree governance command: $1. Use path/new/state/list/prune/check." >&2
      return 1
      ;;
  esac

  ( cd "$repo_root" && ./scripts/worktree_governance.sh "$@" )
}
