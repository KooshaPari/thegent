"""thegent-core: Foundation layer for thegent.

This package contains the core domain primitives, ports (hexagonal architecture
interfaces), configuration management, constants, contracts, and models.

Modules migrated from thegent monolith src/thegent/:
- domain/      : Pure domain entities and value objects (no I/O or side effects)
- ports/       : Hexagonal architecture port interfaces (driven/driving)
- config/      : Configuration management (ThegentSettings and sub-configs)
- constants    : Global constants
- contracts/   : Contract registry, CSM schema, canonical event schemas
- models/      : Model catalog, routing, and scraper infrastructure
"""

# Re-exports will be enabled after import paths are rewritten.
# For now, import submodules directly:
#   from thegent_core.config.settings import ThegentSettings
#   from thegent_core.contracts.csm import CanonicalStructuredMessage
