"""Research: Phase15 enterprise lifecycle surface map."""

from typing import Any

from thegent.phases.enterprise_lifecycle import EnterpriseLifecycleManager


class Phase15EnterpriseLifecycleResearch:
    """Research framework for enterprise lifecycle."""

    def __init__(self):
        """Initialize enterprise lifecycle research."""
        self.lifecycle_manager = EnterpriseLifecycleManager()

    def get_research_map(self) -> dict[str, Any]:
        """Get lifecycle research map."""
        return self.lifecycle_manager.get_lifecycle_map()
