"""Research: Phase15 enterprise compliance test matrix."""

from typing import Any

from thegent.phases.enterprise_compliance_tests import EnterpriseComplianceTestMatrix


class Phase15EnterpriseComplianceTestsResearch:
    """Research framework for enterprise compliance tests."""

    def __init__(self):
        """Initialize enterprise compliance tests research."""
        self.test_matrix = EnterpriseComplianceTestMatrix()

    def run_research_tests(self) -> dict[str, Any]:
        """Run research tests."""
        return self.test_matrix.get_compliance_status()
