"""Stub module."""
from __future__ import annotations


#: Public schema version used by contract payloads surfaced through
#: ``get_server_meta_impl``. Defined here so the registries module remains the
#: single import surface for contract-versioning constants; callers should
#: treat this as the canonical contract schema version string.
CONTRACT_SCHEMA_VERSION: str = "contract-schema-v1"


class ContractRegistry:
    """Registry for contracts."""

    def __init__(self) -> None:
        self._contracts: dict = {}

    def register(self, name: str, contract: dict) -> None:
        self._contracts[name] = contract

    def get(self, name: str) -> dict | None:
        return self._contracts.get(name)


from dataclasses import dataclass


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


__all__ = ["CONTRACT_SCHEMA_VERSION", "ContractRegistry", "ContractVersion"]
