"""Tests for Phase 6a: Memory Storage Backends.

Comprehensive tests covering SQLite and JSONL storage implementations:
- SQLiteMemoryStorage (new indexed backend)
- JSONLMemoryStorage (Phase 5B fallback)
- Full-text search functionality
- Performance comparisons
"""

import unittest
import time
import tempfile
from pathlib import Path
from dataclasses import dataclass

from civilization_memory_storage import (
    MemoryStorage,
    SQLiteMemoryStorage,
    JSONLMemoryStorage,
)


# Mock memory classes for testing
@dataclass
class MockMemoryType:
    value: str


@dataclass
class MockAgentMemory:
    memory_id: str
    agent_id: str
    memory_type: MockMemoryType
    timestamp: float
    content: dict
    context: dict = None
    importance: float = 0.5
    verified: bool = False

    def __post_init__(self):
        if self.context is None:
            self.context = {}


# ========== Test Classes ==========


class TestSQLiteMemoryStorage(unittest.TestCase):
    """Test SQLite backend implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.storage = SQLiteMemoryStorage(self.db_path)
        self.now = time.time()

    def test_store_memory(self):
        """Test storing a memory in SQLite."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=self.now,
            content={"task": "completed"},
        )

        result = self.storage.store(memory)
        assert result

    def test_query_memory(self):
        """Test querying memories from SQLite."""
        # Store multiple memories
        for i in range(5):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 100),
                content={"task": f"task-{i}"},
            )
            self.storage.store(memory)

        # Query all
        results = self.storage.query("agent-1")
        assert len(results) == 5

        # Query with limit
        results = self.storage.query("agent-1", limit=2)
        assert len(results) == 2

    def test_search_memories(self):
        """Test full-text search in SQLite."""
        # Store memories with different content
        for i in range(3):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("learning"),
                timestamp=self.now - (i * 100),
                content={"learning": f"database optimization technique {i}"},
            )
            self.storage.store(memory)

        # Search for keyword
        results = self.storage.search("agent-1", "database")
        assert len(results) > 0

    def test_get_stats(self):
        """Test statistics calculation from SQLite."""
        # Store mixed memories
        for i in range(5):
            mem_type = "execution" if i < 3 else "error" if i == 3 else "learning"
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType(mem_type),
                timestamp=self.now - (i * 100),
                content={"info": f"item {i}"},
                importance=0.5 + (i * 0.1),
            )
            self.storage.store(memory)

        stats = self.storage.get_stats("agent-1")

        assert stats["total_memories"] == 5
        assert stats["error_count"] == 1
        assert stats["learning_count"] == 1
        assert stats["average_importance"] > 0.5

    def test_purge_old_memories(self):
        """Test deleting old memories from SQLite."""
        now = time.time()

        # Store recent memory
        recent = MockAgentMemory(
            memory_id="recent",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=now - 100,
            content={"type": "recent"},
        )
        self.storage.store(recent)

        # Store old memory
        old = MockAgentMemory(
            memory_id="old",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=now - (86400 * 31),  # 31 days old
            content={"type": "old"},
        )
        self.storage.store(old)

        # Purge memories older than 30 days
        deleted = self.storage.purge_old("agent-1", ttl_seconds=86400 * 30)

        assert deleted == 1

        # Verify old memory is gone
        results = self.storage.query("agent-1")
        assert len(results) == 1
        assert results[0].memory_id == "recent"

    def test_clear_agent_memories(self):
        """Test clearing all memories for an agent in SQLite."""
        # Store memories
        for i in range(3):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 100),
                content={"task": f"task-{i}"},
            )
            self.storage.store(memory)

        # Clear
        result = self.storage.clear("agent-1")
        assert result

        # Verify empty
        results = self.storage.query("agent-1")
        assert len(results) == 0


class TestJSONLMemoryStorage(unittest.TestCase):
    """Test JSONL backend (Phase 5B fallback)."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        self.storage = JSONLMemoryStorage(self.base_path)
        self.now = time.time()

    def test_store_memory_jsonl(self):
        """Test storing a memory in JSONL."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=self.now,
            content={"task": "completed"},
        )

        result = self.storage.store(memory)
        assert result

        # Verify file created
        memory_file = self.base_path / "agent-1" / "memory.jsonl"
        assert memory_file.exists()

    def test_query_memory_jsonl(self):
        """Test querying memories from JSONL."""
        # Store memories
        for i in range(3):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 100),
                content={"task": f"task-{i}"},
            )
            self.storage.store(memory)

        # Query
        results = self.storage.query("agent-1")
        assert len(results) == 3

    def test_search_memories_jsonl(self):
        """Test content search in JSONL."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("learning"),
            timestamp=self.now,
            content={"learning": "caching improves performance"},
        )
        self.storage.store(memory)

        # Search
        results = self.storage.search("agent-1", "caching")
        assert len(results) == 1

    def test_get_stats_jsonl(self):
        """Test statistics from JSONL."""
        for i in range(3):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 100),
                content={"task": f"task-{i}"},
            )
            self.storage.store(memory)

        stats = self.storage.get_stats("agent-1")

        assert stats["total_memories"] == 3
        assert stats["memory_types"]["execution"] == 3

    def test_clear_jsonl(self):
        """Test clearing memories in JSONL."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=self.now,
            content={"task": "completed"},
        )
        self.storage.store(memory)

        # Clear
        result = self.storage.clear("agent-1")
        assert result

        # Verify file deleted
        memory_file = self.base_path / "agent-1" / "memory.jsonl"
        assert not memory_file.exists()


