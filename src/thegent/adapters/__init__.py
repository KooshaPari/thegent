"""thegent.adapters - Hexagonal Architecture Adapters.

This package provides driving (primary) and driven (secondary) adapters
following the hexagonal/ports-and-adapters pattern.

Architecture:
- adapters.ports: Port interfaces (Protocol definitions)
- adapters.driven: Outbound adapters (HTTP, cache, metrics)
- adapters.driving: Inbound adapters (CLI, API handlers)
- adapters.plugin_host_adapter: WASM plugin host integration
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

# Plugin Host Adapter - WASM/Extism integration
from thegent.adapters.plugin_host_adapter import (
    PluginHostAdapter,
    PluginHostConfig,
    LoadedPlugin,
    get_plugin_host,
)

# Execution I/O adapters — decomposition seams for the run/bg orchestrators.
# See ``thegent.adapters.execution_io`` for the AUDIT-N+5 hand-off context.
from thegent.adapters.execution_io import (
    LeaseToken,
    ProcessEnvironmentBuilder,
    ProcessSpawner,
    ResourceLockManager,
    ShadowWorkspaceManager,
    SpawnResult,
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
    # Plugin Host
    "PluginHostAdapter",
    "PluginHostConfig",
    "LoadedPlugin",
    "get_plugin_host",
    # Execution I/O seams (AUDIT-N+5)
    "LeaseToken",
    "ProcessEnvironmentBuilder",
    "ProcessSpawner",
    "ResourceLockManager",
    "ShadowWorkspaceManager",
    "SpawnResult",
    # Decorators
    "register_driver",
    "register_router",
    "register_cache",
]
