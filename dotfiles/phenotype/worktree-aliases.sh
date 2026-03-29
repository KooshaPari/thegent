#!/usr/bin/env bash
# dotfiles/phenotype/worktree-aliases.sh
# Shell aliases specific to Phenotype worktree workflow
# Source from .zshrc or .bashrc via: source "$DOTFILES_DIR/phenotype/worktree-aliases.sh"

PHENOTYPE_REPOS="${PHENOTYPE_REPOS:-/Users/kooshapari/CodeProjects/Phenotype/repos}"

# --- Navigation ---
alias phrepos="cd $PHENOTYPE_REPOS"
alias phwt="cd $PHENOTYPE_REPOS/worktrees"
alias phcanon="cd $PHENOTYPE_REPOS"

# --- Worktree management functions ---

# Create a new worktree: phwt-new <project> <topic>
phwt-new() {
  local project="${1:?Usage: phwt-new <project> <topic>}"
  local topic="${2:?Usage: phwt-new <project> <topic>}"
  local canon="$PHENOTYPE_REPOS/$project"
  local wt_path="$PHENOTYPE_REPOS/worktrees/$project/$topic"

  if [[ ! -d "$canon" ]]; then
    echo "ERROR: Repo not found at $canon" >&2
    return 1
  fi

  git -C "$canon" worktree add "$wt_path" -b "feat/$topic"
  echo "Created worktree: $wt_path"
  echo "Branch: feat/$topic"
  cd "$wt_path"
}

# Go to a worktree: phwt-go <project> <topic>
phwt-go() {
  local project="${1:?Usage: phwt-go <project> <topic>}"
  local topic="${2:?Usage: phwt-go <project> <topic>}"
  local wt_path="$PHENOTYPE_REPOS/worktrees/$project/$topic"

  if [[ ! -d "$wt_path" ]]; then
    echo "ERROR: Worktree not found at $wt_path" >&2
    echo "Available worktrees for $project:"
    ls "$PHENOTYPE_REPOS/worktrees/$project/" 2>/dev/null || echo "  (none)"
    return 1
  fi

  cd "$wt_path"
}

# List all worktrees: phwt-ls [project]
phwt-ls() {
  local project="${1:-}"
  if [[ -n "$project" ]]; then
    git -C "$PHENOTYPE_REPOS/$project" worktree list 2>/dev/null || echo "No repo at $PHENOTYPE_REPOS/$project"
  else
    for repo_dir in "$PHENOTYPE_REPOS"/*/; do
      local repo
      repo=$(basename "$repo_dir")
      if [[ -d "$repo_dir/.git" ]] || [[ -f "$repo_dir/.git" ]]; then
        echo "=== $repo ==="
        git -C "$repo_dir" worktree list 2>/dev/null
        echo ""
      fi
    done
  fi
}

# Remove a worktree: phwt-rm <project> <topic>
phwt-rm() {
  local project="${1:?Usage: phwt-rm <project> <topic>}"
  local topic="${2:?Usage: phwt-rm <project> <topic>}"
  local wt_path="$PHENOTYPE_REPOS/worktrees/$project/$topic"
  local canon="$PHENOTYPE_REPOS/$project"

  if [[ ! -d "$wt_path" ]]; then
    echo "ERROR: Worktree not found: $wt_path" >&2
    return 1
  fi

  git -C "$canon" worktree remove "$wt_path" --force
  echo "Removed worktree: $wt_path"
}

# Quick canonical status check
phstatus() {
  for repo_dir in "$PHENOTYPE_REPOS"/*/; do
    if [[ -d "$repo_dir/.git" ]] || [[ -f "$repo_dir/.git" ]]; then
      local repo
      repo=$(basename "$repo_dir")
      local branch
      branch=$(git -C "$repo_dir" branch --show-current 2>/dev/null)
      local dirty
      dirty=$(git -C "$repo_dir" status --short 2>/dev/null | wc -l | tr -d ' ')
      printf "%-30s branch=%-20s dirty=%s\n" "$repo" "$branch" "$dirty"
    fi
  done
}
