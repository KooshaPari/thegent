"""Tests for Phase 5B: Agent Memory Persistence."""

import json
import time
import unittest
import tempfile
from pathlib import Path

try:
    from civilization_agent_memory import MemoryService, AgentMemory, MemoryType

    MEMORY_SERVICE_AVAILABLE = True
except ImportError:
    try:
        from scripts.civilization_agent_memory import MemoryService, AgentMemory, MemoryType

        MEMORY_SERVICE_AVAILABLE = True
    except ImportError:
        MEMORY_SERVICE_AVAILABLE = False
        MemoryService = None
        AgentMemory = None
        MemoryType = None


@unittest.skipUnless(MEMORY_SERVICE_AVAILABLE, "Memory service required")
class TestMemoryStorage(unittest.TestCase):
    """Tests for memory storage and retrieval."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = MemoryService(Path(self.temp_dir))

    def tearDown(self):
        """Clean up after tests."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_store_execution_memory(self):
        """Test storing execution memories."""
        memory = AgentMemory(
            memory_id="exec-1",
            agent_id="agent-1",
            memory_type=MemoryType.EXECUTION,
            timestamp=time.time(),
            content={"tasks_completed": 5, "duration": 2.5},
            importance=0.8,
        )

        result = self.service.store_memory(memory)
        assert result

        # Verify file created
        memory_file = self.service._get_memory_file("agent-1")
        assert memory_file.exists()

    def test_store_learning_memory(self):
        """Test storing learning memories."""
        memory = AgentMemory(
            memory_id="learn-1",
            agent_id="agent-1",
            memory_type=MemoryType.LEARNING,
            timestamp=time.time(),
            content={"learning": "Caching improves performance 3x"},
            importance=0.9,
        )

        result = self.service.store_memory(memory)
        assert result

    def test_store_decision_memory(self):
        """Test storing decision memories."""
        memory = AgentMemory(
            memory_id="decision-1",
            agent_id="agent-2",
            memory_type=MemoryType.DECISION,
            timestamp=time.time(),
            content={"decision": "Use Redis instead of Memcached", "reason": "Better persistence"},
            importance=0.7,
        )

        result = self.service.store_memory(memory)
        assert result

    def test_store_error_memory(self):
        """Test storing error memories."""
        memory = AgentMemory(
            memory_id="error-1",
            agent_id="agent-2",
            memory_type=MemoryType.ERROR,
            timestamp=time.time(),
            content={"error": "Network timeout", "retries": 3},
            importance=0.5,
        )

        result = self.service.store_memory(memory)
        assert result

    def test_store_multiple_memories(self):
        """Test storing multiple memories for same agent."""
        for i in range(5):
            memory = AgentMemory(
                memory_id=f"mem-{i}",
                agent_id="agent-1",
                memory_type=MemoryType.EXECUTION,
                timestamp=time.time() + i,
                content={"index": i},
            )
            self.service.store_memory(memory)

        # Verify all stored
        memories = self.service._load_agent_memories("agent-1")
        assert len(memories) == 5


