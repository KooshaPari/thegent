# thegent dotfiles — shared shell aliases
# Sourced by both .zshrc and .bashrc

# ── Navigation ────────────────────────────────────────────────────────────────
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias repos='cd ~/CodeProjects/Phenotype/repos'
alias phenotype='cd ~/CodeProjects/Phenotype'

# ── Git ───────────────────────────────────────────────────────────────────────
alias g='git'
alias gs='git status --short --branch'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate --all'
alias gd='git diff'
alias gco='git checkout'
alias gb='git branch'
alias gf='git fetch --prune'
alias gpl='git pull --rebase'
alias gwt='git worktree'
alias gwl='git worktree list'

# ── Development ───────────────────────────────────────────────────────────────
alias t='task'
alias tl='task --list'

# Language runners
alias py='python3'
alias node='bun run'         # prefer bun for running Node scripts

# Package managers (prefer fast/modern alternatives)
alias nr='bun run'           # npm run → bun run
alias ni='bun install'       # npm install → bun install
alias nx='bunx'              # npx → bunx

# ── Docker / containers ───────────────────────────────────────────────────────
alias d='docker'
alias dc='docker compose'
alias dps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# ── Misc ──────────────────────────────────────────────────────────────────────
alias reload='exec $SHELL'
alias path='echo $PATH | tr ":" "\n"'
alias ports='lsof -i -P -n | grep LISTEN'
alias ip='curl -s https://api.ipify.org && echo'
alias pubkey='cat ~/.ssh/id_ed25519.pub | pbcopy && echo "Public key copied to clipboard"'

# ── Process management ────────────────────────────────────────────────────────
alias psg='ps aux | grep'
alias killport='f() { lsof -ti tcp:$1 | xargs kill -9; }; f'

# ── Clipboard (cross-platform) ────────────────────────────────────────────────
if command -v pbcopy >/dev/null 2>&1; then
  alias copy='pbcopy'
  alias paste='pbpaste'
elif command -v xclip >/dev/null 2>&1; then
  alias copy='xclip -selection clipboard'
  alias paste='xclip -selection clipboard -o'
elif command -v wl-copy >/dev/null 2>&1; then
  alias copy='wl-copy'
  alias paste='wl-paste'
fi

# ── Phenotype org helpers ─────────────────────────────────────────────────────
# Open PR for current branch
alias propen='gh pr create --web'
# View open PRs for current repo
alias prs='gh pr list'
# Quick worktree creation following governance rules
wtnew() {
  local name="${1:?Usage: wtnew <branch-name>}"
  local repo
  repo="$(basename "$(git rev-parse --show-toplevel)")"
  git worktree add "../${repo}-wtrees/${name}" -b "${name}"
}
