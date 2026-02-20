"""Research: Phase13 compliance profile mapping."""

from typing import Any

from thegent.phases.compliance_profile import ComplianceProfile


class Phase13ComplianceProfilesResearch:
    """Research framework for compliance profiles."""

    def __init__(self) -> None:
        """Initialize compliance profiles research."""
        self.profiles = {}

    def register_profile(self, name: str, profile: ComplianceProfile) -> None:
        """Register a compliance profile."""
        self.profiles[name] = profile

    def get_all_profiles(self) -> dict[str, Any]:
        """Get all registered profiles."""
        return {name: profile.get_requirements() for name, profile in self.profiles.items()}
