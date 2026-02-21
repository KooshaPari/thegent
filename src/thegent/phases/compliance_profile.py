"""Compliance profile mapping (EU-AI-ACT, US-SEC, SOX, GDPR)."""

from typing import Any, ClassVar


class ComplianceProfile:
    """Compliance profile mapping."""

    PROFILES: ClassVar[dict[str, Any]] = {
        "eu-ai-act": {
            "name": "EU AI Act",
            "requirements": ["risk_assessment", "transparency", "human_oversight"],
        },
        "us-sec": {
            "name": "US SEC",
            "requirements": ["financial_reporting", "audit_trail", "data_retention"],
        },
        "sox": {
            "name": "Sarbanes-Oxley",
            "requirements": ["internal_controls", "audit_trail", "data_retention"],
        },
        "gdpr": {
            "name": "GDPR",
            "requirements": ["data_protection", "right_to_erasure", "consent_management"],
        },
    }

    def __init__(self, profile_name: str) -> None:
        """Initialize compliance profile.

        Args:
            profile_name: Name of compliance profile
        """
        self.profile_name = profile_name
        self.profile = self.PROFILES.get(profile_name.lower(), {})

    def get_requirements(self) -> list[str]:
        """Get requirements for this profile.

        Returns:
            List of requirement names
        """
        return self.profile.get("requirements", [])

    def check_compliance(self, feature: str) -> bool:
        """Check if a feature is compliant.

        Args:
            feature: Feature name

        Returns:
            True if compliant
        """
        return feature in self.get_requirements()
