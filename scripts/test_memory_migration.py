#!/usr/bin/env python3
"""Tests for migrate_memory_jsonl_to_sqlite.py."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from migrate_memory_jsonl_to_sqlite import (
    find_jsonl_files,
    init_sqlite_db,
    migrate_file,
    read_jsonl_memories,
)


class TestFindJsonlFiles(unittest.TestCase):
    """Tests for find_jsonl_files."""

    def test_find_jsonl_files(self):
        """Create temp dirs with memory.jsonl and verify discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Create two agent dirs with memory.jsonl
            (base / "agent-alpha").mkdir()
            (base / "agent-alpha" / "memory.jsonl").write_text("")
            (base / "agent-beta").mkdir()
            (base / "agent-beta" / "memory.jsonl").write_text("")
            # Create a dir without memory.jsonl (should be ignored)
            (base / "agent-gamma").mkdir()
            (base / "agent-gamma" / "other.txt").write_text("")

            result = find_jsonl_files(base)
            names = sorted(p.parent.name for p in result)
            self.assertEqual(names, ["agent-alpha", "agent-beta"])

    def test_find_jsonl_files_empty_dir(self):
        """Empty source directory returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_jsonl_files(Path(tmpdir))
            self.assertEqual(result, [])


class TestReadJsonlMemories(unittest.TestCase):
    """Tests for read_jsonl_memories."""

    def test_read_jsonl_memories(self):
        """Write sample JSONL and verify all records are read."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "memory.jsonl"
            records = [
                {"memory_id": "m1", "content": {"text": "hello"}},
                {"memory_id": "m2", "content": {"text": "world"}},
            ]
            with open(jsonl_path, "w") as f:
                f.writelines(json.dumps(r) + "\n" for r in records)

            result = read_jsonl_memories(jsonl_path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["memory_id"], "m1")
            self.assertEqual(result[1]["memory_id"], "m2")

    def test_read_jsonl_skips_malformed(self):
        """Bad JSON on one line is skipped; rest still read."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "memory.jsonl"
            with open(jsonl_path, "w") as f:
                f.write(json.dumps({"memory_id": "m1"}) + "\n")
                f.write("NOT VALID JSON\n")
                f.write(json.dumps({"memory_id": "m3"}) + "\n")

            result = read_jsonl_memories(jsonl_path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["memory_id"], "m1")
            self.assertEqual(result[1]["memory_id"], "m3")

    def test_read_jsonl_skips_blank_lines(self):
        """Blank lines are silently skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = Path(tmpdir) / "memory.jsonl"
            with open(jsonl_path, "w") as f:
                f.write(json.dumps({"memory_id": "m1"}) + "\n")
                f.write("\n")
                f.write("   \n")
                f.write(json.dumps({"memory_id": "m2"}) + "\n")

            result = read_jsonl_memories(jsonl_path)
            self.assertEqual(len(result), 2)


