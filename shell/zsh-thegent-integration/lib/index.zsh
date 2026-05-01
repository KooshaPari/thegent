# lib/index.zsh - Barrel export for thegent zsh integration
# Sources all .zsh files in the lib directory

# Determine the directory where this script resides
[[ -n "${(%):-%x}" ]] && local _lib_dir="${(%):-%x:A:h}" || local _lib_dir="${0:a:h}"

# Source all .zsh files in EXPLICIT order (not glob/alphabetical)
# Order matters:
#   1. functions.zsh - Core functions may be used by async operations
#   2. async.zsh - Async job management depends on base functions
#   3. completions.zsh - Completions load last (can reference any function)
local -a _zsh_files=(
  "$_lib_dir/functions.zsh"
  "$_lib_dir/async.zsh"
  "$_lib_dir/completions.zsh"
)

for _zf in "${_zsh_files[@]}"; do
  [[ "$_zf" == "${0:a}" ]] && continue # Skip self
  if [[ -f "$_zf" ]]; then
    source "$_zf"
  fi
done

# Cleanup temp variables
unset _lib_dir _zf _zsh_files
