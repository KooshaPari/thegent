"""Research: Phase13 cost-sensitivity experiment framework."""

from typing import Any

from phenotype_thegent_planning.research.cost_sensitivity import CostSensitivityFramework


class Phase13CostSensitivityResearch:
    """Research for cost sensitivity experiments."""

    def __init__(self) -> None:
        """Initialize cost sensitivity research."""
        self.framework = CostSensitivityFramework(
            baseline_config={"policy_depth": 1},
            experiment_a_config={"policy_depth": 2},
            experiment_b_config={"policy_depth": 3},
        )

    def run_research_experiment(self) -> dict[str, Any]:
        """Run a research experiment.

        Returns:
            Experiment results
        """
        result = self.framework.run_experiment("baseline", lambda: None)
        return result
