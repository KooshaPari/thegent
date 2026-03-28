"""Unified sync/update command implementation."""

import logging
from pathlib import Path
from typing import Any

from phenotype_thegent_sync.sync.plan_consolidation import PlanConsolidation
from phenotype_thegent_sync.sync.research_integration import ResearchIntegration
from phenotype_thegent_sync.sync.work_stream_integration import WorkStreamIntegration

logger = logging.getLogger(__name__)


class UnifiedSyncCommand:
    """Unified sync/update command."""

    def __init__(self) -> None:
        """Initialize unified sync command."""
        self.work_stream_integration = WorkStreamIntegration()
        self.research_integration = ResearchIntegration()
        self.plan_consolidation = PlanConsolidation()

    def sync_all(self) -> dict[str, Any]:
        """Sync all components.

        Returns:
            Sync results dictionary
        """
        results = {
            "work_stream": self.sync_work_stream(),
            "research": self.sync_research(),
            "plans": self.sync_plans(),
        }
        return results

    def sync_work_stream(self) -> dict[str, Any]:
        """Sync work stream.

        Returns:
            Sync result
        """
        logger.info("Syncing work stream...")
        plan_files = list(Path("docs/plans").glob("*.md"))
        result = self.work_stream_integration.incorporate_from_plans(plan_files)
        return {"status": "success", "items_added": result.get("items_incorporated", 0)}

    def sync_research(self) -> dict[str, Any]:
        """Sync research sprawl.

        Returns:
            Sync result
        """
        logger.info("Syncing research sprawl...")
        result = self.research_integration.integrate_all()
        return {"status": "success", "docs_processed": result.get("research_files", 0)}

    def sync_plans(self) -> dict[str, Any]:
        """Sync and consolidate plans.

        Returns:
            Sync result
        """
        logger.info("Consolidating plans...")
        result = self.plan_consolidation.consolidate()
        return {"status": "success", "plans_consolidated": result.get("plans_consolidated", 0)}
