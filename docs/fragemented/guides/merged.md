# Merged Fragmented Markdown

## Source: guides/PHASE_6_MEMORY_MIGRATION_GUIDE.md

# Phase 6: JSONL to SQLite Memory Migration Guide

**Applies to:** Civilization Framework deployments using Phase 5B JSONL memory storage
**Target:** Phase 6 SQLite memory backend
**Last updated:** 2026-02-19

---

## 1. Overview

Phase 6 introduces a SQLite-backed memory storage backend that replaces the original JSONL file-based storage from Phase 5B. The migration tool converts existing JSONL memory files into a single indexed SQLite database, providing:

- **2.4x faster queries** through indexed lookups instead of full file scans
- **Full-text keyword search** across memory content
- **Typed memory relationships** (causal, similarity, contradiction edges)
- **SQL-native aggregation** for analytics and dashboard integration
- **Reduced disk I/O** from single-file database vs per-agent JSONL files

The migration is non-destructive. Original JSONL files are never modified or deleted by the migration tool.

---

## 2. Prerequisites

- Python 3.9 or later (for `pathlib`, `dataclasses`, and `sqlite3` stdlib modules)
- Existing JSONL memory files in the agent data directory
- Write access to the target SQLite database path
- Sufficient disk space (~1.2x the total JSONL file size, to hold both formats during transition)

---

## 3. Before You Start

### Back Up Your Data

The migration tool does not modify JSONL files, but creating an explicit backup is still recommended:

```bash
# Back up the entire agent data directory
cp -r ~/.claude/civilization/agents ~/.claude/civilization/agents.backup.$(date +%Y%m%d)
```

### Check Existing Data

Verify that JSONL memory files exist and contain valid data:

```bash
# List all agent memory files
find ~/.claude/civilization/agents -name "memory.jsonl" -type f

# Check a sample file for valid JSONL
head -3 ~/.claude/civilization/agents/<agent-id>/memory.jsonl
```

Each line in a valid JSONL file should be a complete JSON object containing at minimum `memory_id` (or `id`), `agent_id`, `memory_type`, `timestamp`, and `content`.

### Check Disk Space

```bash
# Total size of JSONL files
du -sh ~/.claude/civilization/agents/*/memory.jsonl 2>/dev/null | tail -1

# Available disk space
df -h ~/.claude/civilization/
```

The SQLite database will be approximately the same size as the combined JSONL files, plus index overhead (~20%).

---

## 4. Migration Steps

### Step A: Dry Run (Preview)

Run the migration tool in dry-run mode to preview what will be migrated without writing anything:

```bash
python3 scripts/migrate_memory_jsonl_to_sqlite.py --dry-run
```

Expected output:

```
Source: /Users/<you>/.claude/civilization/agents
Target: /Users/<you>/.claude/civilization/memories.db
Dry run: True

Found 3 JSONL file(s) to migrate:

  Migrating: /Users/<you>/.claude/civilization/agents/agent-alpha/memory.jsonl
    Records: 42 total, 42 migrated, 0 skipped, 0 errors

  Migrating: /Users/<you>/.claude/civilization/agents/agent-beta/memory.jsonl
    Records: 18 total, 18 migrated, 0 skipped, 0 errors

  Migrating: /Users/<you>/.claude/civilization/agents/agent-gamma/memory.jsonl
    Records: 7 total, 7 migrated, 0 skipped, 0 errors

DRY RUN Migration complete:
  Total migrated: 67
  Total skipped:  0
  Total errors:   0
```

**Review the output.** If any records are skipped (missing `memory_id`/`id` field) or errors occur (malformed data), investigate those JSONL files before proceeding.

### Step B: Run Actual Migration

```bash
python3 scripts/migrate_memory_jsonl_to_sqlite.py
```

The tool will:
1. Scan `~/.claude/civilization/agents/*/memory.jsonl` for JSONL files
2. Create the SQLite database at `~/.claude/civilization/memories.db`
3. Initialize the schema (memories table, indexes, relationships table)
4. Insert each memory record using `INSERT OR IGNORE` (duplicates are skipped safely)
5. Commit per file and report per-file statistics

### Step C: Verify Migration

---

