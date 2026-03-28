"""Phenotype Python SDK.

A comprehensive Python SDK following:
- Hexagonal Architecture (Ports & Adapters)
- Clean Architecture principles
- SOLID principles
- xDD methodologies (TDD, BDD, DDD)

Usage:
    from phenotype_sdk import Client, Config, Logging

    config = Config.from_env()
    client = Client(config)
    result = await client.query("hello", {"name": "World"})
"""

from phenotype_sdk.client import AsyncClient, SyncClient
from phenotype_sdk.config import Config
from phenotype_sdk.logging import setup_logging
from phenotype_sdk.errors import (
    SDKError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    APIError,
)
from phenotype_sdk.auth import Auth, AuthConfig

__version__ = "0.1.0"

__all__ = [
    # Client
    "AsyncClient",
    "SyncClient",
    # Config
    "Config",
    # Logging
    "setup_logging",
    # Errors
    "SDKError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    # Auth
    "Auth",
    "AuthConfig",
]
