#!/bin/zsh
# spec-preflight.sh — SessionStart hook
# Detects project state (greenfield/brownfield), checks spec docs & trackers.
# Must exit 0 always, target <80ms. Zero subprocess forks in dispatched mode.
set -euo pipefail

trap 'echo "SPEC-PREFLIGHT FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast-path: skip common.sh if dispatched ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  : # no timestamp needed — output is plain text
else
  HOOK_NAME="SPEC-PREFLIGHT"
  # shellcheck source=./lib/common.sh
  source "${BASH_SOURCE[0]%/*}/lib/common.sh"
  hook_init
fi

_PD="${PROJECT_DIR:-.}"

# ---------- gather data (zero forks) ----------
# Check for .git/HEAD instead of forking git rev-parse (saves ~36ms)
HAS_COMMITS=true
[[ -f "$_PD/.git/HEAD" ]] || HAS_COMMITS=false

# Source file heuristic: check if any src/lib/app dir exists with files.
# Single glob per dir instead of 12-extension loop (saves ~70ms).
HAS_SRC=false
for d in "$_PD/src" "$_PD/lib" "$_PD/app" "$_PD/cli"; do
  if [[ -d "$d" ]]; then
    # One compgen for any file (not per-extension)
    compgen -G "$d/*" >/dev/null 2>&1 && { HAS_SRC=true; break; }
  fi
done

# Trivial project gate: no git, no source dirs -> skip everything
if [[ "$HAS_COMMITS" == false && "$HAS_SRC" == false ]]; then
  exit 0
fi

# ---------- spec docs (file existence via builtin [[ -f ]]) ----------
_sp=0 _sm=0
_sp_list="" _sm_list=""
for name in PRD.md ADR.md FUNCTIONAL_REQUIREMENTS.md PLAN.md USER_JOURNEYS.md; do
  if [[ -f "$_PD/$name" ]]; then
    (( ++_sp ))
    [[ -n "$_sp_list" ]] && _sp_list+="," ; _sp_list+="$name"
  else
    (( ++_sm ))
    [[ -n "$_sm_list" ]] && _sm_list+="," ; _sm_list+="$name"
  fi
done

# ---------- trackers ----------
_tp=0 _tm=0
_tp_list="" _tm_list=""
for name in PRD_TRACKER.md ADR_STATUS.md FR_TRACKER.md PLAN_STATUS.md JOURNEY_VALIDATION.md CODE_ENTITY_MAP.md; do
  if [[ -f "$_PD/docs/reference/$name" ]]; then
    (( ++_tp ))
    [[ -n "$_tp_list" ]] && _tp_list+="," ; _tp_list+="$name"
  else
    (( ++_tm ))
    [[ -n "$_tm_list" ]] && _tm_list+="," ; _tm_list+="$name"
  fi
done

# ---------- classify ----------
if [[ "$HAS_COMMITS" == false && "$HAS_SRC" == false && $_sp -eq 0 ]]; then
  PROJECT_TYPE="Greenfield"
elif [[ "$HAS_COMMITS" == false && $_sp -eq 0 ]]; then
  PROJECT_TYPE="Greenfield"
else
  PROJECT_TYPE="Brownfield"
fi

# ---------- output ----------
echo "PROJECT STATE: $PROJECT_TYPE"

if (( _sp == 5 )); then
  echo "SPEC DOCS: All present (PRD, ADR, FR, PLAN, UJ)"
elif (( _sp == 0 )); then
  echo "SPEC DOCS: None found"
else
  echo "SPEC DOCS PRESENT: $_sp_list"
  echo "SPEC DOCS MISSING: $_sm_list"
fi

if [[ "$PROJECT_TYPE" == "Brownfield" || $_sp -gt 0 ]]; then
  if (( _tp == 6 )); then
    echo "TRACKERS: All present"
  elif (( _tp > 0 )); then
    echo "TRACKERS PRESENT: $_tp_list"
    (( _tm > 0 )) && echo "TRACKERS MISSING: $_tm_list"
  else
    (( _tm > 0 )) && echo "TRACKERS MISSING: $_tm_list"
  fi
fi

if [[ "$PROJECT_TYPE" == "Greenfield" && $_sp -eq 0 ]]; then
  echo "SUGGESTION: This project has no specification documentation. When appropriate, offer to generate PRD, ADR, FR, PLAN, and USER_JOURNEYS using templates from ~/.claude/templates/"
fi

exit 0
