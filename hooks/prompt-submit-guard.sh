#!/bin/zsh
# prompt-submit-guard.sh — UserPromptSubmit hook
# Detects antipattern phrases in user prompts and prints advisory QA reminders.
# Blocks (exit 1) for $defer/$pending and $block; advisory (exit 0) for antipatterns and $idea.
# OPTIMIZED: No common.sh sourcing. Pure bash builtins. Target: <50ms.
set -euo pipefail

# Stderr message on unexpected failure (set -e)
trap 'echo "PROMPT-SUBMIT-GUARD FAIL: unexpected error at line $LINENO" >&2' ERR

# --- Fast inline input parsing (no jq, no common.sh) ---
if [[ -n "${_HOOK_DISPATCHED:-}" ]]; then
  # Dispatcher already set PROMPT_TEXT or we extract from env
  PROMPT_TEXT="${PROMPT_TEXT:-}"
  PROJECT_DIR="${PROJECT_DIR:-}"
else
  # Read stdin, extract prompt text and project dir
  INPUT="$(cat)"
  PROMPT_TEXT=$(jq -r '.tool_input.prompt // .tool_input.content // .content // empty' <<< "${INPUT:-{\}}" 2>/dev/null) || PROMPT_TEXT=""
  PROJECT_DIR=$(jq -r '.cwd // .project_dir // .tool_input.cwd // empty' <<< "${INPUT:-{\}}" 2>/dev/null) || PROJECT_DIR=""
fi

[[ -z "$PROMPT_TEXT" ]] && exit 0

# Resolve PROJECT_DIR for $idea save (git root or cwd)
[[ -z "$PROJECT_DIR" || "$PROJECT_DIR" == "/" ]] && PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Convert to lowercase for case-insensitive matching (bash builtin, no spawns)
PROMPT_LOWER="${PROMPT_TEXT,,}"

# ---------- $block: block prompt, add to escalation queue (exit 1) ----------
# Precedence: $block wins over $defer/$pending
if [[ "${PENDING_QUEUE_ENABLED:-1}" == "1" ]] && [[ "${BLOCK_ESCALATION_ENABLED:-1}" == "1" ]]; then
  if [[ "$PROMPT_TEXT" == *'$block'* ]]; then
    RUN_ID="block-$(date +%s)"
    REASON="${PROMPT_TEXT//\$block/}"
    REASON="${REASON//$'\n'/ }"
    REASON="${REASON//\"/\'}"
    REASON="${REASON:0:300}"
    if command -v thegent &>/dev/null; then
      thegent govern escalate add "$RUN_ID" "$REASON" --sla-minutes=60 2>/dev/null || true
    fi
    echo ""
    echo "--- Blocked (requires approval) ---"
    echo "Prompt added to escalation queue. Resolve with:"
    echo "  thegent govern escalate resolve $RUN_ID"
    echo "Then resubmit the prompt or ask 'find the next thing to do'."
    exit 1
  fi
fi

# ---------- $defer / $pending: queue for session stop (exit 1) ----------
if [[ "${PENDING_QUEUE_ENABLED:-1}" == "1" ]]; then
  if [[ "$PROMPT_TEXT" == *'$defer'* ]] || [[ "$PROMPT_TEXT" == *'$pending'* ]]; then
    CLEANED="${PROMPT_TEXT//\$defer/}"
    CLEANED="${CLEANED//\$pending/}"
    CLEANED="$(echo "$CLEANED" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$CLEANED" ]] && { echo "Empty prompt; not queued."; exit 1; }
    QUEUE_DIR="$HOME/.claude"
    [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]] && QUEUE_DIR="${PROJECT_DIR}/.claude"
    mkdir -p "$QUEUE_DIR"
    QUEUE_FILE="$QUEUE_DIR/pending-queue.jsonl"
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)
    echo "{\"ts\":\"$TS\",\"prompt\":$(echo "$CLEANED" | jq -Rs .),\"project\":\"$PROJECT_DIR\"}" >> "$QUEUE_FILE"
    COUNT=$(wc -l < "$QUEUE_FILE" 2>/dev/null | tr -d ' ')
    echo ""
    echo "--- Queued for session stop ---"
    echo "Queued. $COUNT pending. Processed when you stop the session."
    exit 1
  fi
