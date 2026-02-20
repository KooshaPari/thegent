"""Implement learning-record/should-skip subcommands (learning-based)."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LearningSubcommands:
    """Learning-based subcommands."""

    def __init__(self, learning_db_path: Path | None = None) -> None:
        """Initialize learning subcommands.

        Args:
            learning_db_path: Learning database path
        """
        self.learning_db_path = learning_db_path or Path(".learning-db.json")
        self.learning_db: dict[str, Any] = self._load_db()

    def _load_db(self) -> dict[str, Any]:
        """Load learning database.

        Returns:
            Learning database dictionary
        """
        if self.learning_db_path.exists():
            try:
                return json.loads(self.learning_db_path.read_text())
            except Exception:
                return {}
        return {}

    def record(self, pattern: str, skipped: bool, reason: str = "") -> None:
        """Record a learning decision.

        Args:
            pattern: Pattern that was evaluated
            skipped: Whether it was skipped
            reason: Reason for skipping
        """
        if pattern not in self.learning_db:
            self.learning_db[pattern] = {
                "skipped_count": 0,
                "executed_count": 0,
            }

        if skipped:
            self.learning_db[pattern]["skipped_count"] += 1
        else:
            self.learning_db[pattern]["executed_count"] += 1

        self._save_db()
        logger.info(f"Recorded learning: pattern={pattern}, skipped={skipped}")

    def should_skip(self, pattern: str, threshold: float = 0.8) -> bool:
        """Determine if pattern should be skipped.

        Args:
            pattern: Pattern to evaluate
            threshold: Skip threshold (0.0-1.0)

        Returns:
            True if should skip
        """
        if pattern not in self.learning_db:
            return False

        stats = self.learning_db[pattern]
        total = stats["skipped_count"] + stats["executed_count"]
        if total == 0:
            return False

        skip_ratio = stats["skipped_count"] / total
        should_skip = skip_ratio >= threshold

        logger.debug(f"Pattern {pattern}: skip_ratio={skip_ratio:.2f}, should_skip={should_skip}")
        return should_skip

    def _save_db(self) -> None:
        """Save learning database."""
        self.learning_db_path.write_text(json.dumps(self.learning_db, indent=2))
