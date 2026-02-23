"""Idea Seed Detection & Storage System."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IdeaSeedSystem:
    """System for detecting and storing idea seeds."""

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize idea seed system.

        Args:
            storage_path: Storage directory path
        """
        self.storage_path = storage_path or Path("data/idea_seeds")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.seeds: list[dict[str, Any]] = []

    def detect_seed(self, content: str, context: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Detect an idea seed in content.

        Args:
            content: Content to analyze
            context: Additional context

        Returns:
            Idea seed dictionary or None
        """
        # Simple detection - would use NLP/ML in production
        keywords = ["idea", "concept", "proposal", "suggestion", "innovation"]
        content_lower = content.lower()

        for keyword in keywords:
            if keyword in content_lower:
                seed = {
                    "id": f"seed_{len(self.seeds)}",
                    "content": content,
                    "keyword": keyword,
                    "context": context or {},
                    "detected_at": datetime.now(UTC).isoformat(),
                }
                self.seeds.append(seed)
                logger.info(f"Detected idea seed: {seed['id']}")
                return seed

        return None

    def store_seed(self, seed: dict[str, Any]) -> Path:
        """Store an idea seed.

        Args:
            seed: Seed dictionary

        Returns:
            Path to stored seed file
        """
        seed_file = self.storage_path / f"{seed['id']}.json"
        import json

        seed_file.write_text(json.dumps(seed, indent=2).decode().decode())
        logger.info(f"Stored idea seed: {seed_file}")
        return seed_file

    def get_seeds(self, keyword: str | None = None) -> list[dict[str, Any]]:
        """Get stored seeds.

        Args:
            keyword: Optional keyword filter

        Returns:
            List of seeds
        """
        if keyword:
            return [s for s in self.seeds if keyword.lower() in s.get("content", "").lower()]
        return self.seeds