@unittest.skipUnless(MEMORY_SERVICE_AVAILABLE, "Memory service required")
class TestMemoryQuerying(unittest.TestCase):
    """Tests for memory querying."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = MemoryService(Path(self.temp_dir))

        # Create sample memories
        self.base_time = time.time()
        self.agent_id = "test-agent"

        # 3 executions
        for i in range(3):
            memory = AgentMemory(
                memory_id=f"exec-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=self.base_time + i * 100,
                content={"index": i},
            )
            self.service.store_memory(memory)

        # 2 learnings
        for i in range(2):
            memory = AgentMemory(
                memory_id=f"learn-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.LEARNING,
                timestamp=self.base_time + (3 + i) * 100,
                content={"learning": f"Pattern {i}"},
            )
            self.service.store_memory(memory)

        # 1 error
        memory = AgentMemory(
            memory_id="error-1",
            agent_id=self.agent_id,
            memory_type=MemoryType.ERROR,
            timestamp=self.base_time + 500,
            content={"error": "Test error"},
        )
        self.service.store_memory(memory)

    def tearDown(self):
        """Clean up after tests."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_query_all_memories(self):
        """Test querying all memories."""
        memories = self.service.query_memory(self.agent_id)
        assert len(memories) == 6

    def test_query_by_type(self):
        """Test querying by memory type."""
        executions = self.service.query_memory(self.agent_id, MemoryType.EXECUTION)
        assert len(executions) == 3

        learnings = self.service.query_memory(self.agent_id, MemoryType.LEARNING)
        assert len(learnings) == 2

        errors = self.service.query_memory(self.agent_id, MemoryType.ERROR)
        assert len(errors) == 1

    def test_query_by_time_range(self):
        """Test querying by time range."""
        start_time = self.base_time + 100
        end_time = self.base_time + 300

        memories = self.service.query_memory(
            self.agent_id,
            start_time=start_time,
            end_time=end_time,
        )

        # Should include memories between timestamps
        assert len(memories) > 0
        for memory in memories:
            assert memory.timestamp >= start_time
            assert memory.timestamp <= end_time

    def test_query_with_limit(self):
        """Test querying with result limit."""
        memories = self.service.query_memory(self.agent_id, limit=3)
        assert len(memories) == 3

    def test_query_nonexistent_agent(self):
        """Test querying for agent with no memories."""
        memories = self.service.query_memory("nonexistent-agent")
        assert len(memories) == 0


@unittest.skipUnless(MEMORY_SERVICE_AVAILABLE, "Memory service required")
class TestMemoryStats(unittest.TestCase):
    """Tests for memory statistics and aggregation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = MemoryService(Path(self.temp_dir))
        self.agent_id = "stats-agent"

        # Create diverse memories
        base_time = time.time()

        # 10 successful executions
        for i in range(10):
            memory = AgentMemory(
                memory_id=f"exec-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
                content={"status": "success"},
                importance=0.7,
            )
            self.service.store_memory(memory)

        # 2 errors
        for i in range(2):
            memory = AgentMemory(
                memory_id=f"error-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.ERROR,
                timestamp=base_time + 100 + i,
                content={"error": f"Error {i}"},
                importance=0.3,
            )
            self.service.store_memory(memory)

        # 3 learnings
        for i in range(3):
            memory = AgentMemory(
                memory_id=f"learn-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.LEARNING,
                timestamp=base_time + 200 + i,
                content={"learning": f"Learning {i}"},
                importance=0.9,
            )
            self.service.store_memory(memory)

    def tearDown(self):
        """Clean up after tests."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_get_agent_stats(self):
        """Test retrieving agent statistics."""
        stats = self.service.get_agent_stats(self.agent_id)

        assert stats["total_memories"] == 15
        assert stats["error_count"] == 2
        assert stats["learning_count"] == 3
        assert stats["memory_types"]["execution"] == 10
        assert stats["memory_types"]["error"] == 2
        assert stats["memory_types"]["learning"] == 3

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = self.service.get_agent_stats(self.agent_id)

        # 10 successful executions, 2 errors out of 12 total
        # Success rate: 10/12 = 0.83
        expected_rate = 10 / 12
        self.assertAlmostEqual(stats["success_rate"], round(expected_rate, 2), places=1)  # noqa: PT009

    def test_average_importance(self):
        """Test average importance calculation."""
        stats = self.service.get_agent_stats(self.agent_id)

        # Average of 10*0.7 + 2*0.3 + 3*0.9 = 7 + 0.6 + 2.7 = 10.3 / 15 = 0.69
        expected_avg = (10 * 0.7 + 2 * 0.3 + 3 * 0.9) / 15
        self.assertAlmostEqual(stats["average_importance"], round(expected_avg, 2), places=1)  # noqa: PT009

    def test_timestamps_in_stats(self):
        """Test that first and last timestamps are recorded."""
        stats = self.service.get_agent_stats(self.agent_id)

        assert stats["first_memory"] is not None
        assert stats["last_memory"] is not None
        assert stats["first_memory"] < stats["last_memory"]


