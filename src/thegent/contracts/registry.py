"""Contract registry — single source of truth for contract schemas.

This module is the canonical surface for contract-versioning constants
(``CONTRACT_SCHEMA_VERSION``), the ``ContractRegistry`` instance, and
its lookup helpers (``get_registry``, ``is_compatible``,
``list_versions``). All governance commands and the L9 ROB-010
critical-lane downgrade guard import from this module.

Backwards-compatible: ``CONTRACT_SCHEMA_VERSION``, ``ContractRegistry``,
and ``ContractVersion`` are preserved from the original stub.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


#: Public schema version used by contract payloads surfaced through
#: ``get_server_meta_impl``. Defined here so the registries module remains the
#: single import surface for contract-versioning constants; callers should
#: treat this as the canonical contract schema version string.
CONTRACT_SCHEMA_VERSION: str = "contract-schema-v1"


@dataclass
class ContractVersionInfo:
    """Metadata for a registered contract version.

    Governance commands (``contracts_registry_cmd``) and the L9 ROB-010
    downgrade guard consume this shape — the field set is frozen and
    contract-pinned by ``tests/unit/contracts/test_registry_contract.py``.
    """

    contract_id: str
    version: str
    description: str = ""
    deprecated: bool = False
    #: ISO-8601 date string after which this version is no longer
    #: accepted by the migrator. ``None`` means no expiry.
    migration_window_end: str | None = None


@dataclass
class ContractRegistry:
    """Registry for contracts and their compatibility metadata.

    The registry is intentionally minimal: it tracks registered
    ``ContractVersionInfo`` entries and answers two queries:

    * ``list_versions()`` — surface every registered entry (drives the
      ``thegent contracts registry`` governance command).
    * ``is_compatible(requested, current)`` — return ``True`` only when
      the requested version is the canonical current version. ROB-010
      uses this to block any non-current contract version in a
      critical lane.
    """

    _contracts: dict[str, ContractVersionInfo] = field(default_factory=dict)

    def register(self, name: str, contract: dict[str, Any]) -> None:
        """Back-compat shim: accept legacy ``register(name, dict)`` calls.

        Stores a ``ContractVersionInfo`` derived from the dict payload.
        """
        info = ContractVersionInfo(
            contract_id=name,
            version=str(contract.get("version", "")),
            description=str(contract.get("description", "")),
            deprecated=bool(contract.get("deprecated", False)),
            migration_window_end=contract.get("migration_window_end"),
        )
        self._contracts[name] = info

    def get(self, name: str) -> ContractVersionInfo | None:
        return self._contracts.get(name)

    def list_versions(self) -> list[ContractVersionInfo]:
        """Return every registered ``ContractVersionInfo``, sorted by id.

        Stable ordering so governance table output is deterministic.
        """
        return sorted(self._contracts.values(), key=lambda v: (v.contract_id, v.version))

    def is_compatible(self, requested: str, current: str) -> bool:
        """Return ``True`` only when ``requested == current``.

        ROB-010 contract-version downgrade prevention: in a critical
        lane the only acceptable requested version is the canonical
        current schema version. Forward or backward drift is rejected.
        Unknown versions are treated as incompatible.
        """
        return bool(requested) and requested == current


#: Canonical single instance. Populated at import time with the
#: ``csm`` contract at ``CONTRACT_SCHEMA_VERSION`` so list_versions()
#: is never empty.
CONTRACT_REGISTRY: ContractRegistry = ContractRegistry()
CONTRACT_REGISTRY.register(
    "csm",
    {
        "version": CONTRACT_SCHEMA_VERSION,
        "description": "Canonical Structured Message contract (csm).",
        "deprecated": False,
        "migration_window_end": None,
    },
)


def get_registry() -> ContractRegistry:
    """Return the canonical ``CONTRACT_REGISTRY`` singleton.

    Used by governance commands (``contracts_registry_cmd``) and the
    L9 ROB-010 critical-lane downgrade guard in
    ``_phase_bg_evaluate_contract``.
    """
    return CONTRACT_REGISTRY


@dataclass
class ContractVersion:
    """Version information for a contract."""

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)


__all__ = [
    "CONTRACT_REGISTRY",
    "CONTRACT_SCHEMA_VERSION",
    "ContractRegistry",
    "ContractVersion",
    "ContractVersionInfo",
    "get_registry",
]
