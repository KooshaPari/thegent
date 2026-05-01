# lib/index.zsh - Barrel export for thegent zsh integration
# Sources all .zsh files in the lib directory

# Determine the directory where this script resides
[[ -n "${(%):-%x}" ]] && local _lib_dir="${(%):-%x:A:h}" || local _lib_dir="${0:a:h}"

# Source all .zsh files in order
# Order matters: functions must be loaded before async (which may use them)
for _zf in "$_lib_dir"/*.zsh(N); do
  [[ "$_zf" == "${0:a}" ]] && continue  # Skip self
  source "$_zf"
done

# Cleanup temp variables
unset _lib_dir _zf
