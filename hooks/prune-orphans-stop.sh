#!/bin/zsh
# prune-orphans-stop.sh — Stop hook
# Auto-prune redundant agent-related processes (LSPs, MCP servers, cc-status, etc.)
# when count exceeds threshold. Runs on Stop when THGENT_AUTO_PRUNE=1.
# Advisory only (always exits 0). Debounced by cooldown.
# See: docs/reference/SWARM_PROCESS_OPTIMIZATIONS.md
set -euo pipefail

# Stderr message on unexpected failure
trap 'echo "PRUNE-ORPHANS FAIL: unexpected error at line $LINENO" >&2' ERR

# Opt-in: disabled by default
[[ "${THGENT_AUTO_PRUNE:-0}" == "1" ]] || exit 0

readonly _THRESHOLD="${THGENT_AUTO_PRUNE_THRESHOLD:-12}"
readonly _CC_STATUS_THRESHOLD="${THGENT_AUTO_PRUNE_CC_STATUS_THRESHOLD:-3}"
readonly _COOLDOWN="${THGENT_AUTO_PRUNE_COOLDOWN:-300}"
readonly _COOLDOWN_JITTER="${THGENT_AUTO_PRUNE_COOLDOWN_JITTER:-30}"
readonly _MEM_THRESHOLD="${THGENT_AUTO_PRUNE_MEMORY_THRESHOLD_MB:-0}"
readonly _STATE_DIR="${TMPDIR:-/tmp}/thegent-prune-$(id -u)"
readonly _LAST_PRUNE="${_STATE_DIR}/last-prune"

mkdir -p "$_STATE_DIR"

# Patterns for redundant processes (must match those in thegent mcp prune)
_patterns="pyright-langserver|typescript-language-server|tsserver\.js|@playwright/mcp|context7-mcp|cc-status|octocode-mcp|next-devtools-mcp|sequential-thinking"

# Count node/bun/deno processes matching our patterns
_count=$(ps -eo pid,command 2>/dev/null | grep -E "node|npm|bun|deno|cc-status" | grep -cE "(${_patterns})" || true)
[[ -z "$_count" ]] && _count=0

# cc-status-specific count (often high-RSS; lower threshold)
_cc_count=$(ps -eo pid,command 2>/dev/null | grep -cE "cc-status" || true)
[[ -z "$_cc_count" ]] && _cc_count=0

# Available memory (MB): Linux /proc/meminfo, macOS vm_stat
_available_mb=99999
if [[ -f /proc/meminfo ]]; then
  _avail_kb=$(grep -E '^MemAvailable:' /proc/meminfo 2>/dev/null | awk '{print $2}' || echo 0)
  _available_mb=$(( _avail_kb / 1024 ))
elif command -v vm_stat >/dev/null 2>&1; then
  _vm=$(vm_stat 2>/dev/null)
  _free=$(echo "$_vm" | grep "Pages free:" | sed 's/.*: *\([0-9]*\).*/\1/')
  _inactive=$(echo "$_vm" | grep "Pages inactive:" | sed 's/.*: *\([0-9]*\).*/\1/')
  _free=${_free:-0}
  _inactive=${_inactive:-0}
  _available_mb=$(( (_free + _inactive) * 4096 / 1024 / 1024 ))
fi

# Cooldown: skip if we pruned recently
if [[ -f "$_LAST_PRUNE" ]]; then
  _last=$(stat -f '%m' "$_LAST_PRUNE" 2>/dev/null || stat -c '%Y' "$_LAST_PRUNE" 2>/dev/null || echo 0)
  _now=$(date +%s)
  if (( _now - _last < _COOLDOWN )); then
    exit 0
  fi
fi

# Prune when: (a) orphan count >= threshold, (b) cc-status >= cc threshold, or (c) memory < threshold (if set)
_should_prune=0
if (( _count >= _THRESHOLD )); then
  _should_prune=1
elif (( _cc_count >= _CC_STATUS_THRESHOLD )); then
  _should_prune=1
elif [[ -n "$_MEM_THRESHOLD" ]] && (( _MEM_THRESHOLD > 0 )) && (( _available_mb < _MEM_THRESHOLD )); then
  _should_prune=1
fi
[[ "$_should_prune" -eq 0 ]] && exit 0

# Jitter: stagger prune calls when multiple Stop events fire (avoid thundering herd)
_jitter=$(( RANDOM % (_COOLDOWN_JITTER + 1) ))
[[ "$_jitter" -gt 0 ]] && sleep "$_jitter"

# Run prune with retry+backoff on failure (ADVANCED_STRATEGIES §2.4)
# Log errors instead of suppressing them so user knows what triggered pruning
if command -v thegent >/dev/null 2>&1; then
  _prune_rc=1
  for _attempt in 1 2 3; do
    # Log what's triggering the prune
    echo "THEGENT PRUNE: Auto-prune hook triggered (attempt $_attempt/3)" >&2
    echo "THEGENT PRUNE: Reason: orphan count=$_count, cc-status=$_cc_count, available_mb=$_available_mb" >&2

    if thegent mcp prune --force 2>&1; then
      _prune_rc=0
      echo "THEGENT PRUNE: Successfully pruned processes" >&2
      break
    else
      _prune_err=$?
      echo "THEGENT PRUNE: Prune attempt $_attempt failed with exit code $_prune_err" >&2
    fi
    [[ $_attempt -lt 3 ]] && sleep $(( 2 ** _attempt ))
  done
  echo "$(date +%s)" > "$_LAST_PRUNE" 2>/dev/null || true
fi

exit 0
