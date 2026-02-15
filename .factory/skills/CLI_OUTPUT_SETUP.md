# CLI Output Setup - Proper Configuration

**Date:** February 6, 2026
**Status:** ✅ All wrapper scripts updated with proper output flags

---

## Summary

All 4 agent CLI wrappers now support proper output capture and streaming:

| Agent | CLI Flag | Output Format | Implementation |
|-------|----------|---------------|-----------------|
| **Copilot** | `--stream on` | stdout stream | `--allow-all-tools --stream on` |
| **Codex** | `--json` or `-o FILE` | JSONL or file | `--json` for stream, `-o FILE` for structured |
| **Gemini** | `--output-format` | text/json/stream-json | `--output-format stream-json` |
| **Cursor** | `--print` | stdout stream | `cursor agent --print` (implicit) |

---

## Per-Agent Configuration

### 1. Copilot Agent
**File:** `~/.factory/skills/copilot-agent/scripts/run_copilot.sh`

**Output Flags:**
```bash
--allow-all-tools    # Allow all tools without prompting
--stream on          # Stream output to stdout in real-time
```

**Usage:**
```bash
run_copilot.sh --prompt "task" --mode programmatic --cd ~/project
# Output: Streams to stdout, captured automatically
```

**Modes & Output:**
- **interactive:** Streams to stdout (real-time conversation)
- **programmatic:** Streams to stdout, exits on completion
- **autopilot:** Streams to stdout until task done

---

### 2. Codex Agent
**File:** `~/.factory/skills/codex-agent/scripts/run_codex.sh`

**Output Flags:**
```bash
--json                    # Output JSONL (JSON Lines) to stdout
-o/--output-last-message  # Write last message to file
```

**Usage:**
```bash
# Option 1: JSON stream output
run_codex.sh --prompt "task" --cd ~/project --json
# Output: JSONL lines to stdout (parseable)

# Option 2: File output (wrapper default)
run_codex.sh --prompt "task" --cd ~/project
# Output: Temp file created, content printed to stdout, file cleaned up
```

**Wrapper Behavior:**
- Default (no flag): Uses `-o FILE`, prints content to stdout, cleans up temp file
- With `--json`: Passes through to codex subagent with `--json` flag

---

### 3. Gemini Agent
**File:** `~/.factory/skills/gemini-agent/scripts/run_gemini.sh`

**Output Flags:**
```bash
--output-format text        # Human-readable text
--output-format json        # JSON format
--output-format stream-json # Streaming JSON (default in wrapper)
```

**Usage:**
```bash
run_gemini.sh --prompt "scan for vulnerabilities" --mode read-only --cd ~/project
# Output: Streaming JSON to stdout (--output-format stream-json hardcoded)
```

**Wrapper Implementation:**
- Automatically adds `--output-format stream-json` to all executions
- Streams output to stdout in real-time
- User can override if needed (not recommended)

---

### 4. Cursor Agent
**File:** `~/.factory/skills/cursor-agent/scripts/run_cursor.sh`

**Output Flags:**
```bash
--print   # Print agent output to stdout (implicit with agent mode)
```

**Usage:**
```bash
run_cursor.sh --prompt "design auth flow" --mode plan --cd ~/project
# Output: Agent output printed to stdout via --print flag
```

**Wrapper Implementation:**
- Always uses `cursor agent --print` for output capture
- Supports `--mode plan` and `--mode ask` for interactive modes
- Output streams to stdout

---

## Wrapper Script Updates

### Changes Made

#### Copilot Wrapper
```bash
# Added to execute_copilot() function:
if [[ "$MODE" == "programmatic" ]]; then
  cmd_array+=(--allow-all-tools --stream on)
fi
```

**Effect:** Programmatic mode now streams output to stdout instead of silently executing.

---

#### Codex Wrapper
```bash
# New logic to handle output:
if [[ "$OUTPUT_JSON" == "true" ]]; then
  # Pass through --json flag
  exec ~/.claude/skills/codex-subagent/scripts/run_codex_subagent.sh "$@" \
    --model "$MODEL" --json
else
  # Default: Use temp file, print to stdout, clean up
  TEMP_OUTPUT=$(mktemp)
  ~/.claude/skills/codex-subagent/scripts/run_codex_subagent.sh "$@" \
    --model "$MODEL" -o "$TEMP_OUTPUT"

  if [[ -f "$TEMP_OUTPUT" ]]; then
    cat "$TEMP_OUTPUT"
    rm -f "$TEMP_OUTPUT"
  fi
fi
```

**Effect:** Both JSON streaming and file-based output now capture to stdout.

---

