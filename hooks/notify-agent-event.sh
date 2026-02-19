#!/usr/bin/env bash
# notify-agent-event.sh
# Best-effort desktop + voice notifications for hook events.
# Never hard-fails caller.
set -uo pipefail

EVENT="event"
TITLE="thegent"
MESSAGE=""
SEVERITY="info"
HARNESS="${THGENT_HARNESS:-}"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --event) EVENT="${2:-event}"; shift 2 ;;
    --title) TITLE="${2:-thegent}"; shift 2 ;;
    --message) MESSAGE="${2:-}"; shift 2 ;;
    --severity) SEVERITY="${2:-info}"; shift 2 ;;
    --harness) HARNESS="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ "${THGENT_NOTIFY_ENABLE:-1}" == "0" ]]; then
  exit 0
fi

_now_epoch() { date +%s 2>/dev/null || echo 0; }

_detect_harness() {
  if [[ -n "$HARNESS" ]]; then
    echo "$HARNESS"
    return
  fi
  local pid="${PPID:-}"
  local i=0
  while [[ -n "$pid" && "$pid" != "0" && $i -lt 10 ]]; do
    local cmd
    cmd="$(/bin/ps -o command= -p "$pid" 2>/dev/null | tr '[:upper:]' '[:lower:]')"
    if [[ "$cmd" == *"cursor"* ]]; then echo "cursor"; return; fi
    if [[ "$cmd" == *"codex"* || "$cmd" == *" dex "* || "$cmd" == *"/dex"* ]]; then echo "codex"; return; fi
    if [[ "$cmd" == *"claude"* || "$cmd" == *"clode"* ]]; then echo "claude"; return; fi
    if [[ "$cmd" == *"droid"* || "$cmd" == *"roid"* ]]; then echo "droid"; return; fi
    pid="$(/bin/ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')"
    ((i++))
  done
  echo "thegent"
}

HARNESS="$(_detect_harness)"
SUBTITLE="[$HARNESS] $EVENT/$SEVERITY"
BODY="$MESSAGE"
[[ -z "$BODY" ]] && BODY="$EVENT"

_agent_label() {
  case "${1:-thegent}" in
    codex|dex) echo "Codex" ;;
    claude|clode) echo "Claude" ;;
    droid|roid) echo "Droid" ;;
    cursor) echo "Cursor" ;;
    *) echo "Thegent" ;;
  esac
}

_state_label() {
  case "${1:-event}" in
    sessionend) echo "Session Complete" ;;
    taskcompleted) echo "Task Complete" ;;
    teammateidle) echo "Teammate Idle" ;;
    stop)
      if [[ "${2:-info}" == "error" || "${2:-info}" == "critical" ]]; then
        echo "Stop Issues"
      else
        echo "Stop Complete"
      fi
      ;;
    *) echo "Update" ;;
  esac
}

_normalize_ws() {
  tr '\n\t' '  ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//'
}

_truncate_words() {
  local text="$1"
  local maxw="$2"
  awk -v maxw="$maxw" '{
    n=0; out="";
    for (i=1; i<=NF && n<maxw; i++) { out = out (n? " ":"") $i; n++ }
    print out
  }' <<< "$text"
}

_chat_label_for_session() {
  local sid="${SESSION_ID:-}"
  local state_dir="$PROJECT_DIR/.claude"
  local map_file="$state_dir/notify-chat-map.tsv"
  local seq_file="$state_dir/notify-chat-seq"
  mkdir -p "$state_dir" 2>/dev/null || true

  if [[ -z "$sid" ]]; then
    echo "Chat 0"
    return
  fi

  if [[ -f "$map_file" ]]; then
    local existing
    existing="$(awk -F'\t' -v sid="$sid" '$1==sid{print $2; exit}' "$map_file" 2>/dev/null || true)"
    if [[ -n "$existing" ]]; then
      echo "$existing"
      return
    fi
  fi

  local seq=0
  if [[ -f "$seq_file" ]]; then
    seq="$(cat "$seq_file" 2>/dev/null || echo 0)"
  fi
  if ! [[ "$seq" =~ ^[0-9]+$ ]]; then
    seq=0
  fi
  seq=$((seq + 1))
  local label="Chat $seq"
  printf '%s' "$seq" > "$seq_file" 2>/dev/null || true
  printf '%s\t%s\n' "$sid" "$label" >> "$map_file" 2>/dev/null || true
  echo "$label"
}

