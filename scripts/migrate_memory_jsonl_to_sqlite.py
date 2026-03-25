#!/usr/bin/env python3
"""Migrate Civilization Framework memories from JSONL to SQLite backend.

Usage:
    python3 scripts/migrate_memory_jsonl_to_sqlite.py [--dry-run] [--source-dir DIR] [--db-path PATH]

Options:
    --dry-run       Preview what would be migrated without writing
    --source-dir    Base directory containing agent subdirs (default: ~/.claude/civilization/agents)
    --db-path       Target SQLite database path (default: ~/.claude/civilization/memories.db)
"""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path


def find_jsonl_files(source_dir: Path) -> list:
    """Find all memory.jsonl files under source_dir/*/memory.jsonl."""
    return sorted(source_dir.glob("*/memory.jsonl"))


def read_jsonl_memories(jsonl_path: Path) -> list:
    """Read all memory records from a JSONL file. Skip malformed lines."""
    memories = []
    with open(jsonl_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                memories.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(
                    f"  WARNING: Skipping malformed line {line_num} in {jsonl_path}: {e}",
                    file=sys.stderr,
                )
    return memories


def init_sqlite_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with the memory schema.

    Uses the same schema as SQLiteMemoryStorage in civilization_memory_storage.py.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            timestamp REAL NOT NULL,
            content TEXT NOT NULL,
            context TEXT,
            importance REAL,
            verified BOOLEAN
        );
        CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON memories(agent_id, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_agent_type ON memories(agent_id, memory_type);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp DESC);
    """)
    conn.commit()
    return conn


def migrate_file(jsonl_path: Path, conn: sqlite3.Connection, dry_run: bool = False) -> dict:
    """Migrate one JSONL file to SQLite. Returns stats dict."""
    memories = read_jsonl_memories(jsonl_path)
    agent_id = jsonl_path.parent.name  # directory name is agent_id
    stats = {
        "file": str(jsonl_path),
        "total": len(memories),
        "migrated": 0,
        "skipped": 0,
        "errors": 0,
    }

    for mem in memories:
        memory_id = mem.get("memory_id") or mem.get("id")
        if not memory_id:
            stats["skipped"] += 1
            continue

        if dry_run:
            stats["migrated"] += 1
            continue

        try:
            content = mem.get("content", {})
            conn.execute(
                "INSERT OR IGNORE INTO memories "
                "(id, agent_id, memory_type, timestamp, content, importance, verified, context) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    memory_id,
                    mem.get("agent_id", agent_id),
                    str(mem.get("memory_type", "unknown")),
                    mem.get("timestamp", time.time()),
                    json.dumps(content) if isinstance(content, dict) else str(content),
                    float(mem.get("importance", 0.5)),
                    int(mem.get("verified", False)),
                    json.dumps(mem.get("context", {})),
                ),
            )
            stats["migrated"] += 1
        except Exception as e:
            stats["errors"] += 1
            print(
                f"  ERROR migrating memory {memory_id}: {e}",
                file=sys.stderr,
            )

    if not dry_run:
        conn.commit()
    return stats


def main():
    parser = argparse.ArgumentParser(description="Migrate JSONL memories to SQLite")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path.home() / ".claude/civilization/agents",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.home() / ".claude/civilization/memories.db",
    )
    args = parser.parse_args()

    print(f"Source: {args.source_dir}")
    print(f"Target: {args.db_path}")
    print(f"Dry run: {args.dry_run}")
    print()

    if not args.source_dir.exists():
        print(f"Source directory does not exist: {args.source_dir}")
        print("Nothing to migrate.")
        sys.exit(0)

    jsonl_files = find_jsonl_files(args.source_dir)
    if not jsonl_files:
        print("No memory.jsonl files found. Nothing to migrate.")
        sys.exit(0)

    print(f"Found {len(jsonl_files)} JSONL file(s) to migrate:")

    conn = None if args.dry_run else init_sqlite_db(args.db_path)

    total_migrated = 0
    total_skipped = 0
    total_errors = 0

    for jsonl_path in jsonl_files:
        print(f"\n  Migrating: {jsonl_path}")
        stats = migrate_file(jsonl_path, conn, dry_run=args.dry_run)
        print(
            f"    Records: {stats['total']} total, {stats['migrated']} migrated, "
            f"{stats['skipped']} skipped, {stats['errors']} errors"
        )
        total_migrated += stats["migrated"]
        total_skipped += stats["skipped"]
        total_errors += stats["errors"]

    if conn:
        conn.close()

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Migration complete:")
    print(f"  Total migrated: {total_migrated}")
    print(f"  Total skipped:  {total_skipped}")
    print(f"  Total errors:   {total_errors}")

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
