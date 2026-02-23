# thegent worktree governance (managed)
# Goal:
# - Keep the primary repository checkout on main.
# - Do all feature work in dedicated worktrees.

thg_new_worktree() {
  if [[ $# -lt 1 ]]; then
    echo "Usage: thg_new_worktree <branch> [start-point] [worktree-path]" >&2
    return 1
  fi

  local branch="$1"
  local start_point="${2:-main}"
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

  local wt_path
  if [[ $# -ge 3 ]]; then
    wt_path="$3"
  else
    local slug="${branch//\//-}"
    wt_path="$repo_root/../wt/$slug"
  fi

  local existing
  existing="$(git -C "$repo_root" worktree list --porcelain | awk -v b="$branch" '
    /^worktree / { path=$2 }
    /^branch refs\/heads\// {
      ref=$2
      sub(/^refs\/heads\//, "", ref)
      if (ref == b) print path
    }
  ')"

  if [[ -n "$existing" ]]; then
    echo "[OK] Existing worktree for $branch: $existing"
    return 0
  fi

  if git -C "$repo_root" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$repo_root" worktree add "$wt_path" "$branch"
  else
    git -C "$repo_root" worktree add -b "$branch" "$wt_path" "$start_point"
  fi

  echo "[OK] Worktree ready: $wt_path ($branch)"
}

thg_main_guard() {
  local repo_root current_branch
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || return 0
  current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || return 0

  # Opt-out for temporary workflows.
  [[ "${THGENT_DISABLE_MAIN_GUARD:-0}" == "1" ]] && return 0

  if [[ -f "$repo_root/.thegent-primary-main" ]] && [[ "$current_branch" != "main" ]]; then
    echo "[thegent] Primary repo policy: keep this checkout on main. Use thg_new_worktree <branch>." >&2
  fi
}

if [[ -o interactive ]]; then
  autoload -Uz add-zsh-hook
  add-zsh-hook precmd thg_main_guard
fi
