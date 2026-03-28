"""Research: Phase15 enterprise compliance test matrix."""

from typing import Any

from phenotype_thegent_planning.phases.enterprise_compliance_tests import EnterpriseComplianceTestMatrix


class Phase15EnterpriseComplianceTestsResearch:
    """Research framework for enterprise compliance tests."""

    def __init__(self) -> None:
        """Initialize enterprise compliance tests research."""
        self.test_matrix = EnterpriseComplianceTestMatrix()

    def run_research_tests(self) -> dict[str, Any]:
        """Run research tests."""
        return self.test_matrix.get_compliance_status()