#### Gemini Wrapper
```bash
# Added to command building:
CMD+=(--output-format stream-json)
```

**Effect:** All gemini executions now output streaming JSON to stdout.

---

#### Cursor Wrapper
```bash
# Simplified and clarified:
CMD=(cursor agent)
CMD+=(--print)  # Explicit --print flag for output capture
```

**Effect:** Clearer output handling with explicit --print flag.

---

## Testing Output Capture

### Quick Test Commands

**Copilot:**
```bash
~/.factory/skills/copilot-agent/scripts/run_copilot.sh \
  --prompt "say hello" --mode programmatic 2>&1 | head -20
# Expected: Copilot output appears in terminal
```

**Codex:**
```bash
~/.factory/skills/codex-agent/scripts/run_codex.sh \
  --prompt "analyze this code" --cd ~/project 2>&1 | head -20
# Expected: Codex analysis output appears in terminal
```

**Gemini:**
```bash
~/.factory/skills/gemini-agent/scripts/run_gemini.sh \
  --prompt "scan for issues" --mode workspace-write --cd ~/project 2>&1 | head -20
# Expected: Streaming JSON output appears in terminal
```

**Cursor:**
```bash
~/.factory/skills/cursor-agent/scripts/run_cursor.sh \
  --prompt "design system" --mode plan --cd ~/project 2>&1 | head -20
# Expected: Agent output appears in terminal
```

---

## Integration with Phase 3 Tasks

### How to Use in Bash Wrappers

```bash
# Capture output to variable
output=$(~/.factory/skills/copilot-agent/scripts/run_copilot.sh \
  --prompt "your task" --mode programmatic 2>&1)

# Log output
echo "$output" | tee /tmp/agent-output.log

# Process JSON (for Gemini/Codex --json mode)
echo "$output" | jq '.message' > /tmp/parsed-output.txt
```

### How to Use with Skill() Tool

```bash
# Skill tool invocation (if fixed for proper output)
Skill(skill: "copilot-agent", args: "--prompt 'task' --mode programmatic")
# Output: Streams to stdout automatically
```

---

## Troubleshooting

### Issue: No output appears
**Solution:** Check that flags are present in wrapper scripts
```bash
# Verify Copilot flags
grep -n "stream on" ~/.factory/skills/copilot-agent/scripts/run_copilot.sh

# Verify Gemini format
grep -n "output-format" ~/.factory/skills/gemini-agent/scripts/run_gemini.sh
```

### Issue: Output is truncated
**Solution:** Remove `head -N` limit when testing
```bash
# Full output:
run_copilot.sh --prompt "task" --mode programmatic 2>&1

# Don't pipe to head initially - capture to file:
run_copilot.sh --prompt "task" --mode programmatic 2>&1 | tee /tmp/full-output.txt
```

### Issue: JSON parsing errors
**Solution:** Use proper JSON tools
```bash
# For Gemini/Codex JSON output:
output=$(run_gemini.sh --prompt "task" 2>&1)
echo "$output" | jq -s '.' # Parse as JSON array

# For Codex JSONL format:
echo "$output" | jq -s '.' # Parses multiple JSON lines
```

---

## Architecture

### Output Flow

```
User Request
    ↓
Wrapper Script (run_*.sh)
    ↓
CLI Tool (copilot/codex/gemini/cursor)
    ├─ Executes task
    └─ Outputs to stdout
         ↓
    Wrapper Captures
    ├─ Streams to terminal (live feedback)
    └─ Can be piped/redirected
         ↓
    User/Calling Process
    ├─ Sees real-time output
    ├─ Can parse/process output
    └─ Gets proper exit codes
```

### Output Modes

| Mode | Copilot | Codex | Gemini | Cursor |
|------|---------|-------|--------|--------|
| **Stream** | `--stream on` | `--json` | `--output-format stream-json` | `--print` |
| **Real-time** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Parseable** | Plain text | JSON | JSON | Plain text |
| **File output** | Via redirection | `-o FILE` | Via redirection | Via redirection |

---

## Summary of Changes

✅ **Copilot:** Added `--stream on --allow-all-tools` for programmatic mode
✅ **Codex:** Added `--json` option and file-to-stdout fallback
✅ **Gemini:** Hardcoded `--output-format stream-json` for consistent JSON output
✅ **Cursor:** Explicit `--print` flag for agent output capture

**Result:** All agents now output to stdout properly, enabling:
- Real-time feedback during execution
- Proper output capture for piping/redirection
- JSON parsing for structured data (Codex/Gemini)
- Integration with Phase 3 Task workflows

---

**Last Updated:** February 6, 2026
**Status:** Production Ready ✅
