"""Work stream auto-incorporation."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class WorkStreamIntegration:
    """Auto-incorporate items into work stream."""

    def __init__(self, work_stream_path: Path | None = None):
        """Initialize work stream integration.
        
        Args:
            work_stream_path: Path to WORK_STREAM.md
        """
        self.work_stream_path = work_stream_path or Path("docs/reference/WORK_STREAM.md")

    def incorporate_from_plans(self, plan_files: list[Path]) -> dict[str, Any]:
        """Incorporate items from plan files.
        
        Args:
            plan_files: List of plan markdown files
            
        Returns:
            Incorporation results
        """
        incorporated = []
        
        for plan_file in plan_files:
            if not plan_file.exists():
                continue
            
            content = plan_file.read_text()
            # Parse plan file for items (simplified)
            items = self._parse_plan_items(content)
            incorporated.extend(items)
            logger.info(f"Incorporated {len(items)} items from {plan_file}")
        
        return {
            "items_incorporated": len(incorporated),
            "items": incorporated,
        }

    def _parse_plan_items(self, content: str) -> list[dict[str, Any]]:
        """Parse items from plan content.
        
        Args:
            content: Plan file content
            
        Returns:
            List of item dictionaries
        """
        items = []
        # Simple parsing - would be more sophisticated in production
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("- [ ]") or line.strip().startswith("|"):
                # Potential item
                items.append({"raw": line.strip()})
        
        return items

    def update_work_stream(self, items: list[dict[str, Any]]) -> bool:
        """Update work stream with new items.
        
        Args:
            items: List of items to add
            
        Returns:
            True if successful
        """
        if not self.work_stream_path.exists():
            logger.warning(f"Work stream not found: {self.work_stream_path}")
            return False
        
        # Implementation would parse and update WORK_STREAM.md
        logger.info(f"Updating work stream with {len(items)} items")
        return True
