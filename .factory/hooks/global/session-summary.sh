#!/usr/bin/env bash
# Global hook: Session summary on exit

input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // "unknown"')
transcript_path=$(echo "$input" | jq -r '.transcript_path // ""')

if [ -f "$transcript_path" ]; then
  turns=$(grep -c '"role":"user"' "$transcript_path" 2>/dev/null || echo "0")
  echo "✅ Session complete: $turns interactions"
else
  echo "✅ Session complete: $session_id"
fi

exit 0
