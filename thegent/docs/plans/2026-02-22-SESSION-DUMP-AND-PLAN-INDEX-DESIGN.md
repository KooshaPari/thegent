---
title: Session Dump Automation + Plan Index
date: 2026-02-22
status: SPEC
owner: thegent
tags: [session, dump, index, automation, harness-agnostic]
---

# Session Dump Automation + Plan Index

## Problem

The current `session-end-write-dump.sh` hook creates an **empty template stub** — it does not extract real session content. Plans accumulate in `docs/plans/` with no machine-readable index. Cross-session continuity requires manually reading dozens of files.

## Goal

1. **Real content dumps** — on session end, extract actual conversation content (decisions, fixes, research findings) into `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md`
2. **Plan index** — machine-readable `docs/plans/INDEX.json` kept current; queryable via CLI
3. **Harness-agnostic** — works for Claude Code, Codex, Cursor, and any future harness
4. **Tested** — full test coverage per thegent standards

---

## Current State

### What exists
- `hooks/session-end-write-dump.sh` — creates empty template, no content extraction
- `src/thegent/prompts.py` — `list_sessions()`, `dump_cursor_session()` — functional but not wired to auto-run
- `src/thegent/research/always_dumps.py` — `ConversationDumpWriter` — writes JSON blobs, not human-readable MD
- `docs/plans/00-MASTER-INDEX.md` — manual, not machine-generated

### Gap
The hook doesn't call `thegent prompts dump`. The dump command exists but requires manual invocation. No JSON index of plans exists.

---

## Design

### 1. Session Dump Pipeline

#### Flow
```
SessionEnd hook fires
  → detect harness (claude / codex / cursor / generic)
  → locate session transcript (jsonl / sqlite / files)
  → extract: messages, tool uses, decisions, fixes, research
  → LLM summarize (haiku, ≤500 tokens) OR heuristic extraction
  → append to docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md
  → emit thegent_memory_add for key decisions
  → update docs/plans/INDEX.json
```

#### Harness detection + transcript location

| Harness | Transcript location | Format |
|---------|-------------------|--------|
| Claude Code | `~/.claude/projects/<proj>/*.jsonl` | JSONL (messages) |
| Codex | `~/.codex/history.jsonl` | JSONL |
| Cursor | `~/.cursor-agent/transcripts/` | JSON files |
| Generic | stdin JSON | Structured |

#### Extraction rules (heuristic, no LLM needed for most cases)
- **Decisions**: lines/messages containing "changed", "fixed", "added", "removed", "renamed" near code patterns
- **Files touched**: scan `tool_use` records for `file_path` fields
- **Errors resolved**: scan for `error`/`pyright`/`0 errors` patterns
- **Research findings**: scan for URL references, package names, version numbers

#### LLM summarization (opt-in, uses haiku)
```bash
THGENT_DUMP_LLM=1 thegent prompts dump <session_id>
```

#### Output format
```markdown
# Conversation Dump YYYY-MM-DD — <auto-title from first user message>

## Session Goal
<extracted from first user message>

## Files Modified
- `src/thegent/foo.py` (+42 lines)
- `src/thegent/bar.py` (-15 lines)

## Decisions Made
- Fixed `fast_file_watcher.py`: mandatory imports, removed fallbacks
- Renamed `_guardrails_from_env` → `guardrails_from_env` (exported)

## Research Findings
- (URLs, packages, version bumps mentioned)

## Open Questions / Residual
- (unresolved items from session)

## Next Steps
- (last user message or extracted todo items)
```

---

### 2. Plan Index

#### `docs/plans/INDEX.json`

```json
{
  "generated_at": "2026-02-22T10:00:00Z",
  "plans": [
    {
      "id": "WL-128",
      "file": "docs/plans/WL-128-PYTHON-TOOLCHAIN-DEDUP-SLICE.md",
      "title": "Python Toolchain Dedup Slice",
      "status": "COMPLETED",
      "date": "2026-02-21",
      "tags": ["python", "toolchain"],
      "work_stream_ref": "WL-128"
    }
  ]
}
```

#### Auto-update triggers
- PostToolUse:Write when target is `docs/plans/*.md`
- Daily via cron/scheduler
- `thegent plan index rebuild` — manual full rebuild

#### CLI
```bash
thegent plan index list --status OPEN
thegent plan index list --tag python
thegent plan index show WL-128
thegent plan index search "monolith split"
```

---

### 3. Hook Fix: `session-end-write-dump.sh`

Replace stub with real invocation:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Get current session ID from env (set by harness hook dispatcher)
SESSION_ID="${THGENT_SESSION_ID:-}"
HARNESS="${THGENT_HARNESS:-claude}"

if [ -n "$SESSION_ID" ]; then
    thegent prompts dump "$SESSION_ID" \
        --harness "$HARNESS" \
        --output "docs/research/CONVERSATION_DUMP_$(date +%Y-%m-%d).md" \
        --append
else
    # Fallback: create dated stub only if no session ID
    thegent prompts dump --latest \
        --output "docs/research/CONVERSATION_DUMP_$(date +%Y-%m-%d).md" \
        --append
fi

# Always rebuild plan index on session end
thegent plan index rebuild --quiet
```

---

## Work Items

| ID | Description | Effort |
|----|-------------|--------|
| WL-NEW-20 | Fix session-end-write-dump.sh to call real dump command | S |
| WL-NEW-21 | `thegent prompts dump` — harness-agnostic extraction (Claude/Codex/Cursor) | M |
| WL-NEW-22 | Heuristic content extractor (decisions/files/findings without LLM) | M |
| WL-NEW-23 | `thegent plan index rebuild` + INDEX.json generation | S |
| WL-NEW-24 | PostToolUse:Write hook to update INDEX.json on plan writes | S |
| WL-NEW-25 | `thegent plan index search` CLI | S |
| WL-NEW-26 | Tests: dump extraction, index generation, hook integration | M |

---

## Backmatter

**Decision delta:** Fix existing stub hook; wire existing `prompts.py` extraction to run automatically.

**Validation commands:**
```bash
thegent prompts dump --latest
cat docs/research/CONVERSATION_DUMP_$(date +%Y-%m-%d).md
thegent plan index list
python -m pytest tests/test_session_dump.py tests/test_plan_index.py -v
```

**Residual risks:**
- Session ID may not be available in all harness contexts — need graceful fallback to "latest session"
- JSONL format differs between harness versions — need version-aware parser

**Follow-up review:** 2026-03-22