class TestStorageAbstraction(unittest.TestCase):
    """Test that both backends implement the same interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sqlite_storage = SQLiteMemoryStorage(Path(self.temp_dir) / "sqlite.db")
        self.jsonl_storage = JSONLMemoryStorage(Path(self.temp_dir) / "jsonl")
        self.now = time.time()

    def test_both_backends_store(self):
        """Test both backends can store memories."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("execution"),
            timestamp=self.now,
            content={"task": "completed"},
        )

        sqlite_result = self.sqlite_storage.store(memory)
        jsonl_result = self.jsonl_storage.store(memory)

        assert sqlite_result
        assert jsonl_result

    def test_both_backends_query(self):
        """Test both backends can query memories."""
        # Store in both
        for i in range(3):
            memory = MockAgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 100),
                content={"task": f"task-{i}"},
            )
            self.sqlite_storage.store(memory)
            self.jsonl_storage.store(memory)

        # Query both
        sqlite_results = self.sqlite_storage.query("agent-1")
        jsonl_results = self.jsonl_storage.query("agent-1")

        assert len(sqlite_results) == 3
        assert len(jsonl_results) == 3

    def test_both_backends_search(self):
        """Test both backends can search."""
        memory = MockAgentMemory(
            memory_id="mem-1",
            agent_id="agent-1",
            memory_type=MockMemoryType("learning"),
            timestamp=self.now,
            content={"learning": "optimization technique"},
        )
        self.sqlite_storage.store(memory)
        self.jsonl_storage.store(memory)

        # Search both
        sqlite_results = self.sqlite_storage.search("agent-1", "optimization")
        jsonl_results = self.jsonl_storage.search("agent-1", "optimization")

        assert len(sqlite_results) > 0
        assert len(jsonl_results) > 0


class TestPerformance(unittest.TestCase):
    """Test performance characteristics of both backends."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sqlite_storage = SQLiteMemoryStorage(Path(self.temp_dir) / "perf_sqlite.db")
        self.jsonl_storage = JSONLMemoryStorage(Path(self.temp_dir) / "perf_jsonl")
        self.now = time.time()

    def test_sqlite_vs_jsonl_store_performance(self):
        """Compare store performance between backends."""
        # Store 100 memories in each

        # SQLite
        sqlite_start = time.time()
        for i in range(100):
            memory = MockAgentMemory(
                memory_id=f"sqlite-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 10),
                content={"data": f"item {i}"},
            )
            self.sqlite_storage.store(memory)
        sqlite_time = time.time() - sqlite_start

        # JSONL
        jsonl_start = time.time()
        for i in range(100):
            memory = MockAgentMemory(
                memory_id=f"jsonl-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 10),
                content={"data": f"item {i}"},
            )
            self.jsonl_storage.store(memory)
        jsonl_time = time.time() - jsonl_start

        print(f"SQLite store (100 items): {sqlite_time:.3f}s")
        print(f"JSONL store (100 items): {jsonl_time:.3f}s")

        # Both should be relatively fast
        # SQLite has higher write overhead: schema init grows with more tables (relationships added in 6.3).
        # Threshold is generous (5.0s) to accommodate concurrent agent load and schema growth.
        # The important metric is query speed — see test_sqlite_vs_jsonl_query_performance.
        assert sqlite_time < 5.0
        assert jsonl_time < 1.0

    def test_sqlite_vs_jsonl_query_performance(self):
        """Compare query performance between backends."""
        # Store 100 memories in each
        for i in range(100):
            memory = MockAgentMemory(
                memory_id=f"perf-{i}",
                agent_id="agent-1",
                memory_type=MockMemoryType("execution"),
                timestamp=self.now - (i * 10),
                content={"data": f"item {i}"},
            )
            self.sqlite_storage.store(memory)
            self.jsonl_storage.store(memory)

        # SQLite query
        sqlite_start = time.time()
        for _ in range(10):
            self.sqlite_storage.query("agent-1", limit=10)
        sqlite_time = time.time() - sqlite_start

        # JSONL query
        jsonl_start = time.time()
        for _ in range(10):
            self.jsonl_storage.query("agent-1", limit=10)
        jsonl_time = time.time() - jsonl_start

        print(f"SQLite query (10x, 100 items): {sqlite_time:.3f}s")
        print(f"JSONL query (10x, 100 items): {jsonl_time:.3f}s")

        # SQLite should be noticeably faster for queries
        # (but JSONL acceptable for small datasets)
        assert sqlite_time < 0.5
        assert jsonl_time < 1.0


if __name__ == "__main__":
    unittest.main()