_session_topic() {
  local topic_file="$PROJECT_DIR/.claude/notify-topic.txt"
  if [[ -f "$topic_file" ]]; then
    cat "$topic_file" 2>/dev/null | _normalize_ws
    return
  fi
  echo "workstream updated"
}

_session_message_contract() {
  local label="$(_chat_label_for_session)"
  local topic="$(_session_topic)"
  # Programmatic guardrail for ~5s speech:
  # keep topic concise (<=8 words), then full line stays short enough.
  topic="$(_truncate_words "$topic" 8)"
  topic="$(printf '%s' "$topic" | _normalize_ws)"
  [[ -z "$topic" ]] && topic="workstream updated"
  printf 'Session Complete - %s - %s' "$label" "$topic"
}

_derive_noti() {
  local event="$1"
  local severity="$2"
  local body="$3"
  local normalized=""
  if [[ "$event" == "sessionend" ]]; then
    printf '%s' "$body"
    return
  fi
  if [[ "$event" == "stop" ]]; then
    if [[ "$severity" == "error" || "$severity" == "critical" || "$body" == *"failures="* ]]; then
      echo "quality checks reported failures"
    else
      echo "quality checks passed"
    fi
    return
  fi
  normalized="$(printf '%s' "$body" | _normalize_ws)"
  _truncate_words "$normalized" 12
}

_speech_contract() {
  local state="$(_state_label "$EVENT" "$SEVERITY")"
  local agent="$(_agent_label "$HARNESS")"
  local noti="$(_derive_noti "$EVENT" "$SEVERITY" "$BODY")"
  noti="$(printf '%s' "$noti" | _normalize_ws)"
  [[ -z "$noti" ]] && noti="update ready"
  printf '%s - %s says - %s' "$state" "$agent" "$noti"
}

if [[ "$EVENT" == "sessionend" ]]; then
  BODY="$(_session_message_contract)"
  TITLE="Session Complete"
  SUBTITLE="[$HARNESS] session"
fi

if [[ "${THGENT_NOTIFY_DRY_RUN:-0}" == "1" ]]; then
  echo "notify(dry-run): event=$EVENT severity=$SEVERITY title=$TITLE subtitle=$SUBTITLE message=$BODY speak=\"$(_speech_contract)\""
  exit 0
fi

# Debounce duplicate notifications.
COOLDOWN="${THGENT_NOTIFY_COOLDOWN_SEC:-8}"
STATE_FILE="${TMPDIR:-/tmp}/thegent-notify.state"
KEY="$(printf '%s|%s|%s|%s|%s' "$EVENT" "$SEVERITY" "$TITLE" "$SUBTITLE" "$BODY" | cksum | awk '{print $1}')"
NOW="$(_now_epoch)"
if [[ -f "$STATE_FILE" ]]; then
  LAST_KEY="$(cut -d'|' -f1 "$STATE_FILE" 2>/dev/null || true)"
  LAST_TS="$(cut -d'|' -f2 "$STATE_FILE" 2>/dev/null || true)"
  if [[ "$KEY" == "$LAST_KEY" && -n "$LAST_TS" ]]; then
    AGE=$((NOW - LAST_TS))
    if (( AGE >= 0 && AGE < COOLDOWN )); then
      exit 0
    fi
  fi
fi
printf '%s|%s\n' "$KEY" "$NOW" > "$STATE_FILE" 2>/dev/null || true

