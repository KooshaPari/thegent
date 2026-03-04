"""Configuration models - delegates to thegent-config package.

DEPRECATED: Import from thegent_config.models instead.
"""

from thegent_config.models import (
    BinarySettings,
    BudgetSettings,
    GovernanceSettings,
    MCPSettings,
    ModelDefaultsSettings,
    OutputSettings,
    OwnerSettings,
    PathSettings,
    RetentionSettings,
    RoutingSettings,
    SecuritySettings,
    SessionSettings,
    TimeoutSettings,
)

__all__ = [
    "PathSettings",
    "ModelDefaultsSettings",
    "TimeoutSettings",
    "SessionSettings",
    "RetentionSettings",
    "BudgetSettings",
    "RoutingSettings",
    "GovernanceSettings",
    "OwnerSettings",
    "OutputSettings",
    "MCPSettings",
    "SecuritySettings",
    "BinarySettings",
]
