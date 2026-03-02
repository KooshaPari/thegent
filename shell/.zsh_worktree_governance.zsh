# thegent worktree governance (managed)
# Goal:
# - Keep the primary repository checkout on main.
# - Do all feature work in dedicated worktrees.

thg_new_worktree() {
  if [[ $# -lt 3 ]]; then
    echo "Usage: thg_new_worktree <domain> <scale> <change-anchor> [start-point]" >&2
    return 1
  fi

  local domain="$1"
  local scale="$2"
  local change_anchor="$3"
  local start_point="${4:-main}"
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "[FAIL] Not inside a git repository." >&2
    return 1
  }

  local current_branch
  current_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null)" || return 1
  if [[ "$current_branch" != "main" ]]; then
    echo "[FAIL] Primary checkout must remain on main. Current branch: $current_branch" >&2
    return 1
  fi

  if [[ -n "$(git -C "$repo_root" status --porcelain 2>/dev/null)" ]]; then
    echo "[FAIL] Primary checkout is dirty. Commit/stash first." >&2
    return 1
  fi

  if [[ -z "$domain" || -z "$scale" || -z "$change_anchor" ]]; then
    echo "Usage: thg_new_worktree <domain> <scale> <change-anchor> [start-point]" >&2
    return 1
  fi

  local path
  path="$(/bin/sh "$repo_root/scripts/worktree_governance.sh" new "$domain" "$scale" "$change_anchor" "$start_point")"
  local rc=$?
  if [[ $rc -ne 0 ]]; then
    return $rc
  fi

  echo "[OK] Worktree ready: $path ($domain/$scale/$change_anchor)"
}

thg_main_guard() {
  local repo_root current_branch
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || return 0
  current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || return 0

  # Opt-out for temporary workflows.
  [[ "${THGENT_DISABLE_MAIN_GUARD:-0}" == "1" ]] && return 0

  if [[ -f "$repo_root/.thegent-primary-main" ]] && [[ "$current_branch" != "main" ]]; then
    echo "[thegent] Primary repo policy: keep this checkout on main. Use thg_new_worktree <domain> <scale> <change-anchor>." >&2
  fi
}

if [[ -o interactive ]]; then
  autoload -Uz add-zsh-hook
  add-zsh-hook precmd thg_main_guard
fi
