# lib/completions.zsh - Tab completions for thegent integration

# Enable completions
autoload -Uz compinit
compinit

# --- tg command completions ---
_tg() {
  local -a commands
  commands=(
    'run:Execute agent task'
    'free:Run with free tier (default)'
    'bg:Background execution'
    'ps:List active sessions'
    'skills:List available skills'
    'hooks:List lifecycle hooks'
    'lsp:LSP server management'
    'mcp:MCP server management'
    'serve:Start MCP server'
    'plan:Plan management'
    'p:Quick prompt (alias for run)'
    'f:Run agent on file (alias for tgf)'
    'w:Watch mode (alias for tgw)'
    's:Run skill (alias for tgs)'
    'who:Show current agent context'
    'work:Show work stream'
    'next:Get next item from work stream'
    'log:View thegent logs'
    'status:Quick status check'
    'doc:Open thegent docs'
    'help:Show help'
  )
  
  _describe 'command' commands
}

compdef _tg tg

# --- thegent run completions ---
_thegent_run() {
  local -a opts
  opts=(
    '-d+[Working directory]:directory:_directories'
    '-m+[Mode]:mode:(read-only write read-write)'
    '-M+[Model]:model:->models'
    '-t+[Timeout in seconds]:timeout:'
    '-P+[Provider]:provider:(free claude gemini antigravity cursor kiro)'
    '-b[Background mode]'
    '-d[Debug mode]'
    '-C+[Continue session]:session_id:'
    '--agent+[Agent name]:agent:'
    '--skill+[Skill name]:skill:'
    '--override+[Override prompt]:prompt:'
    '--model-first[Model-first mode]'
    '--failover[Allow failover]'
  )
  
  _arguments -s -A '-*' "$opts" '1:prompt: '
}

compdef _thegent_run thegent-run

# --- thegent free completions ---
_thegent_free() {
  local -a opts
  opts=(
    '-d+[Working directory]:directory:_directories'
    '-m+[Mode]:mode:(read-only write read-write)'
    '-t+[Timeout in seconds]:timeout:'
    '-b[Background mode]'
    '-d[Debug mode]'
    '-C+[Continue session]:session_id:'
    '--do-next[Get next item from work stream]'
    '--skill+[Skill name]:skill:'
    '--model-first[Model-first mode]'
  )
  
  _arguments -s -A '-*' "$opts" '1:prompt: '
}

compdef _thegent_free thegent-free

# --- thegent bg completions ---
_thegent_bg() {
  local -a opts
  opts=(
    '-d+[Working directory]:directory:_directories'
    '-m+[Mode]:mode:(read-only write read-write)'
    '-t+[Timeout in seconds]:timeout:'
    '-C+[Continue session]:session_id:'
    '-d[Debug mode]'
    '--skill+[Skill name]:skill:'
  )
  
  _arguments -s -A '-*' "$opts" '1:prompt: '
}

compdef _thegent_bg thegent-bg

# --- thegent skills completions ---
_thegent_skills() {
  local -a commands
  commands=(
    'list:List all available skills'
    'show:Show skill details'
    'add:Add a new skill'
    'remove:Remove a skill'
  )
  
  _describe 'command' commands
}

compdef _thegent_skills thegent-skills

# --- thegent hooks completions ---
_thegent_hooks() {
  local -a commands
  commands=(
    'list:List all lifecycle hooks'
    'run:Run a specific hook'
    'enable:Enable a hook'
    'disable:Disable a hook'
    'status:Show hook status'
  )
  
  _describe 'command' commands
}

compdef _thegent_hooks thegent-hooks

# --- thegent lsp completions ---
_thegent_lsp() {
  local -a commands
  commands=(
    'status:Show LSP server status'
    'start:Start LSP server'
    'stop:Stop LSP server'
    'restart:Restart LSP server'
    'list:List available LSP servers'
    'install:Install LSP server'
    'uninstall:Uninstall LSP server'
  )
  
  _describe 'command' commands
}

compdef _thegent_lsp thegent-lsp

# --- thegent mcp completions ---
_thegent_mcp() {
  local -a commands
  commands=(
    'up:Start MCP server'
    'down:Stop MCP server'
    'status:Show MCP server status'
    'restart:Restart MCP server'
    'prune:Cleanup orphaned processes'
    'list:List available MCP tools'
    'serve:Start MCP server (alias for up)'
  )
  
  _describe 'command' commands
}

compdef _thegent_mcp thegent-mcp

# --- thegent plan completions ---
_thegent_plan() {
  local -a commands
  commands=(
    'do-next:Get next actionable item'
    'list:List all plan items'
    'status:Show plan status'
    'add:Add item to plan'
    'remove:Remove item from plan'
    'loop:Start continuous work loop'
    'wait-next:Wait for next item'
    'incorporate:Incorporate plan fragments'
  )
  
  _describe 'command' commands
}

compdef _thegent_plan thegent-plan

# --- thegent completions (main) ---
_thegent() {
  local -a commands
  commands=(
    'run:Execute agent task'
    'free:Run with free tier'
    'bg:Background execution'
    'ps:List active sessions'
    'stop:Stop a session'
    'status:Show status'
    'skills:Manage skills'
    'hooks:Manage lifecycle hooks'
    'lsp:Manage LSP servers'
    'mcp:Manage MCP servers'
    'plan:Plan management'
    'serve:Start MCP server'
    'doctor:Run diagnostics'
    'prompts:Show prompts'
    'version:Show version'
    'help:Show help'
  )
  
  _describe 'command' commands
}

compdef _thegent thegent

# --- tgf file completion ---
_tgf() {
  _files
}

compdef _tgf tgf

# --- tgs skill completion ---
_tgs() {
  local -a skills
  skills=(
    'sitback-agent:Sitback agent for monitoring'
    'agent-orchestra:Orchestrate multiple agents'
    'explore:Explore codebase'
    'plan:Plan agent for design'
    'research:Research agent'
    'general-purpose:General purpose agent'
  )
  
  _describe 'skill' skills
}

compdef _tgs tgs

# --- tgmcp completion ---
_tgmcp() {
  local -a commands
  commands=(
    'up:Start MCP server'
    'down:Stop MCP server'
    'status:Show status'
    'prune:Cleanup processes'
    'restart:Restart server'
  )
  
  _describe 'command' commands
}

compdef _tgmcp tgmcp

# --- tglog completion ---
_tglog() {
  _arguments '1:lines:(10 20 50 100 200)' '2:log file:_files'
}

compdef _tglog tglog

# Style for completions
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path ~/.zcompcache

# Group by category
zstyle ':completion:*' group-name ''
zstyle ':completion:*' descriptive-prefixes

# Add colors to descriptions
zstyle ':completion:*:descriptions' format '%B%d%b'

# Fuzzy matching
zstyle ':completion:*' fuzzy true
zstyle ':completion:*' match-original both
