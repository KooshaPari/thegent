#!/usr/bin/env zsh
# harvest-idea-seeds.sh — Harvest $idea and $defer/$pending from Claude Code, Codex, and Cursor.
# Run periodically (cron, Stop, or manual) to capture ideas before sessions expire (~2 weeks).
# $idea → docs/research/idea-seeds/; $defer/$pending → pending-handoff.md
set -euo pipefail

IDEA_FLAG='$idea'
CLAUDE_HISTORY="${CLAUDE_HISTORY:-$HOME/.claude/history.jsonl}"
CODEX_HISTORY="${CODEX_HISTORY:-$HOME/.codex/history.jsonl}"
# Only use default when unset; CURSOR_PROJECTS= explicitly skips Cursor harvest
[[ -z "${CURSOR_PROJECTS+x}" ]] && CURSOR_PROJECTS="$HOME/.cursor/projects"
OUTPUT_DIR="${OUTPUT_DIR:-}"
STATE_DIR="${STATE_DIR:-$HOME/.claude}"
CLAUDE_OFFSET_FILE="$STATE_DIR/.idea-harvest-claude-offset"
CODEX_OFFSET_FILE="$STATE_DIR/.idea-harvest-codex-offset"
CURSOR_HARVESTED_FILE="$STATE_DIR/.idea-harvest-cursor-done"
CODEX_STATE_DB="${CODEX_STATE_DB:-$HOME/.codex/state_5.sqlite}"

# Fallback output: ~/.claude/idea-seeds (used when project/cwd unknown)
FALLBACK_OUTPUT="$HOME/.claude/idea-seeds"
mkdir -p "$FALLBACK_OUTPUT"

# Resolve project root from path (git root if in repo, else dir as-is)
resolve_project_root() {
  local dir="$1"
  [[ -z "$dir" || ! -d "$dir" ]] && return
  (cd "$dir" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null) || echo "$dir"
}

harvest_claude() {
  [[ ! -f "$CLAUDE_HISTORY" ]] && return 0
  local offset=0
  [[ -f "$CLAUDE_OFFSET_FILE" ]] && offset=$(<"$CLAUDE_OFFSET_FILE")
  local line_num=0
  local count=0
  while IFS= read -r line; do
    (( line_num++ )) || true
    [[ $line_num -le $offset ]] && continue
    [[ -z "$line" ]] && continue
    local display
    display=$(echo "$line" | jq -r '.display // empty' 2>/dev/null) || continue
    [[ -z "$display" ]] && continue
    local has_idea=false
    local has_defer=false
    [[ "$display" == *"$IDEA_FLAG"* ]] && has_idea=true
    if [[ "$display" == *'$defer'* ]] || [[ "$display" == *'$pending'* ]]; then
      has_defer=true
    fi
    [[ "$has_idea" != "true" && "$has_defer" != "true" ]] && continue
    local project ts session_id
    project=$(echo "$line" | jq -r '.project // ""' 2>/dev/null)
    ts=$(echo "$line" | jq -r '.timestamp // 0' 2>/dev/null)
    session_id=$(echo "$line" | jq -r '.sessionId // ""' 2>/dev/null)
    local out_sub="$FALLBACK_OUTPUT"
    if [[ -n "$project" && -d "$project" ]]; then
      local root
      root=$(resolve_project_root "$project")
      [[ -n "$root" ]] && out_sub="$root/docs/research/idea-seeds"
    fi
    [[ -n "$OUTPUT_DIR" ]] && out_sub="$OUTPUT_DIR"
    mkdir -p "$out_sub"
    local ts_iso
    if [[ "$(uname -s)" == "Darwin" ]]; then
      ts_iso=$(date -r "$(( ts / 1000 ))" -u +%Y%m%dT%H%M%SZ 2>/dev/null) || ts_iso=$(date -u +%Y%m%dT%H%M%SZ)
    else
      ts_iso=$(date -d "@$(( ts / 1000 ))" -u +%Y%m%dT%H%M%SZ 2>/dev/null) || ts_iso=$(date -u +%Y%m%dT%H%M%SZ)
    fi
    if [[ "$has_defer" == "true" ]]; then
      local handoff
      handoff="$out_sub/../pending-handoff.md"
      [[ "$out_sub" == "$FALLBACK_OUTPUT" ]] && handoff="$STATE_DIR/pending-handoff.md"
      mkdir -p "$(dirname "$handoff")"
      {
        echo ""
        echo "# From Claude history (harvest $ts_iso)"
        echo ""
        echo "1. $(echo "$display" | sed 's/\$defer//g; s/\$pending//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        echo ""
      } >> "$handoff"
    fi
    if [[ "$has_idea" == "true" ]]; then
      local f="$out_sub/seed_claude_${ts_iso}_${line_num}.md"
      {
        echo "---"
        echo "saved_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "source: claude_history"
        echo "project: $project"
        echo "session_id: $session_id"
        echo "---"
        echo ""
        echo "$display"
      } > "$f"
    fi
    (( count++ )) || true
  done < "$CLAUDE_HISTORY"
  echo "$line_num" > "$CLAUDE_OFFSET_FILE"
  echo "Claude: harvested $count idea(s)"
}

