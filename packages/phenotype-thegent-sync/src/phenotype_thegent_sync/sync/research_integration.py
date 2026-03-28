"""Research sprawl integration."""

import logging
from pathlib import Path
from typing import Any

from phenotype_thegent_core.utils.batch_ops import batch_read

logger = logging.getLogger(__name__)


class ResearchIntegration:
    """Integrate research documents into work stream."""

    def __init__(self, research_dir: Path | None = None) -> None:
        """Initialize research integration.

        Args:
            research_dir: Research directory path
        """
        self.research_dir = research_dir or Path("docs/research")

    def scan_research_docs(self) -> list[Path]:
        """Scan for research documents.

        Returns:
            List of research document paths
        """
        if not self.research_dir.exists():
            return []

        research_files = list(self.research_dir.rglob("*.md"))
        logger.info(f"Found {len(research_files)} research documents")
        return research_files

    def extract_items(self, content: str, research_file: Path) -> list[dict[str, Any]]:
        """Extract work items from research document content.

        Args:
            content: File content
            research_file: Research document path

        Returns:
            List of extracted items
        """
        items = []

        # Simple extraction - would use more sophisticated parsing
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line or "- [ ]" in line:
                items.append(
                    {
                        "source": str(research_file),
                        "line": i + 1,
                        "content": line.strip(),
                    }
                )

        return items

    def integrate_all(self) -> dict[str, Any]:
        """Integrate all research documents.

        Returns:
            Integration results
        """
        research_files = self.scan_research_docs()

        # Batch read all research files at once
        file_contents = batch_read(research_files)

        all_items = []
        for research_file in research_files:
            content = file_contents.get(research_file, "")
            items = self.extract_items(content, research_file)
            all_items.extend(items)

        return {
            "research_files": len(research_files),
            "items_extracted": len(all_items),
            "items": all_items,
        }
