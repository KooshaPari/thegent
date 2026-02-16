#!/usr/bin/env bash
# Service Role Detection Hook
# CRITICAL: Prevents service role keys in application code

set -euo pipefail
HOOK_NAME="CHECK-SERVICE-ROLE"
# shellcheck source=./lib/common.sh
source "${BASH_SOURCE[0]%/*}/lib/common.sh"
hook_init

# Initialize variables if not set by hook_init/dispatcher
TOOL_NAME="${TOOL_NAME:-Edit}"
TOOL_CONTENT="${TOOL_CONTENT:-}"
TOOL_NEW_STRING="${TOOL_NEW_STRING:-}"

# --- Fast-path exits (zero spawns) ---

# Skip if no file path
[[ -z "$FILE_PATH" ]] && exit 0

# Only care about src/ and app/ paths — skip everything else immediately
case "$FILE_PATH" in
  */src/*|*/app/*) ;;
  *) exit 0 ;;
esac

# Skip migrations and scripts
case "$FILE_PATH" in
  */supabase/migrations/*|*/scripts/*) exit 0 ;;
esac

# Extract content using common.sh helper (single jq call for both Write/Edit)
hook_extract_content

# Get the relevant content based on tool type
CONTENT=""
if [[ "$TOOL_NAME" == "Write" ]]; then
  CONTENT="$TOOL_CONTENT"
elif [[ "$TOOL_NAME" == "Edit" ]]; then
  CONTENT="$TOOL_NEW_STRING"
fi

[[ -z "$CONTENT" ]] && exit 0

# Check for service role using bash lowercase matching (no grep spawn)
local_lower="${CONTENT,,}"
if [[ "$local_lower" == *supabase_service_key* || "$local_lower" == *service_role* || "$local_lower" == *servicerole* ]]; then
    echo "CRITICAL SECURITY VIOLATION" >&2
    echo "   Service role key detected in: $FILE_PATH" >&2
    echo "" >&2
    echo "   Service role keys must NEVER be in application code!" >&2
    echo "" >&2
    echo "Use WorkOS AuthKit JWTs instead:" >&2
    echo "   - All database queries use user JWT context" >&2
    echo "   - RLS policies validate auth.jwt()" >&2
    echo "   - Service role ONLY for migrations/CLI" >&2
    exit 1
fi

exit 0