fi

# ---------- Antipattern detection (all bash builtins, zero spawns) ----------
ANTIPATTERNS_FOUND=()

# Test-skipping patterns
for pattern in "skip tests" "skip the tests" "don't write tests" "no tests" "dont write tests" "without tests"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("test-skipping: \"$pattern\"")
    break
  fi
done

# Lint-skipping patterns
for pattern in "disable lint" "ignore lint" "skip lint" "no linting"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("lint-skipping: \"$pattern\"")
    break
  fi
done

# Quality-skipping patterns
for pattern in "just make it work" "just get it working" "just get it done" "make it work somehow"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("quality-shortcut: \"$pattern\"")
    break
  fi
done

# Error-suppression patterns
for pattern in "ignore the errors" "ignore errors" "suppress the" "suppress errors" "hide the errors"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("error-suppression: \"$pattern\"")
    break
  fi
done

# Dangerous git patterns
for pattern in "--no-verify" "--force" "force push" "force-push" "--force-with-lease"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    ANTIPATTERNS_FOUND+=("dangerous-git: \"$pattern\"")
    break
  fi
done

# ---------- Print advisory if antipatterns detected ----------
if [[ ${#ANTIPATTERNS_FOUND[@]} -gt 0 ]]; then
  echo "QA Governance Reminder: Quality enforcement is active."
  echo "  Detected patterns:"
  for ap in "${ANTIPATTERNS_FOUND[@]}"; do
    echo "    - $ap"
  done
  echo "  Consider:"
  echo "    - Tests are required for all new code (TDD mandate)"
  echo "    - Suppressions require inline justification"
  echo "    - All linters must pass"
fi

# ---------- Check for pending QA findings ----------
QA_FINDINGS="$HOME/.claude/.qa-findings-pending"
if [[ -f "$QA_FINDINGS" ]] && [[ -s "$QA_FINDINGS" ]]; then
  # Count lines using bash builtins (eliminates wc + tr spawns)
  FINDING_COUNT=0
  while IFS= read -r _; do
    (( FINDING_COUNT++ ))
  done < "$QA_FINDINGS"
  echo "QA Reminder: $FINDING_COUNT unresolved finding(s) from previous quality checks."
  echo "  Review: $QA_FINDINGS"
fi

# ---------- Workflow triggers: inject agent instructions ----------
# Idea/task prompts → research dump, specs, work stream
IDEA_PATTERNS=("idea" "research" "explore" "figure out" "add feature" "build" "implement" "design" "create" "task" "feature" "investigate")
for pattern in "${IDEA_PATTERNS[@]}"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    echo ""
    echo "--- Agent workflow (idea/task detected) ---"
    echo "1. Dump research to docs/research/ (or docs/guides/ as appropriate)"
    echo "2. Create or update specs in docs/docset/ (formal specification docset)"
    echo "3. Add work items to unified work stream (docs/reference/, contracts/, or project tracker)"
    echo "4. This enables: spam ideas here → open new chat → ask 'find the next thing to do'"
    break
  fi
done

# ---------- Continuous work instruction: Always work on backlog when idle ----------
# CRITICAL: Inject instruction to keep working and avoid chat termination
echo ""
echo "--- Continuous Work Instruction (Always Active) ---"
echo "CRITICAL: When idle or between tasks, ALWAYS:"
echo "1. Check backlog: thegent plan do-next --limit 5"
echo "2. Work on items directly (don't just delegate)"
echo "3. Use 'thegent plan wait-next' to block until work ready (keeps session alive)"
echo "4. Use 'thegent plan loop' for continuous autonomous work"
echo "5. NEVER terminate chat - always check for next work item"
echo "6. If no work available, wait with: thegent plan wait-next --timeout 0"
echo "7. Continue working until explicitly told to stop"

# ---------- Session topic capture for SessionComplete notifications ----------
# Keep a concise moving topic per chat/session from latest prompt text.
TOPIC_DIR="$PROJECT_DIR/.claude"
mkdir -p "$TOPIC_DIR" 2>/dev/null || true
TOPIC_FILE="$TOPIC_DIR/notify-topic.txt"
TOPIC_TEXT="$(echo "$PROMPT_TEXT" | tr '\n\t' '  ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//')"
TOPIC_TEXT="$(echo "$TOPIC_TEXT" | awk '{n=0; out=\"\"; for(i=1;i<=NF&&n<8;i++){out=out (n?\" \":\"\") $i; n++} print out}')"
[[ -z "$TOPIC_TEXT" ]] && TOPIC_TEXT="workstream updated"
echo "$TOPIC_TEXT" > "$TOPIC_FILE" 2>/dev/null || true

# Quality green → run task quality-a-r
QUALITY_PATTERNS=("get task quality green" "quality green" "make quality pass" "fix quality" "task quality" "quality pass" "get quality green")
for pattern in "${QUALITY_PATTERNS[@]}"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    echo ""
    echo "--- Agent workflow (quality green) ---"
    echo "Run: task quality-a-r"
    echo "  (Full quality pipeline; on fail pipes to agent and reloads until green)"
    echo "  Or: task quality:dag (DAG only, no agent loop)"
    break
  fi
done

# Next thing to do → read from work stream
NEXT_PATTERNS=("find the next thing to do" "next thing to do" "what next" "pick next" "next task" "next item" "next work item")
for pattern in "${NEXT_PATTERNS[@]}"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    echo ""
    echo "--- Agent workflow (next item) ---"
    echo "1. Read from unified work stream: docs/reference/, docs/docset/, contracts/, docs/plans/"
    echo "2. Check docs/reference/PLAN_STATUS.md, docs/reference/FR_TRACKER.md, or project tracker"
    echo "3. Pick the highest-priority in-progress or pending item"
    echo "4. Execute that item"
    break
  fi
done

# Gardening → converge to empty backlog + complete green
GARDEN_PATTERNS=("garden" "converge" "empty backlog" "complete green" "check gov traceability" "check plan items" "get project converging")
for pattern in "${GARDEN_PATTERNS[@]}"; do
  if [[ "$PROMPT_LOWER" == *"$pattern"* ]]; then
    echo ""
    echo "--- Agent workflow (gardening) ---"
    echo "1. thegent govern go health (8 dimensions)"
    echo "2. task quality; FR traceability; spec-verifier"
    echo "3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/"
    echo "4. thegent govern escalate list --past-sla"
    echo "5. Dispatch: thegent_run/thegent_bg for each failing dimension or pending item"
    echo "6. task quality-a-r until green"
    echo "7. thegent govern go cycle (AgilePlus)"
    echo "8. Repeat until backlog empty and all green"
    break
  fi
done

# ---------- $idea flag: save exact prompt to research seeds ----------
if [[ "$PROMPT_TEXT" == *'$idea'* ]]; then
  SEEDS_DIR="${PROJECT_DIR}/docs/research/idea-seeds"
  mkdir -p "$SEEDS_DIR"
  TS=$(date -u +%Y%m%dT%H%M%SZ 2>/dev/null || date +%Y%m%dT%H%M%SZ)
  SEED_FILE="$SEEDS_DIR/seed_${TS}.md"
  {
    echo "---"
    echo "saved_at: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ)"
    echo "source: UserPromptSubmit"
    echo "---"
    echo ""
    echo "$PROMPT_TEXT"
  } > "$SEED_FILE"
  echo ""
  echo "--- Idea seed saved ---"
  echo "Saved to: $SEED_FILE"
fi

exit 0
