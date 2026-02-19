"""Research: Phase14 autonomous learning surface map."""

from typing import Any

from thegent.research.autonomous_learning import AutonomousLearningSurface


class Phase14AutonomousLearningResearch:
    """Research framework for autonomous learning."""

    def __init__(self):
        """Initialize autonomous learning research."""
        self.learning_surface = AutonomousLearningSurface()

    def get_research_map(self) -> dict[str, Any]:
        """Get learning research map."""
        return {
            "learning_points": len(self.learning_surface.learning_points),
            "capabilities": ["learning", "recommendation"],
        }
