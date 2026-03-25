"""Tests for civilization memory analytics."""

import time
import unittest

from civilization_memory_analytics import MemoryAnalytics


def make_memory(memory_type, timestamp_offset_days=0, content=None, importance=0.5):
    return {
        "memory_id": f"m-{memory_type}-{timestamp_offset_days}",
        "agent_id": "test-agent",
        "memory_type": memory_type,
        "timestamp": time.time() - (timestamp_offset_days * 86400),
        "content": content or {"data": f"test {memory_type} content"},
        "importance": importance,
    }


class TestMemoryAnalytics(unittest.TestCase):
    def setUp(self):
        self.analytics = MemoryAnalytics()

    def test_learning_velocity_basic(self):
        memories = [
            make_memory("learning", timestamp_offset_days=1),
            make_memory("learning", timestamp_offset_days=3),
            make_memory("learning", timestamp_offset_days=5),
            make_memory("error", timestamp_offset_days=2),
        ]
        velocity = self.analytics.calculate_learning_velocity(memories, days=30)
        self.assertAlmostEqual(velocity, 3 / 30)

    def test_learning_velocity_old_filtered(self):
        memories = [
            make_memory("learning", timestamp_offset_days=1),
            make_memory("learning", timestamp_offset_days=35),
            make_memory("learning", timestamp_offset_days=40),
        ]
        velocity = self.analytics.calculate_learning_velocity(memories, days=30)
        self.assertAlmostEqual(velocity, 1 / 30)

    def test_error_density_basic(self):
        memories = [
            make_memory("error", timestamp_offset_days=1),
            make_memory("error", timestamp_offset_days=3),
            make_memory("learning", timestamp_offset_days=2),
        ]
        density = self.analytics.calculate_error_density(memories, days=7)
        self.assertAlmostEqual(density, 2 / 7)

    def test_keyword_trends_basic(self):
        memories = [
            make_memory("learning", content={"data": "python automation testing"}),
            make_memory("learning", content={"data": "python deployment automation"}),
            make_memory("error", content={"data": "python error handling"}),
        ]
        trends = self.analytics.get_keyword_trends(memories, top_n=5)
        keywords = [kw for kw, _ in trends]
        assert "python" in keywords
        assert "automation" in keywords

    def test_keyword_trends_stop_words_filtered(self):
        memories = [
            make_memory("learning", content={"data": "the quick brown fox and this that"}),
        ]
        trends = self.analytics.get_keyword_trends(memories, top_n=10)
        keywords = [kw for kw, _ in trends]
        assert "the" not in keywords
        assert "and" not in keywords
        assert "this" not in keywords
        assert "that" not in keywords
        assert "quick" in keywords
        assert "brown" in keywords

    def test_compare_agents_similar(self):
        memories_a = [
            make_memory("learning", content={"data": "python automation testing deploy"}),
        ]
        memories_b = [
            make_memory("learning", content={"data": "python automation testing deploy"}),
        ]
        result = self.analytics.compare_agents(memories_a, memories_b)
        self.assertAlmostEqual(result["similarity_score"], 1.0)
        assert result["agent_a_unique_keywords"] == []
        assert result["agent_b_unique_keywords"] == []

    def test_compare_agents_different(self):
        memories_a = [
            make_memory("learning", content={"data": "python automation"}),
        ]
        memories_b = [
            make_memory("learning", content={"data": "javascript React"}),
        ]
        result = self.analytics.compare_agents(memories_a, memories_b)
        assert result["similarity_score"] < 0.5
        assert "python" in result["agent_a_unique_keywords"]
        assert "react" in result["agent_b_unique_keywords"]

    def test_get_agent_summary(self):
        memories = [
            make_memory("learning", timestamp_offset_days=1, importance=0.8),
            make_memory("error", timestamp_offset_days=2, importance=0.6),
            make_memory("execution", timestamp_offset_days=3, importance=0.4),
        ]
        summary = self.analytics.get_agent_summary(memories)
        assert summary["total_memories"] == 3
        assert summary["memory_types"]["learning"] == 1
        assert summary["memory_types"]["error"] == 1
        assert summary["memory_types"]["execution"] == 1
        self.assertAlmostEqual(summary["avg_importance"], 0.6)
        assert isinstance(summary["learning_velocity"], float)
        assert isinstance(summary["error_density"], float)
        assert isinstance(summary["top_keywords"], list)

    def test_empty_memories(self):
        summary = self.analytics.get_agent_summary([])
        assert summary["total_memories"] == 0
        assert summary["memory_types"] == {}
        self.assertAlmostEqual(summary["avg_importance"], 0.0)
        self.assertAlmostEqual(summary["learning_velocity"], 0.0)
        self.assertAlmostEqual(summary["error_density"], 0.0)
        assert summary["top_keywords"] == []

        velocity = self.analytics.calculate_learning_velocity([])
        self.assertAlmostEqual(velocity, 0.0)

        density = self.analytics.calculate_error_density([])
        self.assertAlmostEqual(density, 0.0)

        trends = self.analytics.get_keyword_trends([])
        assert trends == []

        result = self.analytics.compare_agents([], [])
        self.assertAlmostEqual(result["similarity_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
