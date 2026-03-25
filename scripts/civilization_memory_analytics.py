"""Memory analytics for civilization agents.

Provides analytics over memory dicts including learning velocity,
error density, keyword trends, agent comparison, and summaries.
"""

import time


class MemoryAnalytics:
    STOP_WORDS = {
        "the",
        "and",
        "for",
        "this",
        "that",
        "with",
        "from",
        "have",
        "been",
        "will",
        "are",
        "was",
        "not",
        "but",
        "can",
        "has",
    }

    def _extract_keywords(self, content: dict) -> list:
        """Flatten all string values in content dict recursively, split by whitespace,
        filter len>3 and not in STOP_WORDS, lowercase."""
        words = []
        self._flatten_strings(content, words)
        return [w for w in words if len(w) > 3 and w not in self.STOP_WORDS]

    def _flatten_strings(self, obj, acc: list):
        """Recursively extract lowercase words from nested dicts/lists/strings."""
        if isinstance(obj, str):
            acc.extend(obj.lower().split())
        elif isinstance(obj, dict):
            for v in obj.values():
                self._flatten_strings(v, acc)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                self._flatten_strings(item, acc)

    def calculate_learning_velocity(self, memories: list, days: int = 30) -> float:
        """Count memories whose memory_type contains 'learning' in the last N days.
        Return count / days."""
        cutoff = time.time() - (days * 86400)
        count = sum(1 for m in memories if "learning" in m.get("memory_type", "") and m.get("timestamp", 0) >= cutoff)
        return count / days

    def calculate_error_density(self, memories: list, days: int = 7) -> float:
        """Count memories whose memory_type contains 'error' in the last N days.
        Return count / days."""
        cutoff = time.time() - (days * 86400)
        count = sum(1 for m in memories if "error" in m.get("memory_type", "") and m.get("timestamp", 0) >= cutoff)
        return count / days

    def get_keyword_trends(self, memories: list, top_n: int = 10) -> list:
        """Extract keywords from all memory content dicts.
        Return [(keyword, count)] sorted by count desc, top N."""
        freq: dict[str, int] = {}
        for m in memories:
            content = m.get("content", {})
            if isinstance(content, dict):
                for kw in self._extract_keywords(content):
                    freq[kw] = freq.get(kw, 0) + 1
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_n]

    def compare_agents(self, memories_a: list, memories_b: list) -> dict:
        """Compare two agents by keyword overlap using Jaccard similarity."""
        keywords_a = set()
        for m in memories_a:
            content = m.get("content", {})
            if isinstance(content, dict):
                keywords_a.update(self._extract_keywords(content))

        keywords_b = set()
        for m in memories_b:
            content = m.get("content", {})
            if isinstance(content, dict):
                keywords_b.update(self._extract_keywords(content))

        intersection = keywords_a & keywords_b
        union = keywords_a | keywords_b
        similarity = len(intersection) / len(union) if union else 0.0

        return {
            "similarity_score": similarity,
            "agent_a_unique_keywords": sorted(keywords_a - keywords_b),
            "agent_b_unique_keywords": sorted(keywords_b - keywords_a),
            "shared_keywords": sorted(intersection),
        }

    def get_agent_summary(self, memories: list) -> dict:
        """Return summary statistics for an agent's memories."""
        total = len(memories)

        memory_types: dict[str, int] = {}
        for m in memories:
            mt = m.get("memory_type", "unknown")
            memory_types[mt] = memory_types.get(mt, 0) + 1

        avg_importance = 0.0
        if total > 0:
            avg_importance = sum(m.get("importance", 0.0) for m in memories) / total

        learning_velocity = self.calculate_learning_velocity(memories)
        error_density = self.calculate_error_density(memories)
        top_keywords = [kw for kw, _ in self.get_keyword_trends(memories, top_n=5)]

        return {
            "total_memories": total,
            "memory_types": memory_types,
            "avg_importance": avg_importance,
            "learning_velocity": learning_velocity,
            "error_density": error_density,
            "top_keywords": top_keywords,
        }
