#!/bin/bash
# Safe grep wrapper that avoids alias/config issues
# Use this instead of rg or grep when encountering config errors

# Force use of /usr/bin/grep or system binary
SAFE_GREP=$(command -v grep)
SAFE_RG=$(command -v rg)

if [ "$1" = "rg" ]; then
    shift
    exec "$SAFE_RG" "$@"
elif [ "$1" = "grep" ]; then
    shift
    exec "$SAFE_GREP" "$@"
else
    # Default to rg
    exec "$SAFE_RG" "$@"
fi
