"""Research: Phase14 cost-sensing test matrix."""

from typing import Any

from thegent.phases.cost_sensing import CostSensingTestMatrix


class Phase14CostSensingTestsResearch:
    """Research framework for cost sensing tests."""

    def __init__(self) -> None:
        """Initialize cost sensing tests research."""
        self.test_matrix = CostSensingTestMatrix()

    def run_research_tests(self) -> dict[str, Any]:
        """Run research tests."""
        return self.test_matrix.get_test_status()
