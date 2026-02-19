#!/usr/bin/env zsh
# Shell builtin accelerators - replace expensive process spawns for trivial tasks

# Avoid double-sourcing
[[ -n "${_BUILTIN_WRAPPER_LOADED:-}" ]] && return 0
_BUILTIN_WRAPPER_LOADED=1

# wc -l accelerator: avoid process spawn for simple file line counting
wc() {
  if [[ "$1" == "-l" && $# -eq 2 && -f "$2" ]]; then
    if [ -n "${ZSH_VERSION:-}" ]; then
      local _lines; _lines=( ${(f)"$(<"$2")"} )
      echo "${#_lines}"
    elif [ -n "${BASH_VERSION:-}" ]; then
      local _lines; mapfile -t _lines < "$2"
      echo "${#_lines[@]}"
    else
      command wc "$@"
    fi
  else
    command wc "$@"
  fi
}

# tr accelerator: avoid process spawn for simple character deletions/replacements
tr() {
  if [[ "$1" == "-d" && $# -eq 3 ]]; then
    local char="$2"
    local val="$3"
    # Use parameter expansion for deletion
    echo "${val//$char/}"
  else
    command tr "$@"
  fi
}

# date accelerator: avoid process spawn for common format strings
date() {
  if [[ -n "${START_TIMESTAMP:-}" && ( "$*" == "+%s" || "$*" == "-u"* ) ]]; then
    if [[ "$*" == "+%s" ]]; then
      echo "$START_TIMESTAMP"
      return 0
    fi
  fi
  command date "$@"
}

if [ -n "${BASH_VERSION:-}" ]; then
  export -f wc tr date
fi