# Get Codex cwd for session from state_5.sqlite threads table
codex_cwd_for_session() {
  local sid="$1"
  [[ -z "$sid" ]] && return
  [[ ! -f "$CODEX_STATE_DB" ]] && return
  sid="${sid//\'/\'\'}"
  sqlite3 -noheader "$CODEX_STATE_DB" "SELECT cwd FROM threads WHERE id='$sid' LIMIT 1" 2>/dev/null
}

harvest_codex() {
  [[ ! -f "$CODEX_HISTORY" ]] && return 0
  local offset=0
  [[ -f "$CODEX_OFFSET_FILE" ]] && offset=$(<"$CODEX_OFFSET_FILE")
  local line_num=0
  local count=0
  while IFS= read -r line; do
    (( line_num++ )) || true
    [[ $line_num -le $offset ]] && continue
    [[ -z "$line" ]] && continue
    local text
    text=$(echo "$line" | jq -r '.text // empty' 2>/dev/null) || continue
    [[ -z "$text" ]] && continue
    local has_idea=false
    local has_defer=false
    [[ "$text" == *"$IDEA_FLAG"* ]] && has_idea=true
    if [[ "$text" == *'$defer'* ]] || [[ "$text" == *'$pending'* ]]; then
      has_defer=true
    fi
    [[ "$has_idea" != "true" && "$has_defer" != "true" ]] && continue
    local session_id ts
    session_id=$(echo "$line" | jq -r '.session_id // ""' 2>/dev/null)
    ts=$(echo "$line" | jq -r '.ts // 0' 2>/dev/null)
    local out_sub="$FALLBACK_OUTPUT"
    local cwd
    cwd=$(codex_cwd_for_session "$session_id")
    if [[ -n "$cwd" && -d "$cwd" ]]; then
      local root
      root=$(resolve_project_root "$cwd")
      [[ -n "$root" ]] && out_sub="$root/docs/research/idea-seeds"
    fi
    [[ -n "$OUTPUT_DIR" ]] && out_sub="$OUTPUT_DIR"
    mkdir -p "$out_sub"
    local ts_iso
    if [[ "$(uname -s)" == "Darwin" ]]; then
      ts_iso=$(date -r "$ts" -u +%Y%m%dT%H%M%SZ 2>/dev/null) || ts_iso=$(date -u +%Y%m%dT%H%M%SZ)
    else
      ts_iso=$(date -d "@$ts" -u +%Y%m%dT%H%M%SZ 2>/dev/null) || ts_iso=$(date -u +%Y%m%dT%H%M%SZ)
    fi
    if [[ "$has_defer" == "true" ]]; then
      local handoff
      handoff="$out_sub/../pending-handoff.md"
      [[ "$out_sub" == "$FALLBACK_OUTPUT" ]] && handoff="$STATE_DIR/pending-handoff.md"
      mkdir -p "$(dirname "$handoff")"
      {
        echo ""
        echo "# From Codex history (harvest $ts_iso)"
        echo ""
        echo "1. $(echo "$text" | sed 's/\$defer//g; s/\$pending//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        echo ""
      } >> "$handoff"
    fi
    if [[ "$has_idea" == "true" ]]; then
      local f="$out_sub/seed_codex_${ts_iso}_${line_num}.md"
      {
        echo "---"
        echo "saved_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "source: codex_history"
        echo "session_id: $session_id"
        echo "cwd: $cwd"
        echo "---"
        echo ""
        echo "$text"
      } > "$f"
    fi
    (( count++ )) || true
  done < "$CODEX_HISTORY"
  echo "$line_num" > "$CODEX_OFFSET_FILE"
  echo "Codex: harvested $count idea(s)"
}

# Resolve Cursor project folder to workspace path. Folder format: path segments joined by -.
# Try 1: decode (split on -, join with /) — works when no segment contains -.
# Try 2: grep agent-tools for path containing last segment (e.g. thegent).
cursor_project_path() {
  local folder="$1"
  [[ -z "$folder" ]] && return
  local proj_dir="$CURSOR_PROJECTS/$folder"
  local path
  path=$(echo "$folder" | awk -F'-' '{s=""; for(i=1;i<=NF;i++) s=s"/"$i; print s}')
  [[ -n "$path" && -d "$path" ]] && echo "$path" && return
  local last_seg
  last_seg=$(echo "$folder" | awk -F'-' '{print $NF}')
  [[ -z "$last_seg" ]] && return
  for f in "$proj_dir"/agent-tools/*.txt "$proj_dir"/agent-transcripts/*.jsonl; do
    [[ -f "$f" ]] || continue
    path=$(grep -oE "/Users/[^ ]*/${last_seg}" "$f" 2>/dev/null | head -1) || true
    [[ -n "$path" && -d "$path" ]] && echo "$path" && return
  done
}

