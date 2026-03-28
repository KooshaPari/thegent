"""WP-35003: Geo-Distributed Data Sovereignty Guard.
Ensures that data is stored and processed according to regional sovereignty rules.
"""

import logging

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class SovereigntyRule(BaseModel):
    """Defines where specific data types can be stored/processed."""

    data_category: str
    allowed_regions: set[str]
    restricted_regions: set[str] = set()
    requires_encryption: bool = True


class DataLocationCheck(BaseModel):
    """Result of a sovereignty check."""

    is_compliant: bool
    data_id: str
    category: str
    current_region: str
    violations: list[str] = []


class GeoGuard:
    """Enforces data sovereignty policies across distributed regions."""

    def __init__(self) -> None:
        self.rules: dict[str, SovereigntyRule] = {}
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load baseline sovereignty rules."""
        # Example: EU data must stay in EU regions
        self.rules["PII_EU"] = SovereigntyRule(
            data_category="PII_EU",
            allowed_regions={"eu-west-1", "eu-central-1"},
            restricted_regions={"us-east-1", "us-west-2", "ap-south-1"},
        )
        # Example: Critical Infrastructure data (US)
        self.rules["CRITICAL_INFRA_US"] = SovereigntyRule(
            data_category="CRITICAL_INFRA_US",
            allowed_regions={"us-gov-east-1", "us-gov-west-1"},
            requires_encryption=True,
        )

    def add_rule(self, rule: SovereigntyRule) -> None:
        """Add or update a sovereignty rule."""
        self.rules[rule.data_category] = rule
        _log.info("Sovereignty rule added/updated for category: %s", rule.data_category)

    def validate_location(self, data_id: str, category: str, region: str) -> DataLocationCheck:
        """Verify if data of a given category can reside in the specified region."""
        rule = self.rules.get(category)
        if not rule:
            _log.debug("No sovereignty rule found for category %s, allowing by default.", category)
            return DataLocationCheck(is_compliant=True, data_id=data_id, category=category, current_region=region)

        violations = []
        if rule.allowed_regions and region not in rule.allowed_regions:
            violations.append(f"Region {region} is not in allowed list for category {category}")

        if region in rule.restricted_regions:
            violations.append(f"Region {region} is explicitly restricted for category {category}")

        is_compliant = len(violations) == 0
        if not is_compliant:
            _log.error("SOVEREIGNTY VIOLATION for data %s: %s", data_id, ", ".join(violations))

        return DataLocationCheck(
            is_compliant=is_compliant, data_id=data_id, category=category, current_region=region, violations=violations
        )