@unittest.skipUnless(MEMORY_SERVICE_AVAILABLE, "Memory service required")
class TestMemoryOperations(unittest.TestCase):
    """Tests for memory operations like purging and importance filtering."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = MemoryService(Path(self.temp_dir))
        self.agent_id = "ops-agent"

    def tearDown(self):
        """Clean up after tests."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_get_memories_by_importance(self):
        """Test retrieving memories above importance threshold."""
        base_time = time.time()

        # Create memories with varying importance
        for i in range(10):
            memory = AgentMemory(
                memory_id=f"mem-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
                importance=i * 0.1,  # 0.0 to 0.9
            )
            self.service.store_memory(memory)

        # Get only high importance
        important = self.service.get_memories_by_importance(
            self.agent_id,
            min_importance=0.7,
            limit=5,
        )

        assert len(important) == 3  # 0.7, 0.8, 0.9
        for memory in important:
            assert memory.importance >= 0.7

    def test_purge_old_memories(self):
        """Test purging memories older than TTL."""
        base_time = time.time()

        # Create old memories (1 hour ago)
        for i in range(5):
            memory = AgentMemory(
                memory_id=f"old-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time - 3600 + i,
            )
            self.service.store_memory(memory)

        # Create recent memories
        for i in range(5):
            memory = AgentMemory(
                memory_id=f"new-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
            )
            self.service.store_memory(memory)

        # Purge memories older than 30 minutes
        ttl_seconds = 30 * 60
        deleted = self.service.purge_old_memories(self.agent_id, ttl_seconds)

        assert deleted == 5  # Old memories deleted

        # Verify only recent remain
        remaining = self.service.query_memory(self.agent_id)
        assert len(remaining) == 5

    def test_get_learning_summary(self):
        """Test getting learning summary."""
        base_time = time.time()

        # Create some learnings
        for i in range(3):
            memory = AgentMemory(
                memory_id=f"learn-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.LEARNING,
                timestamp=base_time + i,
                content={"learning": f"Important pattern {i}"},
                importance=0.9 - i * 0.1,
            )
            self.service.store_memory(memory)

        summary = self.service.get_learning_summary(self.agent_id, limit=2)

        assert len(summary) == 2
        for item in summary:
            assert "learning" in item
            assert "importance" in item
            assert "timestamp" in item

    def test_clear_agent_memory(self):
        """Test clearing all memories for an agent."""
        base_time = time.time()

        # Create several memories
        for i in range(10):
            memory = AgentMemory(
                memory_id=f"mem-{i}",
                agent_id=self.agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
            )
            self.service.store_memory(memory)

        # Verify they exist
        memories = self.service.query_memory(self.agent_id)
        assert len(memories) == 10

        # Clear all
        result = self.service.clear_agent_memory(self.agent_id)
        assert result

        # Verify cleared
        memories = self.service.query_memory(self.agent_id)
        assert len(memories) == 0


@unittest.skipUnless(MEMORY_SERVICE_AVAILABLE, "Memory service required")
class TestMemoryPersistence(unittest.TestCase):
    """Tests for memory persistence across service restarts."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_memories_persist_across_restarts(self):
        """Test that memories are persisted and reloaded."""
        agent_id = "persist-agent"
        base_time = time.time()

        # Create service and store memories
        service1 = MemoryService(Path(self.temp_dir))
        for i in range(5):
            memory = AgentMemory(
                memory_id=f"mem-{i}",
                agent_id=agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
                content={"index": i},
            )
            service1.store_memory(memory)

        # Create new service instance
        service2 = MemoryService(Path(self.temp_dir))

        # Verify memories loaded
        memories = service2.query_memory(agent_id)
        assert len(memories) == 5

    def test_stats_persist_across_restarts(self):
        """Test that stats files persist."""
        agent_id = "stats-agent"
        base_time = time.time()

        # Create service and store memories
        service1 = MemoryService(Path(self.temp_dir))
        for i in range(10):
            memory = AgentMemory(
                memory_id=f"exec-{i}",
                agent_id=agent_id,
                memory_type=MemoryType.EXECUTION,
                timestamp=base_time + i,
            )
            service1.store_memory(memory)

        stats1 = service1.get_agent_stats(agent_id)

        # Create new service instance
        service2 = MemoryService(Path(self.temp_dir))
        stats2 = service2.get_agent_stats(agent_id)

        # Stats should match
        assert stats1["total_memories"] == stats2["total_memories"]
        assert stats1["memory_types"] == stats2["memory_types"]


if __name__ == "__main__":
    unittest.main()
