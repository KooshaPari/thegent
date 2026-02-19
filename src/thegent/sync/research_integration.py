"""Research sprawl integration."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ResearchIntegration:
    """Integrate research documents into work stream."""

    def __init__(self, research_dir: Path | None = None):
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

    def extract_items(self, research_file: Path) -> list[dict[str, Any]]:
        """Extract work items from research document.
        
        Args:
            research_file: Research document path
            
        Returns:
            List of extracted items
        """
        content = research_file.read_text()
        items = []
        
        # Simple extraction - would use more sophisticated parsing
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line or "- [ ]" in line:
                items.append({
                    "source": str(research_file),
                    "line": i + 1,
                    "content": line.strip(),
                })
        
        return items

    def integrate_all(self) -> dict[str, Any]:
        """Integrate all research documents.
        
        Returns:
            Integration results
        """
        research_files = self.scan_research_docs()
        all_items = []
        
        for research_file in research_files:
            items = self.extract_items(research_file)
            all_items.extend(items)
        
        return {
            "research_files": len(research_files),
            "items_extracted": len(all_items),
            "items": all_items,
        }