class TestMigrateFile(unittest.TestCase):
    """Tests for migrate_file."""

    def _make_jsonl(self, tmpdir, agent_id, records):
        """Helper: write records to {tmpdir}/{agent_id}/memory.jsonl."""
        agent_dir = Path(tmpdir) / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = agent_dir / "memory.jsonl"
        with open(jsonl_path, "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in records)
        return jsonl_path

    def test_migrate_file_basic(self):
        """Write 3 memories to JSONL, migrate to in-memory SQLite, verify count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"memory_id": "m1", "agent_id": "a1", "memory_type": "learning", "timestamp": 1000.0, "content": {"text": "learned X"}, "importance": 0.8, "verified": False, "context": {}},
                {"memory_id": "m2", "agent_id": "a1", "memory_type": "decision", "timestamp": 1001.0, "content": {"text": "decided Y"}, "importance": 0.6, "verified": True, "context": {"key": "val"}},
                {"memory_id": "m3", "agent_id": "a1", "memory_type": "error", "timestamp": 1002.0, "content": {"text": "error Z"}, "importance": 0.3, "verified": False, "context": {}},
            ]
            jsonl_path = self._make_jsonl(tmpdir, "a1", records)

            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)
            stats = migrate_file(jsonl_path, conn)
            conn.close()

            self.assertEqual(stats["total"], 3)
            self.assertEqual(stats["migrated"], 3)
            self.assertEqual(stats["skipped"], 0)
            self.assertEqual(stats["errors"], 0)

            # Verify data in DB
            conn2 = sqlite3.connect(str(db_path))
            rows = conn2.execute("SELECT id, agent_id, memory_type, content FROM memories ORDER BY timestamp").fetchall()
            conn2.close()
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0][0], "m1")
            self.assertEqual(rows[0][1], "a1")
            self.assertEqual(rows[0][2], "learning")
            self.assertIn("learned X", rows[0][3])

    def test_migrate_file_dry_run(self):
        """Dry run returns stats but writes nothing to DB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"memory_id": "m1", "content": {"text": "hello"}},
                {"memory_id": "m2", "content": {"text": "world"}},
            ]
            jsonl_path = self._make_jsonl(tmpdir, "a1", records)

            # conn is None for dry run
            stats = migrate_file(jsonl_path, conn=None, dry_run=True)
            self.assertEqual(stats["total"], 2)
            self.assertEqual(stats["migrated"], 2)
            self.assertEqual(stats["skipped"], 0)
            self.assertEqual(stats["errors"], 0)

    def test_migrate_file_skips_missing_id(self):
        """Memory without memory_id or id field is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"memory_id": "m1", "content": {"text": "good"}},
                {"content": {"text": "no id here"}},  # no memory_id or id
                {"memory_id": "m3", "content": {"text": "also good"}},
            ]
            jsonl_path = self._make_jsonl(tmpdir, "a1", records)

            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)
            stats = migrate_file(jsonl_path, conn)
            conn.close()

            self.assertEqual(stats["total"], 3)
            self.assertEqual(stats["migrated"], 2)
            self.assertEqual(stats["skipped"], 1)
            self.assertEqual(stats["errors"], 0)

            conn2 = sqlite3.connect(str(db_path))
            count = conn2.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            conn2.close()
            self.assertEqual(count, 2)

    def test_no_duplicates(self):
        """Migrating same file twice doesn't create duplicates (INSERT OR IGNORE)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"memory_id": "m1", "content": {"text": "hello"}, "importance": 0.5},
                {"memory_id": "m2", "content": {"text": "world"}, "importance": 0.7},
            ]
            jsonl_path = self._make_jsonl(tmpdir, "a1", records)

            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)

            # Migrate once
            stats1 = migrate_file(jsonl_path, conn)
            self.assertEqual(stats1["migrated"], 2)

            # Migrate again -- should not duplicate
            stats2 = migrate_file(jsonl_path, conn)
            # INSERT OR IGNORE means second run still counts as "migrated" in stats
            # but only 2 rows exist in DB
            conn.close()

            conn2 = sqlite3.connect(str(db_path))
            count = conn2.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            conn2.close()
            self.assertEqual(count, 2)

    def test_migrate_file_uses_id_field_fallback(self):
        """Memory with 'id' field (not 'memory_id') is accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"id": "alt-id-1", "content": {"text": "uses id field"}},
            ]
            jsonl_path = self._make_jsonl(tmpdir, "a1", records)

            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)
            stats = migrate_file(jsonl_path, conn)
            conn.close()

            self.assertEqual(stats["migrated"], 1)
            self.assertEqual(stats["skipped"], 0)

            conn2 = sqlite3.connect(str(db_path))
            row = conn2.execute("SELECT id FROM memories").fetchone()
            conn2.close()
            self.assertEqual(row[0], "alt-id-1")

    def test_migrate_file_defaults(self):
        """Missing optional fields get sensible defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            records = [
                {"memory_id": "m1"},  # minimal record
            ]
            jsonl_path = self._make_jsonl(tmpdir, "agent-x", records)

            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)
            stats = migrate_file(jsonl_path, conn)
            conn.close()

            self.assertEqual(stats["migrated"], 1)

            conn2 = sqlite3.connect(str(db_path))
            row = conn2.execute(
                "SELECT agent_id, memory_type, importance, verified, context FROM memories WHERE id='m1'"
            ).fetchone()
            conn2.close()
            self.assertEqual(row[0], "agent-x")  # falls back to dir name
            self.assertEqual(row[1], "unknown")
            self.assertAlmostEqual(row[2], 0.5)
            self.assertEqual(row[3], 0)
            self.assertEqual(row[4], "{}")


class TestInitSqliteDb(unittest.TestCase):
    """Tests for init_sqlite_db."""

    def test_creates_tables_and_indexes(self):
        """Verify schema has expected tables and indexes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            conn = init_sqlite_db(db_path)

            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            table_names = [t[0] for t in tables]
            self.assertIn("memories", table_names)

            indexes = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
            ).fetchall()
            index_names = [i[0] for i in indexes]
            self.assertIn("idx_agent_timestamp", index_names)
            self.assertIn("idx_agent_type", index_names)
            self.assertIn("idx_timestamp", index_names)

            conn.close()


if __name__ == "__main__":
    unittest.main()