_notify_macos() {
  command -v osascript >/dev/null 2>&1 || return 1
  # Some macOS builds reject `subtitle` in this form; fall back to title/message only.
  osascript - "$TITLE" "$SUBTITLE" "$BODY" <<'APPLESCRIPT' >/dev/null 2>&1 && return 0
on run argv
  set t to item 1 of argv
  set s to item 2 of argv
  set b to item 3 of argv
  display notification b with title t subtitle s
end run
APPLESCRIPT
  osascript - "$TITLE" "$BODY" <<'APPLESCRIPT' >/dev/null 2>&1 && return 0
on run argv
  set t to item 1 of argv
  set b to item 2 of argv
  display notification b with title t
end run
APPLESCRIPT
  return 1
}

_notify_linux() {
  if command -v notify-send >/dev/null 2>&1; then
    local urg="normal"
    [[ "$SEVERITY" == "error" || "$SEVERITY" == "critical" ]] && urg="critical"
    notify-send -u "$urg" "$TITLE" "$SUBTITLE - $BODY" >/dev/null 2>&1 || return 1
    return 0
  fi
  if command -v dunstify >/dev/null 2>&1; then
    local urg="normal"
    [[ "$SEVERITY" == "error" || "$SEVERITY" == "critical" ]] && urg="critical"
    dunstify -u "$urg" "$TITLE" "$SUBTITLE - $BODY" >/dev/null 2>&1 || return 1
    return 0
  fi
  return 1
}

_notify_windows() {
  command -v powershell.exe >/dev/null 2>&1 || return 1
  powershell.exe -NoProfile -Command \
    "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('$BODY','$TITLE')" \
    >/dev/null 2>&1 || return 1
}

_voice_macos() {
  command -v say >/dev/null 2>&1 || return 1
  local requested="${THGENT_NOTIFY_VOICE_NAME:-Siri}"
  local voice="$requested"
  if ! say -v "$voice" "" >/dev/null 2>&1; then
    # Try any Siri* voice first, then fallback to Samantha.
    local siri_voice
    siri_voice="$(say -v '?' 2>/dev/null | awk '/Siri/ {print $1; exit}')"
    if [[ -n "$siri_voice" ]]; then
      voice="$siri_voice"
    else
      voice="Samantha"
    fi
  fi
  local text="$(_speech_contract)"
  say -v "$voice" "$text" >/dev/null 2>&1 || return 1
}

_voice_linux() {
  local text="$(_speech_contract)"
  if command -v spd-say >/dev/null 2>&1; then
    spd-say "$text" >/dev/null 2>&1 || return 1
    return 0
  fi
  if command -v espeak >/dev/null 2>&1; then
    espeak "$text" >/dev/null 2>&1 || return 1
    return 0
  fi
  return 1
}

case "$(uname -s 2>/dev/null || echo unknown)" in
  Darwin) _notify_macos || true ;;
  Linux) _notify_linux || true ;;
  MINGW*|MSYS*|CYGWIN*) _notify_windows || true ;;
  *) true ;;
esac

# Voice behavior: default on for error/critical, opt-in for info.
VOICE_MODE="${THGENT_NOTIFY_VOICE_MODE:-errors}"
if [[ "$VOICE_MODE" == "all" || ( "$VOICE_MODE" == "errors" && ( "$SEVERITY" == "error" || "$SEVERITY" == "critical" ) ) ]]; then
  case "$(uname -s 2>/dev/null || echo unknown)" in
    Darwin) _voice_macos || true ;;
    Linux) _voice_linux || true ;;
    *) true ;;
  esac
fi

# Last-resort local hint.
if [[ -t 2 ]]; then
  printf '\a' 2>/dev/null || true
  echo "NOTIFY [$HARNESS/$EVENT/$SEVERITY] $TITLE - $BODY" >&2
fi

exit 0