# Get offset for a transcript file from state
cursor_get_offset() {
  local f="$1"
  [[ ! -f "$CURSOR_HARVESTED_FILE" ]] && echo "0" && return
  grep -F "$f:" "$CURSOR_HARVESTED_FILE" 2>/dev/null | tail -1 | cut -d: -f2- || echo "0"
}

harvest_cursor() {
  [[ -z "$CURSOR_PROJECTS" || ! -d "$CURSOR_PROJECTS" ]] && return 0
  local count=0
  local offset_file="$CURSOR_HARVESTED_FILE"
  : > "${offset_file}.tmp" 2>/dev/null || true
  for proj_dir in "$CURSOR_PROJECTS"/Users-*/; do
    [[ -d "$proj_dir" ]] || continue
    local agent_dir="$proj_dir/agent-transcripts"
    [[ ! -d "$agent_dir" ]] && continue
    local project_path
    project_path=$(cursor_project_path "$(basename "$proj_dir")")
    local out_sub="$FALLBACK_OUTPUT"
    if [[ -n "$project_path" ]]; then
      local root
      root=$(resolve_project_root "$project_path")
      [[ -n "$root" ]] && out_sub="$root/docs/research/idea-seeds"
    fi
    [[ -n "$OUTPUT_DIR" ]] && out_sub="$OUTPUT_DIR"
    mkdir -p "$out_sub"
    for jsonl in "$agent_dir"/*.jsonl; do
      [[ -f "$jsonl" ]] || continue
      local offset
      offset=$(cursor_get_offset "$jsonl")
      offset="${offset:-0}"
      local line_num=0
      while IFS= read -r line; do
        (( line_num++ )) || true
        [[ $line_num -le $offset ]] && continue
        [[ -z "$line" ]] && continue
        local role text
        role=$(echo "$line" | jq -r '.role // empty' 2>/dev/null)
        [[ "$role" != "user" ]] && continue
        text=$(echo "$line" | jq -r '.message.content[]? | select(.type=="text") | .text // empty' 2>/dev/null)
        [[ -z "$text" ]] && continue
        local has_idea=false
        local has_defer=false
        [[ "$text" == *"$IDEA_FLAG"* ]] && has_idea=true
        if [[ "$text" == *'$defer'* ]] || [[ "$text" == *'$pending'* ]]; then
          has_defer=true
        fi
        [[ "$has_idea" != "true" && "$has_defer" != "true" ]] && continue
        local ts_iso session_id
        local current_jsonl="$jsonl"
        session_id=$(basename "$current_jsonl" .jsonl)
        ts_iso=$(date -u +%Y%m%dT%H%M%SZ)
        if [[ "$has_defer" == "true" ]]; then
          local handoff
          handoff="$out_sub/../pending-handoff.md"
          [[ "$out_sub" == "$FALLBACK_OUTPUT" ]] && handoff="$STATE_DIR/pending-handoff.md"
          mkdir -p "$(dirname "$handoff")"
          {
            echo ""
            echo "# From Cursor transcript (harvest $ts_iso)"
            echo ""
            echo "1. $(echo "$text" | sed 's/\$defer//g; s/\$pending//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
            echo ""
          } >> "$handoff"
        fi
        if [[ "$has_idea" == "true" ]]; then
          local f="$out_sub/seed_cursor_${ts_iso}_${session_id}_${line_num}.md"
          {
            echo "---"
            echo "saved_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
            echo "source: cursor_agent_transcript"
            echo "project: $project_path"
            echo "project_folder: $(basename "$proj_dir")"
            echo "session_id: $session_id"
            echo "---"
            echo ""
            echo "$text"
          } > "$f"
        fi
        (( count++ )) || true
      done < "$jsonl"
      echo "$jsonl:$line_num" >> "${offset_file}.tmp"
    done
  done
  [[ -f "${offset_file}.tmp" ]] && mv "${offset_file}.tmp" "$offset_file"
  echo "Cursor: harvested $count idea(s)"
}

harvest_claude
harvest_codex
(set +e; harvest_cursor) || true
echo "Idea seeds and \$defer/\$pending written to project docs/research/ (or ${FALLBACK_OUTPUT:-~/.claude/idea-seeds} when project unknown)"
