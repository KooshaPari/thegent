import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SyncResult:
    component: str
    status: SyncStatus
    message: str = ""
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class SyncComponent(ABC):
    def __init__(self, name: str, description: str, depends_on: list[str] | None = None) -> None:
        self.name = name
        self.description = description
        self.depends_on = depends_on or []

    @abstractmethod
    def sync(self, dry_run: bool = False, force: bool = False) -> SyncResult:
        pass


class SyncRegistry:
    def __init__(self) -> None:
        self.components: dict[str, SyncComponent] = {}

    def register(self, component: SyncComponent):
        self.components[component.name] = component

    def get_component(self, name: str) -> SyncComponent | None:
        return self.components.get(name)

    def get_all_components(self) -> list[SyncComponent]:
        return list(self.components.values())


class SyncOrchestrator:
    def __init__(self, registry: SyncRegistry) -> None:
        self.registry = registry

    def sync(self, names: list[str] | None = None, dry_run: bool = False, force: bool = False) -> list[SyncResult]:
        components_to_sync = []
        if not names:
            components_to_sync = self.registry.get_all_components()
        else:
            for name in names:
                comp = self.registry.get_component(name)
                if comp:
                    components_to_sync.append(comp)

        # Simple dependency sorting (can be improved)
        sorted_components = self._resolve_dependencies(components_to_sync)

        results = []
        for comp in sorted_components:
            start_time = time.time()
            try:
                result = comp.sync(dry_run=dry_run, force=force)
                result.duration = time.time() - start_time
                results.append(result)
            except Exception as e:
                results.append(
                    SyncResult(
                        component=comp.name, status=SyncStatus.FAILED, message=str(e), duration=time.time() - start_time
                    )
                )

        return results

    def _resolve_dependencies(self, components: list[SyncComponent]) -> list[SyncComponent]:
        # Basic topological sort
        resolved = []
        seen = set()

        def resolve(comp: SyncComponent):
            if comp.name in seen:
                return
            for dep_name in comp.depends_on:
                dep = self.registry.get_component(dep_name)
                if dep:
                    resolve(dep)
            resolved.append(comp)
            seen.add(comp.name)

        for comp in components:
            resolve(comp)

        # Return only requested components (and their dependencies if missing)
        return resolved


# Global registry
registry = SyncRegistry()
