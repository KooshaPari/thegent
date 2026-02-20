"""Implement fr-ids and fr-index subcommands (FR parsing/indexing)."""

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FRIndexSubcommands:
    """FR (Functional Requirement) parsing and indexing."""

    def __init__(self) -> None:
        """Initialize FR index subcommands."""
        self.index: dict[str, dict[str, Any]] = {}

    def extract_fr_ids(self, content: str) -> list[str]:
        """Extract FR IDs from content.

        Args:
            content: Content to parse

        Returns:
            List of FR IDs
        """
        # Pattern: FR-XXXXX or FR-XXXXX-YY
        pattern = r"FR-\d{5}(?:-\d{2})?"
        fr_ids = re.findall(pattern, content)
        logger.info(f"Extracted {len(fr_ids)} FR IDs")
        return fr_ids

    def index_file(self, file_path: Path) -> dict[str, Any]:
        """Index a file for FR references.

        Args:
            file_path: File to index

        Returns:
            Index entry
        """
        content = file_path.read_text()
        fr_ids = self.extract_fr_ids(content)

        entry = {
            "file": str(file_path),
            "fr_ids": fr_ids,
        }

        self.index[str(file_path)] = entry
        logger.info(f"Indexed {file_path}: {len(fr_ids)} FR references")
        return entry

    def get_fr_references(self, fr_id: str) -> list[str]:
        """Get files referencing an FR.

        Args:
            fr_id: FR identifier

        Returns:
            List of file paths
        """
        files = []
        for file_path, entry in self.index.items():
            if fr_id in entry.get("fr_ids", []):
                files.append(file_path)
        return files
