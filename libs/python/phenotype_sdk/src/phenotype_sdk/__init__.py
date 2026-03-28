"""Phenotype SDK - Configuration management SDK."""

from phenotype_sdk.domain.entities import ConfigEntry, FeatureFlag
from phenotype_sdk.domain.value_objects import ValueType, ConfigValue
from phenotype_sdk.application.use_cases import ConfigUseCases, FeatureUseCases
from phenotype_sdk.adapters.outbound import HttpConfigClient

__version__ = "0.1.0"

__all__ = [
    # Entities
    "ConfigEntry",
    "FeatureFlag",
    # Value Objects
    "ValueType",
    "ConfigValue",
    # Use Cases
    "ConfigUseCases",
    "FeatureUseCases",
    # Adapters
    "HttpConfigClient",
]
