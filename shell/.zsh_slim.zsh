# thegent Slim-Shell for Agents
# Minimal, high-performance Zsh configuration for AI agents.
# Optimized for <10ms startup latency by bypassing all visual/interactive components.

# G-DX-04: Fast-path for agent sub-shells. Bypasses standard .zshrc logic.
export THEGENT_SLIM_SHELL=1

# Disable completion system (too slow for non-interactive agent use)
# agents use direct CLI calls or JSON-only mode in GSH.
unsetopt AUTO_LIST
unsetopt AUTO_MENU
unsetopt MENU_COMPLETE

# Minimal path for speed - agents should use absolute paths where possible
# but we keep core POSIX/thegent paths.
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin"

# Disable history (agents should not pollute human history)
# GSH (JSON mode) handles its own task-centric history.
unset HISTFILE
export HISTSIZE=0
export SAVEHIST=0

# Disable all prompt themes/styling
PROMPT='%# '
RPROMPT=''

# Speed up globbing
unsetopt NOMATCH

# G-GP-02: Input/Output guardrails for agent shells
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# thegent integration
if [[ -n "$THEGENT_ROOT" ]]; then
  export PATH="$THEGENT_ROOT/bin:$PATH"
fi

# Optimization: Silence all non-essential output
# exec 2>/dev/null # This might be too aggressive, better handled by thegent runner

# Ready signal for parent process (if needed)
# echo "thegent-slim-ready"
