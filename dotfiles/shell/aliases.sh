#!/usr/bin/env bash
# dotfiles/shell/aliases.sh
# Canonical shell aliases for Phenotype/thegent development environment
# Source this from ~/.zshrc or ~/.bashrc via: source "$DOTFILES_DIR/shell/aliases.sh"

# --- Safety Aliases ---
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# --- Navigation ---
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias repos='cd /Users/kooshapari/CodeProjects/Phenotype/repos'
alias pheno='cd /Users/kooshapari/CodeProjects/Phenotype'
alias dots='cd $DOTFILES_DIR'

# --- Better Core Utils (prefer modern Rust/Go replacements when available) ---
if command -v eza &>/dev/null; then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza -la --icons --group-directories-first'
  alias lt='eza --tree --icons --level=2'
else
  alias ls='ls --color=auto' 2>/dev/null || alias ls='ls -G'
  alias ll='ls -la'
fi

if command -v bat &>/dev/null; then
  alias cat='bat --style=plain'
  alias catp='bat'  # cat with paging
fi

if command -v fd &>/dev/null; then
  alias find='fd'
fi

if command -v rg &>/dev/null; then
  alias grep='rg'
fi

if command -v procs &>/dev/null; then
  alias ps='procs'
fi

if command -v btop &>/dev/null; then
  alias top='btop'
fi

# --- Git Shortcuts ---
alias g='git'
alias gs='git status --short --branch'
alias ga='git add'
alias gaa='git add -A'
alias gc='git commit'
alias gcm='git commit -m'
alias gp='git push'
alias gpl='git pull'
alias gf='git fetch'
alias gco='git checkout'
alias gb='git branch'
alias glog='git log --oneline --graph --decorate -20'
alias gdiff='git diff'
alias gds='git diff --staged'
alias gwt='git worktree'
alias gwta='git worktree add'
alias gwtl='git worktree list'
alias gwtr='git worktree remove'

# --- Package Managers ---
alias pn='pnpm'
alias pni='pnpm install'
alias pna='pnpm add'
alias pnr='pnpm run'
alias pnx='pnpm exec'

# --- Python / uv ---
alias uvr='uv run'
alias uvs='uv sync'
alias uva='uv add'
alias ptest='uv run pytest'
alias plint='uv run ruff check'
alias pfmt='uv run ruff format'

# --- Rust / Cargo ---
alias cb='cargo build'
alias ct='cargo test'
alias cr='cargo run'
alias cc='cargo check'
alias cf='cargo fmt'
alias ccl='cargo clippy'

# --- Go ---
alias gg='go get'
alias gb='go build'
alias gt='go test ./...'
alias gr='go run'
alias gvet='go vet ./...'

# --- Docker (when needed) ---
alias dk='docker'
alias dkc='docker-compose'
alias dkps='docker ps'
alias dkpsa='docker ps -a'

# --- Process Compose (thegent dev stack) ---
alias pc='process-compose'
alias pcup='process-compose up -d'
alias pcdown='process-compose down'
alias pcs='process-compose process status'
alias pcl='process-compose process logs'

# --- thegent / Phenotype Workflow ---
alias tg='thegent'
alias wtree='cd /Users/kooshapari/CodeProjects/Phenotype/repos/worktrees'
alias phlog='git -C /Users/kooshapari/CodeProjects/Phenotype/repos log --oneline -20'

# --- Claude / AI Dev ---
alias claude-hooks='ls ~/.claude/hooks/'
alias claude-settings='cat ~/.claude/settings.json | jq'

# --- Quality Gates ---
alias lint-all='task lint 2>/dev/null || make lint 2>/dev/null || echo "No lint task configured"'
alias test-all='task test 2>/dev/null || make test 2>/dev/null || echo "No test task configured"'
alias quality='task quality 2>/dev/null || make quality 2>/dev/null || echo "No quality task configured"'

# --- Misc Utilities ---
alias reload='source ~/.zshrc'
alias path='echo $PATH | tr ":" "\n"'
alias week='date +%V'
alias ports='lsof -iTCP -sTCP:LISTEN -P'
alias flushdns='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'
alias pubip='curl -s https://api.ipify.org'
alias localip='ipconfig getifaddr en0'
alias myip='echo "Local: $(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk "{print \$1}")\nPublic: $(curl -s https://api.ipify.org)"'

# --- JSON / YAML Tools ---
alias jq='jq'
alias jqp='jq "."'  # pretty print
if command -v yq &>/dev/null; then
  alias yqp='yq eval "." '  # pretty print yaml
fi

# --- Clipboard ---
if command -v pbcopy &>/dev/null; then
  alias copy='pbcopy'
  alias paste='pbpaste'
elif command -v xclip &>/dev/null; then
  alias copy='xclip -selection clipboard'
  alias paste='xclip -selection clipboard -o'
fi
