"""Contract registry: authoritative contract versioning and compatibility.

Provides single source of truth for structured output contracts across
task-tool (18-tag), Zen rich protocol, and thegent provider outputs.
"""

from dataclasses import dataclass

# Contract schema version for thegent orchestration contracts
CONTRACT_SCHEMA_VERSION = "csm-v1"


@dataclass(frozen=True)
class ContractVersion:
    """A registered contract version with compatibility metadata."""

    contract_id: str
    version: str
    description: str
    compatible_with: tuple[str, ...] = ()
    deprecated: bool = False
    migration_window_end: str | None = None  # ISO date; after this, deprecated versions are rejected


# Compatibility matrix: to_version -> from_versions that can be normalized to it
_COMPATIBILITY_MATRIX: dict[str, tuple[str, ...]] = {
    "csm-v1": ("csm-v1", "task-tool-18", "zen-rich-v1"),
    "task-tool-18": ("task-tool-18",),
    "zen-rich-v1": ("zen-rich-v1",),
}


class ContractRegistry:
    """Authoritative registry of contract definitions and compatibility."""

    def __init__(self) -> None:
        self._versions: dict[str, ContractVersion] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            ContractVersion(
                contract_id="csm",
                version="csm-v1",
                description="Canonical Structured Message: unified schema for task-tool 18-tag and Zen rich protocol",
                compatible_with=("task-tool-18", "zen-rich-v1"),
            )
        )
        self.register(
            ContractVersion(
                contract_id="task-tool",
                version="task-tool-18",
                description="Task-tool canonical 18-tag XML contract (snake_case)",
                compatible_with=("csm-v1",),
            )
        )
        self.register(
            ContractVersion(
                contract_id="zen",
                version="zen-rich-v1",
                description="Zen rich protocol: status, progress, actions, files, quality",
                compatible_with=("csm-v1",),
            )
        )

    def register(self, cv: ContractVersion) -> None:
        """Register a contract version."""
        key = f"{cv.contract_id}@{cv.version}"
        self._versions[key] = cv

    def get(self, contract_id: str, version: str | None = None) -> ContractVersion | None:
        """Get contract version. If version is None, returns latest for contract_id."""
        if version:
            return self._versions.get(f"{contract_id}@{version}")
        # Find latest non-deprecated for contract_id
        candidates = [v for k, v in self._versions.items() if k.startswith(f"{contract_id}@") and not v.deprecated]
        return max(candidates, key=lambda v: v.version) if candidates else None

    def is_compatible(self, from_version: str, to_version: str) -> bool:
        """Check if from_version can be normalized to to_version."""
        compat = _COMPATIBILITY_MATRIX.get(to_version, ())
        return from_version in compat or to_version == from_version

    def list_versions(self) -> list[ContractVersion]:
        """List all registered contract versions."""
        return list(self._versions.values())


_registry: ContractRegistry | None = None


def get_registry() -> ContractRegistry:
    """Get the global contract registry (singleton)."""
    global _registry
    if _registry is None:
        _registry = ContractRegistry()
    return _registry
