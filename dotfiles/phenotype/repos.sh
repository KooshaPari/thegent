#!/usr/bin/env bash
# dotfiles/phenotype/repos.sh
# Clone all Phenotype repos to the correct locations
# Usage: bash repos.sh [--dry-run]
# Run with --dry-run to see what would happen without cloning

set -euo pipefail

PHENOTYPE_ROOT="/Users/kooshapari/CodeProjects/Phenotype/repos"
DRY_RUN="${1:-}"

log() { printf '\033[0;32m[repos]\033[0m %s\n' "$*"; }
warn() { printf '\033[0;33m[repos]\033[0m %s\n' "$*"; }
err() { printf '\033[0;31m[repos]\033[0m ERROR: %s\n' "$*" >&2; }

clone_repo() {
  local repo="$1"
  local dest="$PHENOTYPE_ROOT/$repo"
  local url="https://github.com/KooshaPari/$repo.git"

  if [[ -d "$dest/.git" ]]; then
    log "Already cloned: $repo"
    return 0
  fi

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log "[DRY-RUN] Would clone $url -> $dest"
    return 0
  fi

  log "Cloning $repo..."
  git clone "$url" "$dest"
  log "Cloned $repo"
}

ensure_worktree_dir() {
  local repo="$1"
  local wt_dir="$PHENOTYPE_ROOT/worktrees/$repo"
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log "[DRY-RUN] Would ensure worktree dir: $wt_dir"
    return 0
  fi
  mkdir -p "$wt_dir"
}

# --- Core Repos ---
PHENOTYPE_REPOS=(
  "thegent"
  "AgilePlus"
  "heliosApp"
  "bifrost-extensions"
  "phenotype-infrakit"
  "TraceRTM"
)

log "Setting up Phenotype workspace at $PHENOTYPE_ROOT"
mkdir -p "$PHENOTYPE_ROOT"

for repo in "${PHENOTYPE_REPOS[@]}"; do
  clone_repo "$repo"
  ensure_worktree_dir "$repo"
done

log "Phenotype workspace setup complete"
log "Repos are at: $PHENOTYPE_ROOT"
log "Worktree dirs at: $PHENOTYPE_ROOT/worktrees/"
