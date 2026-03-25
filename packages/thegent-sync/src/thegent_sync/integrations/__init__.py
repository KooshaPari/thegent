"""TheGent integrations package."""

import warnings

# Base integration components
from .base import (
    IntegrationStatus,
    IntegrationInfo,
    DataclassConfig,
    BaseIntegrationConfig,
    BaseIntegration,
)

__all__ = [
    "BaseIntegration",
    "BaseIntegrationConfig",
    "DataclassConfig",
    "IntegrationInfo",
    "IntegrationStatus",
]
