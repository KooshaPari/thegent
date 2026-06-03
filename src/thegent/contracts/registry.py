"""Stub module."""

from __future__ import annotations


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


__all__ = ["ContractRegistry", "ContractVersion"]
