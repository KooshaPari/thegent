import unittest
from civilization_memory_sharing import MemorySharingService
import pytest


class TestMemorySharingService(unittest.TestCase):
    def setUp(self):
        self.service = MemorySharingService(db_path=":memory:")

    def test_store_and_get_learnings(self):
        """Store a learning memory and retrieve it."""
        self.service.store_memory("mem1", "agent_a", "learning", {"skill": "navigation"}, importance=0.8)
        results = self.service.get_agent_learnings("agent_a", min_importance=0.5)
        assert len(results) == 1
        assert results[0]["memory_id"] == "mem1"
        assert results[0]["content"]["skill"] == "navigation"
        self.assertAlmostEqual(results[0]["importance"], 0.8)

    def test_get_learnings_min_importance(self):
        """Low importance memories are filtered out."""
        self.service.store_memory("mem1", "agent_a", "learning", {"skill": "low"}, importance=0.2)
        self.service.store_memory("mem2", "agent_a", "learning", {"skill": "high"}, importance=0.9)
        results = self.service.get_agent_learnings("agent_a", min_importance=0.5)
        assert len(results) == 1
        assert results[0]["memory_id"] == "mem2"

    def test_get_learnings_type_filter(self):
        """Only 'learning' type memories are returned."""
        self.service.store_memory("mem1", "agent_a", "learning", {"data": "yes"}, importance=0.8)
        self.service.store_memory("mem2", "agent_a", "observation", {"data": "no"}, importance=0.8)
        results = self.service.get_agent_learnings("agent_a", min_importance=0.5)
        assert len(results) == 1
        assert results[0]["memory_id"] == "mem1"

    def test_record_learning_transfer_basic(self):
        """Record a transfer and verify it appears in history."""
        self.service.store_memory("mem1", "agent_a", "learning", {"skill": "x"}, importance=0.8)
        success = self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=0.7)
        assert success
        history = self.service.get_transfer_history("agent_a", as_source=True)
        assert len(history) == 1
        assert history[0]["source_agent_id"] == "agent_a"
        assert history[0]["target_agent_id"] == "agent_b"

    def test_record_transfer_invalid_effectiveness(self):
        """effectiveness=1.5 raises ValueError."""
        with pytest.raises(ValueError):
            self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=1.5)

    def test_get_transfer_history_as_source(self):
        """Get transfers FROM an agent."""
        self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=0.6)
        self.service.record_learning_transfer("mem2", "agent_a", "agent_c", effectiveness=0.8)
        history = self.service.get_transfer_history("agent_a", as_source=True)
        assert len(history) == 2
        target_agents = {h["target_agent_id"] for h in history}
        assert target_agents == {"agent_b", "agent_c"}

    def test_get_transfer_history_as_target(self):
        """Get transfers TO an agent."""
        self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=0.6)
        self.service.record_learning_transfer("mem2", "agent_c", "agent_b", effectiveness=0.9)
        history = self.service.get_transfer_history("agent_b", as_source=False)
        assert len(history) == 2
        source_agents = {h["source_agent_id"] for h in history}
        assert source_agents == {"agent_a", "agent_c"}

    def test_get_most_shared_learnings(self):
        """Verify ordering by transfer_count."""
        self.service.store_memory("mem1", "agent_a", "learning", {"skill": "popular"}, importance=0.8)
        self.service.store_memory("mem2", "agent_a", "learning", {"skill": "less_popular"}, importance=0.7)
        # mem1 transferred 3 times, mem2 transferred 1 time
        self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=0.7)
        self.service.record_learning_transfer("mem1", "agent_a", "agent_c", effectiveness=0.8)
        self.service.record_learning_transfer("mem1", "agent_a", "agent_d", effectiveness=0.6)
        self.service.record_learning_transfer("mem2", "agent_a", "agent_b", effectiveness=0.5)
        results = self.service.get_most_shared_learnings(limit=5)
        assert len(results) >= 2
        assert results[0]["memory_id"] == "mem1"
        assert results[0]["transfer_count"] == 3
        assert results[1]["memory_id"] == "mem2"
        assert results[1]["transfer_count"] == 1

    def test_calculate_transfer_effectiveness(self):
        """Average effectiveness computed correctly."""
        self.service.record_learning_transfer("mem1", "agent_a", "agent_b", effectiveness=0.6)
        self.service.record_learning_transfer("mem2", "agent_c", "agent_b", effectiveness=0.8)
        avg = self.service.calculate_transfer_effectiveness("agent_b")
        self.assertAlmostEqual(avg, 0.7, places=5)

    def test_calculate_effectiveness_no_transfers(self):
        """Returns 0.0 when no transfers exist."""
        avg = self.service.calculate_transfer_effectiveness("nonexistent_agent")
        assert avg == 0.0


if __name__ == "__main__":
    unittest.main()
