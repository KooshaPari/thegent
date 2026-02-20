"""Research: Phase13 cost-sensitivity experiment framework."""

from typing import Any

from thegent.research.cost_sensitivity import CostSensitivityFramework


class Phase13CostSensitivityResearch:
    """Research for cost sensitivity experiments."""

    def __init__(self) -> None:
        """Initialize cost sensitivity research."""
        self.framework = CostSensitivityFramework()

    def run_research_experiment(self) -> dict[str, Any]:
        """Run a research experiment.

        Returns:
            Experiment results
        """
        result = self.framework.run_experiment(100.0, 80.0)
        return result
