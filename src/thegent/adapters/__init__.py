"""thegent.adapters - Hexagonal Architecture Adapters.

This package provides driving (primary) and driven (secondary) adapters
following the hexagonal/ports-and-adapters pattern.

Architecture:
- adapters.ports: Port interfaces (Protocol definitions)
- adapters.driven: Outbound adapters (HTTP, cache, metrics)
- adapters.driving: Inbound adapters (CLI, API handlers)
"""

from thegent.adapters.ports import (
    # Driven (Outbound) Ports
    HTTPClientPort,
    CachePort,
    MetricsPort,
    AuthPort,
    # Driving (Inbound) Ports
    ProviderExecutionPort,
    RoutingPort,
    GovernancePort,
    # Unified Registry
    AdapterRegistry,
    PluginInterface,
    DriverPlugin,
    RouterPlugin,
    # Registration Decorators
    register_driver,
    register_router,
    register_cache,
    # Runtime
    _runtime_registry,
)

__all__ = [
    # Ports
    "HTTPClientPort",
    "CachePort",
    "MetricsPort",
    "AuthPort",
    "ProviderExecutionPort",
    "RoutingPort",
    "GovernancePort",
    # Registry
    "AdapterRegistry",
    "_runtime_registry",
    # Plugins
    "PluginInterface",
    "DriverPlugin",
    "RouterPlugin",
    # Decorators
    "register_driver",
    "register_router",
    "register_cache",
]
