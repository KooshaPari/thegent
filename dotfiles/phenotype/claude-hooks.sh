#!/usr/bin/env bash
# dotfiles/phenotype/claude-hooks.sh
# Install/update Claude hooks from the canonical thegent location
# Usage: bash claude-hooks.sh [--check]

set -euo pipefail

THEGENT_REPO="/Users/kooshapari/CodeProjects/Phenotype/repos/thegent"
HOOKS_SRC="$THEGENT_REPO/hooks"
HOOKS_DST="$HOME/.claude/hooks"
SETTINGS_SRC="$THEGENT_REPO/settings.json"
SETTINGS_DST="$HOME/.claude/settings.json"
CHECK_ONLY="${1:-}"

log() { printf '\033[0;32m[claude-hooks]\033[0m %s\n' "$*"; }
warn() { printf '\033[0;33m[claude-hooks]\033[0m %s\n' "$*"; }
err() { printf '\033[0;31m[claude-hooks]\033[0m ERROR: %s\n' "$*" >&2; }

if [[ ! -d "$THEGENT_REPO" ]]; then
  err "thegent repo not found at $THEGENT_REPO"
  err "Run: bash $DOTFILES_DIR/phenotype/repos.sh first"
  exit 1
fi

# Sync governance docs to ~/.claude/
sync_governance() {
  local claude_dir="$HOME/.claude"
  mkdir -p "$claude_dir"

  if [[ -f "$DOTFILES_DIR/claude/CLAUDE.md" ]]; then
    if [[ "$CHECK_ONLY" == "--check" ]]; then
      log "[CHECK] Would symlink CLAUDE.md -> $claude_dir/CLAUDE.md"
    else
      ln -sf "$DOTFILES_DIR/claude/CLAUDE.md" "$claude_dir/CLAUDE.md"
      log "Symlinked CLAUDE.md -> $claude_dir/CLAUDE.md"
    fi
  fi

  if [[ -f "$DOTFILES_DIR/claude/AGENTS.md" ]]; then
    if [[ "$CHECK_ONLY" == "--check" ]]; then
      log "[CHECK] Would symlink AGENTS.md -> $claude_dir/AGENTS.md"
    else
      ln -sf "$DOTFILES_DIR/claude/AGENTS.md" "$claude_dir/AGENTS.md"
      log "Symlinked AGENTS.md -> $claude_dir/AGENTS.md"
    fi
  fi
}

# Sync hooks from thegent repo
sync_hooks() {
  if [[ ! -d "$HOOKS_SRC" ]]; then
    warn "No hooks directory at $HOOKS_SRC -- skipping"
    return 0
  fi

  if [[ "$CHECK_ONLY" == "--check" ]]; then
    log "[CHECK] Would sync hooks from $HOOKS_SRC -> $HOOKS_DST"
    ls "$HOOKS_SRC/"
    return 0
  fi

  mkdir -p "$HOOKS_DST"
  rsync -av --delete "$HOOKS_SRC/" "$HOOKS_DST/"
  find "$HOOKS_DST" -name "*.sh" -exec chmod +x {} \;
  log "Hooks synced to $HOOKS_DST"
}

# Check current symlink status
check_status() {
  log "Claude governance status:"
  echo ""
  local claude_dir="$HOME/.claude"

  for f in CLAUDE.md AGENTS.md; do
    if [[ -L "$claude_dir/$f" ]]; then
      local target
      target=$(readlink "$claude_dir/$f")
      printf "  %-20s -> %s\n" "$f" "$target"
    elif [[ -f "$claude_dir/$f" ]]; then
      printf "  %-20s (unmanaged file)\n" "$f"
    else
      printf "  %-20s (missing)\n" "$f"
    fi
  done

  echo ""
  log "Hooks:"
  ls "$HOOKS_DST/" 2>/dev/null || echo "  (no hooks installed)"
}

sync_governance
sync_hooks
check_status
