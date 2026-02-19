#!/bin/zsh
# Fast-path wrapper for which command
# Prevents shell initialization cascades during PATH resolution

which() {
    # Set flag to skip wrapper functions during PATH resolution
    export _RESOLVING_PATH=1
    
    # Use system which directly
    command which "$@"
    local exit_code=$?
    
    # Unset flag
    unset _RESOLVING_PATH
    
    return $exit_code
}

# Export for subprocesses
export -f which
