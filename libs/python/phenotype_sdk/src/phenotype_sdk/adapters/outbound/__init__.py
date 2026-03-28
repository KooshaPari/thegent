"""Outbound adapters - Implementations of domain ports for external systems."""

from phenotype_sdk.adapters.outbound.http_client import HttpConfigClient
from phenotype_sdk.adapters.outbound.inmemory import InMemoryConfigRepository

__all__ = [
    "HttpConfigClient",
    "InMemoryConfigRepository",
]
