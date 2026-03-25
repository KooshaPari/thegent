"""File-based storage for idea seeds using JSONL format.

Seeds are stored in docs/research/seeds.jsonl (one JSON object per line).
Provides read, write, update, and query operations.
"""

import orjson as json
import logging
from datetime import UTC, datetime
from pathlib import Path

from thegent.memory.seed_detector import Seed, SeedSource

_log = logging.getLogger(__name__)


class SeedStorage:
    """JSONL-based storage for idea seeds."""

    DEFAULT_STORAGE_PATH = Path("docs/research/seeds.jsonl")
    ARCHIVE_PATH = Path("docs/research/seeds_archive.jsonl")

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize seed storage.

        Args:
            storage_path: Path to seeds.jsonl (defaults to docs/research/seeds.jsonl)
        """
        self.storage_path = storage_path or self.DEFAULT_STORAGE_PATH
        self.archive_path = self.storage_path.parent / "seeds_archive.jsonl"
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure storage directory exists."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def store_seed(self, seed: Seed) -> str:
        """Store a seed in the JSONL file.

        Args:
            seed: Seed object to store

        Returns:
            Seed ID
        """
        self._ensure_directory()

        # Check for duplicates by exact text match
        existing = self.find_by_text(seed.text)
        if existing:
            _log.debug(f"Seed already exists: {existing.id}")
            return existing.id

        # Append to JSONL
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(seed.to_dict()).decode() + "\n")

        _log.info(f"Stored seed {seed.id}: {seed.text[:50]}...")
        return seed.id

    def load_seeds(self) -> list[Seed]:
        """Load all seeds from storage.

        Returns:
            List of Seed objects
        """
        if not self.storage_path.exists():
            return []

        seeds = []
        with open(self.storage_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    seed = self._dict_to_seed(data)
                    seeds.append(seed)
                except (json.JSONDecodeError, KeyError) as e:
                    _log.warning(f"Failed to parse seed line: {e}")

        return seeds

    def find_by_id(self, seed_id: str) -> Seed | None:
        """Find a seed by ID.

        Args:
            seed_id: Seed ID to find

        Returns:
            Seed object or None if not found
        """
        seeds = self.load_seeds()
        return next((s for s in seeds if s.id == seed_id), None)

    def find_by_text(self, text: str) -> Seed | None:
        """Find a seed by exact text match.

        Args:
            text: Text to match

        Returns:
            Seed object or None if not found
        """
        seeds = self.load_seeds()
        return next((s for s in seeds if s.text == text[:500]), None)

    def find_by_status(self, status: str) -> list[Seed]:
        """Find seeds by status.

        Args:
            status: Status to filter by (e.g., "new", "developing", "implemented")

        Returns:
            List of matching Seed objects
        """
        seeds = self.load_seeds()
        return [s for s in seeds if s.status == status]

    def find_by_tag(self, tag: str) -> list[Seed]:
        """Find seeds by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of matching Seed objects
        """
        seeds = self.load_seeds()
        return [s for s in seeds if tag in s.tags]

    def find_by_source(self, source: SeedSource) -> list[Seed]:
        """Find seeds by source.

        Args:
            source: SeedSource to filter by

        Returns:
            List of matching Seed objects
        """
        seeds = self.load_seeds()
        return [s for s in seeds if SeedSource(s.source) == source]

    def update_seed(self, seed_id: str, **kwargs) -> bool:
        """Update seed fields (status, tags, etc.).

        Args:
            seed_id: Seed ID to update
            **kwargs: Fields to update (status, tags, context, etc.)

        Returns:
            True if updated, False if not found
        """
        seeds = self.load_seeds()
        updated = False

        for _i, seed in enumerate(seeds):
            if seed.id == seed_id:
                # Update allowed fields
                if "status" in kwargs:
                    seed.status = kwargs["status"]
                if "tags" in kwargs:
                    seed.tags = kwargs["tags"]
                if "context" in kwargs:
                    seed.context = kwargs["context"]
                updated = True
                break

        if updated:
            self._write_seeds(seeds)
            _log.info(f"Updated seed {seed_id}")

        return updated

    def archive_seed(self, seed_id: str) -> bool:
        """Move a seed to archive (mark as archived).

        Args:
            seed_id: Seed ID to archive

        Returns:
            True if archived, False if not found
        """
        return self.update_seed(seed_id, status="archived")

    def delete_seed(self, seed_id: str) -> bool:
        """Delete a seed (actually moves to archive).

        Args:
            seed_id: Seed ID to delete

        Returns:
            True if deleted, False if not found
        """
        seeds = self.load_seeds()
        deleted_seed = None

        for seed in seeds:
            if seed.id == seed_id:
                deleted_seed = seed
                break

        if deleted_seed:
            # Move to archive
            self.archive_seed(seed_id)
            _log.info(f"Archived seed {seed_id}")
            return True

        return False

    def get_stats(self) -> dict:
        """Get storage statistics.

        Returns:
            Dict with stats: total, by_status, by_source, by_confidence
        """
        seeds = self.load_seeds()

        stats = {
            "total": len(seeds),
            "by_status": {},
            "by_source": {},
            "by_confidence": {"high": 0, "medium": 0, "low": 0},
            "avg_confidence": 0,
        }

        for seed in seeds:
            # By status
            stats["by_status"][seed.status] = stats["by_status"].get(seed.status, 0) + 1

            # By source
            source_name = seed.source if isinstance(seed.source, str) else SeedSource(seed.source).value
            stats["by_source"][source_name] = stats["by_source"].get(source_name, 0) + 1

            # By confidence
            if seed.confidence > 0.8:
                stats["by_confidence"]["high"] += 1
            elif seed.confidence >= 0.5:
                stats["by_confidence"]["medium"] += 1
            else:
                stats["by_confidence"]["low"] += 1

        if seeds:
            stats["avg_confidence"] = sum(s.confidence for s in seeds) / len(seeds)

        return stats

    def export_markdown(self, output_path: Path | None = None) -> str:
        """Export seeds as markdown for easy reading.

        Args:
            output_path: Optional path to write markdown file

        Returns:
            Markdown content
        """
        seeds = self.load_seeds()

        md_lines = [
            "# Idea Seeds\n",
            f"Generated: {datetime.now(UTC).isoformat()}\n",
            f"Total seeds: {len(seeds)}\n",
            "---\n",
        ]

        # Group by status
        by_status = {}
        for seed in seeds:
            status = seed.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(seed)

        for status in ["new", "developing", "implemented", "archived"]:
            if status not in by_status:
                continue

            status_seeds = by_status[status]
            md_lines.append(f"\n## {status.title()} ({len(status_seeds)})\n")

            for seed in status_seeds:
                md_lines.append(f"\n### {seed.id}\n")
                md_lines.append(f"**Source:** {seed.source}\n")
                md_lines.append(f"**Confidence:** {seed.confidence:.1%}\n")
                md_lines.append(f"**Timestamp:** {seed.timestamp}\n")
                if seed.tags:
                    md_lines.append(f"**Tags:** {', '.join(seed.tags)}\n")
                md_lines.append(f"\n{seed.text}\n")

        content = "".join(md_lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(content)
            _log.info(f"Exported seeds to {output_path}")

        return content

    def _write_seeds(self, seeds: list[Seed]) -> None:
        """Write seeds back to JSONL file.

        Args:
            seeds: List of Seed objects to write
        """
        self._ensure_directory()
        with open(self.storage_path, "w") as f:
            f.writelines(json.dumps(seed.to_dict()).decode() + "\n" for seed in seeds)

    @staticmethod
    def _dict_to_seed(data: dict) -> Seed:
        """Convert dictionary to Seed object.

        Args:
            data: Dictionary from JSON

        Returns:
            Seed object
        """
        # Get source value from data, defaulting to MANUAL enum
        source_value = data.get("source", SeedSource.MANUAL.value)
        # Ensure we pass the enum value (string), the Seed.__post_init__ will convert to enum
        if isinstance(source_value, SeedSource):
            source_value = source_value.value

        return Seed(
            id=data.get("id", ""),
            text=data.get("text", ""),
            source=SeedSource(source_value),  # Convert string to enum explicitly
            confidence=data.get("confidence", 0.5),
            timestamp=data.get("timestamp", ""),
            tags=data.get("tags", []),
            status=data.get("status", "new"),
            context=data.get("context"),
            detected_by=data.get("detected_by"),
        )
