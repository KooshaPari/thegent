"""Tests for Phase 6.3: Memory Relationships.

Tests for link_memories, get_related_memories, and get_relationship_graph
methods on SQLiteMemoryStorage.
"""

import unittest
import time
import tempfile
from pathlib import Path
from dataclasses import dataclass

from civilization_memory_storage import SQLiteMemoryStorage


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


class TestMemoryRelationships(unittest.TestCase):
    """Test memory relationship methods on SQLiteMemoryStorage."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_rel.db"
        self.storage = SQLiteMemoryStorage(self.db_path)
        self.now = time.time()

    def _make_memory(self, memory_id: str, agent_id: str = "agent-1") -> MockAgentMemory:
        return MockAgentMemory(
            memory_id=memory_id,
            agent_id=agent_id,
            memory_type=MockMemoryType("execution"),
            timestamp=self.now,
            content={"task": f"task-{memory_id}"},
        )

    def test_link_memories_basic(self):
        """Link two memories and verify success."""
        self.storage.store(self._make_memory("m1"))
        self.storage.store(self._make_memory("m2"))

        result = self.storage.link_memories("m1", "m2", strength=0.7, relationship_type="related")
        self.assertTrue(result)

    def test_link_memories_invalid_strength(self):
        """Strength outside 0.0-1.0 raises ValueError."""
        with self.assertRaises(ValueError):
            self.storage.link_memories("m1", "m2", strength=1.5)
        with self.assertRaises(ValueError):
            self.storage.link_memories("m1", "m2", strength=-0.1)

    def test_get_related_memories(self):
        """Link A->B, query A gets B back."""
        self.storage.store(self._make_memory("a"))
        self.storage.store(self._make_memory("b"))
        self.storage.link_memories("a", "b", strength=0.8, relationship_type="helps_with")

        related = self.storage.get_related_memories("a")
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]["memory_id"], "b")
        self.assertAlmostEqual(related[0]["strength"], 0.8)
        self.assertEqual(related[0]["relationship_type"], "helps_with")

    def test_get_related_memories_min_strength(self):
        """Filter by min_strength=0.8 excludes weaker links."""
        self.storage.store(self._make_memory("a"))
        self.storage.store(self._make_memory("b"))
        self.storage.store(self._make_memory("c"))

        self.storage.link_memories("a", "b", strength=0.9, relationship_type="related")
        self.storage.link_memories("a", "c", strength=0.3, relationship_type="related")

        related = self.storage.get_related_memories("a", min_strength=0.8)
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]["memory_id"], "b")

    def test_get_related_bidirectional(self):
        """Link A->B, querying B also returns A."""
        self.storage.store(self._make_memory("a"))
        self.storage.store(self._make_memory("b"))
        self.storage.link_memories("a", "b", strength=0.6, relationship_type="similar_to")

        related = self.storage.get_related_memories("b")
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]["memory_id"], "a")
        self.assertEqual(related[0]["relationship_type"], "similar_to")

    def test_relationship_types(self):
        """Test all valid relationship types can be used."""
        valid_types = ["caused_by", "helps_with", "similar_to", "contradicts", "related"]
        for i, rel_type in enumerate(valid_types):
            result = self.storage.link_memories(
                f"x{i}", f"y{i}", strength=0.5, relationship_type=rel_type
            )
            self.assertTrue(result, f"Failed to link with type '{rel_type}'")

    def test_get_relationship_graph(self):
        """Store 2 memories for same agent, link them, get graph."""
        self.storage.store(self._make_memory("g1", agent_id="agent-g"))
        self.storage.store(self._make_memory("g2", agent_id="agent-g"))
        self.storage.link_memories("g1", "g2", strength=0.75, relationship_type="caused_by")

        graph = self.storage.get_relationship_graph("agent-g")

        self.assertIn("g1", graph["nodes"])
        self.assertIn("g2", graph["nodes"])
        self.assertEqual(len(graph["edges"]), 1)

        edge = graph["edges"][0]
        self.assertEqual(edge["from"], "g1")
        self.assertEqual(edge["to"], "g2")
        self.assertAlmostEqual(edge["strength"], 0.75)
        self.assertEqual(edge["type"], "caused_by")

    def test_link_invalid_type(self):
        """Invalid relationship_type raises ValueError."""
        with self.assertRaises(ValueError):
            self.storage.link_memories("m1", "m2", strength=0.5, relationship_type="invalid_type")

    def test_get_relationship_graph_empty(self):
        """Graph for agent with no memories returns empty nodes and edges."""
        graph = self.storage.get_relationship_graph("nonexistent-agent")
        self.assertEqual(graph["nodes"], [])
        self.assertEqual(graph["edges"], [])

    def test_get_related_memories_ordered_by_strength(self):
        """Related memories are returned ordered by strength descending."""
        self.storage.store(self._make_memory("center"))
        self.storage.store(self._make_memory("weak"))
        self.storage.store(self._make_memory("strong"))

        self.storage.link_memories("center", "weak", strength=0.2, relationship_type="related")
        self.storage.link_memories("center", "strong", strength=0.9, relationship_type="related")

        related = self.storage.get_related_memories("center")
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0]["memory_id"], "strong")
        self.assertEqual(related[1]["memory_id"], "weak")


if __name__ == "__main__":
    unittest.main()
